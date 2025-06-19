import re
import shutil
from pathlib import Path
from ff3 import FF3Cipher
from charset_normalizer import from_path

# 복호화를 위한 키와 TWEAK (암호화와 동일해야 함)
KEY = '0123456789abcdef0123456789abcdef'
TWEAK = 'abcdef12345678'
ALPHABET = '0123456789'
cipher = FF3Cipher.withCustomAlphabet(KEY, TWEAK, ALPHABET)

# 경로 설정
ROOT = Path(__file__).resolve().parents[2]
PSEUDO_DIR = ROOT / "data/pseudonymized"
DECRYPTED_DIR = ROOT / "data/decrypted"
DECRYPTED_DIR.mkdir(parents=True, exist_ok=True)

# 유틸: 알파벳만으로 구성된 이름 복호화
def decrypt_alpha(pseudo: str) -> str:
    val = 0
    for c in pseudo:
        val = val * 26 + (ord(c) - 65)
    dec = cipher.decrypt(str(val).rjust(8, '0'))
    return ''.join(chr(int(dec[i:i+2])) for i in range(0, len(dec), 2))

# 유틸: 구조를 유지하는 ID 복호화
def decrypt_structured_id(pseudo: str) -> str:
    match = re.match(r'^([A-Z]+)(\d{2})-(\d+)$', pseudo)
    if not match:
        return pseudo
    p1, p2, p3 = match.groups()
    combined = p1 + p2 + p3
    num = ''.join(str(ord(c)) for c in combined)[:12]
    dec = cipher.decrypt(num)
    return f"{p1}{p2}-{p3} (복호화불완전, 역매핑 필요)"

# 파일 이름 복호화
for file in PSEUDO_DIR.glob("*.txt"):
    pseudonym = file.stem
    try:
        original_id = cipher.decrypt(pseudonym)
        result = from_path(file).best()
        content = str(result)

        # 등록번호 복호화
        content = re.sub(r"(등록번호\s*:\s*)" + pseudonym,
                         lambda m: f"{m.group(1)}{original_id}", content)

        # 출력자ID 복호화
        content = re.sub(r"(출력자ID\s*:\s*)(\d{8})",
                         lambda m: f"{m.group(1)}{cipher.decrypt(m.group(2))}", content)

        # PGM_ID, 병리번호, 육안촬영ID 복호화
        content = re.sub(r"(PGM_ID\s*:\s*)([A-Z0-9\-]+)",
                         lambda m: f"{m.group(1)}{decrypt_structured_id(m.group(2))}", content)

        content = re.sub(r"(병리번호\s*:\s*)([A-Z0-9\-]+)",
                         lambda m: f"{m.group(1)}{decrypt_structured_id(m.group(2))}", content)

        content = re.sub(r"([A-Z]{2,3}\d{2}-\d{4})(?=\s+육안사진촬영)",
                         lambda m: decrypt_structured_id(m.group(1)), content)

        # 날짜 복호화: YYYY-MM-DD 형태만
        content = re.sub(r"((접\s?수\s?일|출력일|결과일)\s*:\s*)(\d{4}-\d{2}-\d{2})",
                         lambda m: f"{m.group(1)}{cipher.decrypt(m.group(3).replace('-', ''))[:4]}-{cipher.decrypt(m.group(3).replace('-', ''))[4:6]}-{cipher.decrypt(m.group(3).replace('-', ''))[6:8]}", content)

        # 복호화된 파일로 저장
        out_file = DECRYPTED_DIR / f"{original_id}.txt"
        out_file.write_text(content, encoding="utf-8")
        print(f"✔ 복호화 완료: {file.name} → {original_id}.txt")

    except Exception as e:
        print(f"❌ 복호화 실패: {file.name} → {e}")
