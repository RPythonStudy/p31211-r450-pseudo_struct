import csv
import shutil
from pathlib import Path
from ff3 import FF3Cipher
from charset_normalizer import from_path

# 🔐 암호화 설정
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

# 디렉토리 생성
OUT_DIR.mkdir(parents=True, exist_ok=True)
FAIL_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# 📄 로그 초기화
log_rows = [("filename", "status", "encoding", "error")]

# 📖 인코딩 감지 및 표준화 함수
def read_and_normalize(path: Path) -> tuple[str, str]:
    result = from_path(path).best()
    try:
        content = str(result)  # 디코딩 시도
        return content, result.encoding
    except Exception as e:
        raise UnicodeDecodeError("charset-normalizer", b"", 0, 1, f"decode failed: {e}")


# 🔁 메인 처리 루프
for file in RAW_DIR.glob("*.txt"):
    original_id = file.stem
    if not all(c in ALPHABET for c in original_id):
        log_rows.append((file.name, "skipped", "", "invalid characters in filename"))
        continue

    try:
        pseudonym = cipher.encrypt(original_id)
        content, encoding_used = read_and_normalize(file)
        (OUT_DIR / f"{pseudonym}.txt").write_text(content, encoding="utf-8")
        log_rows.append((file.name, "success", encoding_used, ""))
        print(f"✔ {file.name} → {pseudonym}.txt (encoding: {encoding_used})")
    except Exception as e:
        shutil.copy(file, FAIL_DIR / file.name)
        log_rows.append((file.name, "failed", "", str(e)))
        print(f"❌ Failed: {file.name} ({e}) → moved to failed_encoding/")

# 📝 CSV 로그 저장
with open(LOG_FILE, mode="w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(log_rows)
