import re
import csv
import shutil
from pathlib import Path
from ff3 import FF3Cipher
from charset_normalizer import from_path

# 암호화 설정
KEY = '0123456789abcdef0123456789abcdef'
TWEAK = 'abcdef12345678'
ALPHABET = '0123456789'
cipher = FF3Cipher.withCustomAlphabet(KEY, TWEAK, ALPHABET)

# 경로 설정
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data/raw"
OUT_DIR = ROOT / "data/pseudonymized"
FAIL_DIR = ROOT / "data/failed_encoding"
LOG_FILE = ROOT / "logs/encoding_report.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)
FAIL_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

log_rows = [("filename", "status", "encoding", "error")]

# FF3 숫자 가명 → 대문자 알파벳 변환
def pseudonym_to_alpha(pseudonym: str) -> str:
    num = int(pseudonym)
    alpha = ""
    while num:
        num, r = divmod(num, 26)
        alpha = chr(65 + r) + alpha
    return alpha.rjust(len(pseudonym), "A")

# 텍스트 인코딩 감지 및 정규화
def read_and_normalize(path: Path) -> tuple[str, str]:
    result = from_path(path).best()
    try:
        content = str(result)
        return content, result.encoding
    except Exception as e:
        raise UnicodeDecodeError("charset-normalizer", b"", 0, 1, f"decode failed: {e}")

# 이름 필드 목록 (정규표현식 패턴 그룹 사용)
name_fields = [
    r"(환\s?자\s?명\s*:\s*)(\S+)",
    r"(의뢰의사\s*:\s*)(\S+)",
    r"(담당의사\s*:\s*)(\S+)",
    r"(결과\s?입력\s*:\s*)(\S+)",
    r"(병리전문의\s*:\s*)(\S+)"
]

# 본문 이름 치환 함수
def pseudonymize_names(text: str) -> str:
    for pattern in name_fields:
        def repl(match):
            label, name = match.groups()
            if not name.isalpha():  # 이름이 아닌 경우(예: 숫자)는 무시
                return match.group(0)
            name_id = ''.join(str(ord(c)) for c in name)[:12]  # 이름 → 숫자 키 생성
            pseudonum = cipher.encrypt(name_id)
            pseudoname = pseudonym_to_alpha(pseudonum)
            return f"{label}{pseudoname}"
        text = re.sub(pattern, repl, text)
    return text

# 메인 처리 루프
for file in RAW_DIR.glob("*.txt"):
    original_id = file.stem
    if not all(c in ALPHABET for c in original_id):
        log_rows.append((file.name, "skipped", "", "invalid filename"))
        continue

    try:
        pseudonym = cipher.encrypt(original_id)
        content, encoding = read_and_normalize(file)

        # 등록번호 치환
        pattern = rf"(등록번호\s*:\s*){original_id}"
        def replace_registered_id(match):
            return f"{match.group(1)}{pseudonym}"
        content = re.sub(pattern, replace_registered_id, content)

        # 이름 필드 치환
        content = pseudonymize_names(content)

        # 결과 저장
        out_file = OUT_DIR / f"{pseudonym}.txt"
        out_file.write_text(content, encoding="utf-8")

        log_rows.append((file.name, "success", encoding, ""))
        print(f"✔ {file.name} → {pseudonym}.txt (등록번호 + 이름 가명화 완료)")
    except Exception as e:
        shutil.copy(file, FAIL_DIR / file.name)
        log_rows.append((file.name, "failed", "", str(e)))
        print(f"❌ Failed: {file.name} ({e}) → moved to failed_encoding/")

# 로그 기록
with open(LOG_FILE, mode="w", encoding="utf-8", newline="") as f:
    csv.writer(f).writerows(log_rows)
