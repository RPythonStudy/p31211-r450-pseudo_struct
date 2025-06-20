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

def pseudonym_to_alpha(pseudonym: str) -> str:
    num = int(pseudonym)
    alpha = ""
    while num:
        num, r = divmod(num, 26)
        alpha = chr(65 + r) + alpha
    return alpha.rjust(len(pseudonym), "A")

def pseudonym_to_alphanum(pseudonym: str) -> str:
    num = int(pseudonym)
    chars = []
    for _ in range(8):
        num, r = divmod(num, 36)
        chars.append(str(r) if r < 10 else chr(65 + r - 10))
    return ''.join(reversed(chars)).rjust(8, 'A')

def pseudonymize_path(path: Path) -> tuple[str, str]:
    result = from_path(path).best()
    return str(result), result.encoding

name_fields = [
    r"(환\s?자\s?명\s*:\s*)(\S+)",
    r"(의뢰의사\s*:\s*)(\S+)",
    r"(담당의사\s*:\s*)(\S+)",
    r"(결과\s?입력\s*:\s*)(\S+)",
    r"(병리전문의\s*:\s*)(\S+)"
]

def pseudonymize_names(text: str) -> str:
    for pattern in name_fields:
        def repl(match):
            label, name = match.groups()
            if not name.isalpha():
                return match.group(0)
            name_id = ''.join(str(ord(c)) for c in name)[:12]
            pseudonum = cipher.encrypt(name_id)
            pseudoname = pseudonym_to_alpha(pseudonum)
            return f"{label}{pseudoname}"
        text = re.sub(pattern, repl, text)
    return text

def pseudonymize_structured_id(original: str) -> str:
    match = re.match(r'^([A-Z]{1,3})(\d{2})-(\d+)$', original)
    if not match:
        return original
    prefix, year, serial = match.groups()
    plain = f"{prefix}{year}{serial}"
    numeric_input = ''.join(str(ord(c)) for c in plain)[:12]
    pseudonum = cipher.encrypt(numeric_input)
    pseudo_prefix = pseudonym_to_alpha(pseudonum[:len(prefix)])
    pseudo_year = pseudonum[len(prefix):len(prefix)+2]
    pseudo_serial = pseudonum[len(prefix)+2:]
    return f"{pseudo_prefix}{pseudo_year}-{pseudo_serial}"

def pseudonymize_misc(text: str) -> str:
    text = re.sub(r"(출력자ID\s*:\s*)(\d{1,8})",
                  lambda m: f"{m.group(1)}{cipher.encrypt(m.group(2).rjust(8, '0'))}", text)

    text = re.sub(r"(PGM_ID\s*:\s*)([A-Z0-9\-]+)",
                  lambda m: f"{m.group(1)}{pseudonymize_structured_id(m.group(2))}", text)

    text = re.sub(r"(병리번호\s*:\s*)([A-Z0-9\-]+)",
                  lambda m: f"{m.group(1)}{pseudonymize_structured_id(m.group(2))}", text)

    text = re.sub(r"(병동/병실\s*:\s*)(\S+\s*/\s*\S+)", r"\1OO / OO", text)

    text = re.sub(r"((접\s?수\s?일|출력일|결과일)\s*:\s*)(\d{4}-\d{2}-\d{2})",
                  lambda m: f"{m.group(1)}{cipher.encrypt(m.group(3).replace('-', ''))[:4]}-{cipher.encrypt(m.group(3).replace('-', ''))[4:6]}-{cipher.encrypt(m.group(3).replace('-', ''))[6:8]}", text)

    return text

def pseudonymize_specimen_id(text: str) -> str:
    def repl(match):
        prefix, year, serial = match.group(1), match.group(2), match.group(3)
        original = f"{prefix}{year}{serial}"
        numeric_input = ''.join(str(ord(c)) for c in original)[:12]
        pseudonum = cipher.encrypt(numeric_input)
        head_chars = pseudonym_to_alpha(pseudonum[:len(prefix)])
        year_digits = pseudonum[len(prefix):len(prefix)+2]
        serial_digits = pseudonum[len(prefix)+2:]
        return f"{head_chars}{year_digits}-{serial_digits}"

    return re.sub(r"([A-Z]{2,3})(\d{2})-(\d{4})(?=\s+육안사진촬영)", repl, text)

def remove_footer_lines(text: str) -> str:
    lines = text.splitlines()
    cleaned_lines = []
    skip_keywords = [
        "전자서명법에 의하여 전자서명된 문서입니다",
        "한국원자력의학원",
        "본 문서는 중요 자산이므로 무단으로 수정 및 복사를 할 수 없습니다"
    ]
    for line in lines:
        if not any(kw in line for kw in skip_keywords):
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

for file in RAW_DIR.glob("*.txt"):
    original_id = file.stem
    if not all(c in ALPHABET for c in original_id):
        log_rows.append((file.name, "skipped", "", "invalid filename"))
        continue

    try:
        pseudonym = cipher.encrypt(original_id)
        content, encoding = pseudonymize_path(file)

        content = re.sub(r"(등록번호\s*:\s*)"+original_id,
                         lambda m: f"{m.group(1)}{pseudonym}", content)

        content = pseudonymize_names(content)
        content = pseudonymize_misc(content)
        content = pseudonymize_specimen_id(content)
        content = remove_footer_lines(content)

        out_file = OUT_DIR / f"{pseudonym}.txt"
        out_file.write_text(content, encoding="utf-8")

        log_rows.append((file.name, "success", encoding, ""))
        print(f"✔ {file.name} → {pseudonym}.txt (전체 가명화 완료)")
    except Exception as e:
        shutil.copy(file, FAIL_DIR / file.name)
        log_rows.append((file.name, "failed", "", str(e)))
        print(f"❌ Failed: {file.name} ({e}) → moved to failed_encoding/")

with open(LOG_FILE, mode="w", encoding="utf-8", newline="") as f:
    csv.writer(f).writerows(log_rows)
