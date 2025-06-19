import re
import csv
import shutil
from pathlib import Path
from ff3 import FF3Cipher
from charset_normalizer import from_path

# 🔐 FF3Cipher 설정
KEY = '0123456789abcdef0123456789abcdef'
TWEAK = 'abcdef12345678'
ALPHABET = '0123456789'
cipher = FF3Cipher.withCustomAlphabet(KEY, TWEAK, ALPHABET)

# 📁 디렉토리 설정
ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data/raw"
OUT_DIR = ROOT / "data/pseudonymized"
FAIL_DIR = ROOT / "data/failed_encoding"
LOG_FILE = ROOT / "logs/encoding_report.csv"

OUT_DIR.mkdir(parents=True, exist_ok=True)
FAIL_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# 📄 로그 초기화
log_rows = [("filename", "status", "encoding", "error")]

# 📖 인코딩 감지 및 디코딩
def read_and_normalize(path: Path) -> tuple[str, str]:
    result = from_path(path).best()
    try:
        content = str(result)
        return content, result.encoding
    except Exception as e:
        raise UnicodeDecodeError("charset-normalizer", b"", 0, 1, f"decode failed: {e}")

# 🔁 파일 처리
for file in RAW_DIR.glob("*.txt"):
    original_id = file.stem
    if not all(c in ALPHABET for c in original_id):
        log_rows.append((file.name, "skipped", "", "invalid filename"))
        continue

    try:
        pseudonym = cipher.encrypt(original_id)
        content, encoding = read_and_normalize(file)

        # ✅ '등록번호:' 본문 내 치환 (안전한 함수 방식)
        pattern = rf"(등록번호\s*:\s*){original_id}"
        def replace_registered_id(match):
            return f"{match.group(1)}{pseudonym}"
        content = re.sub(pattern, replace_registered_id, content)

        # 저장
        out_file = OUT_DIR / f"{pseudonym}.txt"
        out_file.write_text(content, encoding="utf-8")

        log_rows.append((file.name, "success", encoding, ""))
        print(f"✔ {file.name} → {pseudonym}.txt (내부 등록번호 치환 완료)")
    except Exception as e:
        shutil.copy(file, FAIL_DIR / file.name)
        log_rows.append((file.name, "failed", "", str(e)))
        print(f"❌ Failed: {file.name} ({e}) → moved to failed_encoding/")

# 📝 로그 파일 저장
with open(LOG_FILE, mode="w", encoding="utf-8", newline="") as f:
    csv.writer(f).writerows(log_rows)
