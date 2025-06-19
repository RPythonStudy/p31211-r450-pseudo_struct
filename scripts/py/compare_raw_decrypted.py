import difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data/raw"
DECRYPTED_DIR = ROOT / "data/decrypted"
REPORT_FILE = ROOT / "logs/diff_report.txt"

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(REPORT_FILE, "w", encoding="utf-8") as report:
    for raw_file in RAW_DIR.glob("*.txt"):
        decrypted_file = DECRYPTED_DIR / raw_file.name

        if not decrypted_file.exists():
            report.write(f"❌ {raw_file.name}: 복호화된 파일이 없습니다.\n")
            continue

        raw_text = raw_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        dec_text = decrypted_file.read_text(encoding="utf-8", errors="ignore").splitlines()

        if raw_text == dec_text:
            report.write(f"✔ {raw_file.name}: 내용 일치\n")
        else:
            report.write(f"❌ {raw_file.name}: 내용 불일치\n")
            diff = difflib.unified_diff(
                raw_text, dec_text,
                fromfile=f"raw/{raw_file.name}",
                tofile=f"decrypted/{raw_file.name}",
                lineterm=""
            )
            report.write("\n".join(diff) + "\n\n")

print(f"🔍 비교 완료: 결과는 {REPORT_FILE}에 저장됨")
