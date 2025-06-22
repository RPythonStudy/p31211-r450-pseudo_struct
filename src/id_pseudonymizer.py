import re
from ff3 import FF3Cipher

# 암호화 설정 (필요시 외부에서 주입받도록 수정 가능)
KEY = '0123456789abcdef0123456789abcdef'
TWEAK = 'abcdef12345678'
ALPHABET = '0123456789'
cipher = FF3Cipher.withCustomAlphabet(KEY, TWEAK, ALPHABET)

def ff3_pad(msg: str, minlen: int = 6) -> str:
    """등록번호를 FF3 암호화에 맞게 패딩"""
    return msg.rjust(minlen, '0')

def pseudonymize_patient_id(regno: str) -> str:
    """등록번호(환자ID) 가명화"""
    return cipher.encrypt(ff3_pad(regno))

def depseudonymize_patient_id(pseudo_id: str) -> str:
    """등록번호(환자ID) 복호화"""
    return cipher.decrypt(pseudo_id).lstrip('0')

def pseudonymize_patient_id_in_text(text: str, original_id: str, pseudo_id: str) -> str:
    """텍스트 내 등록번호 치환"""
    return re.sub(
        r"(등록번호\s*:\s*)" + re.escape(original_id),
        lambda m: f"{m.group(1)}{pseudo_id}",
        text
    )

def depseudonymize_patient_id_in_text(text: str, pseudo_id: str, original_id: str) -> str:
    """텍스트 내 등록번호 복호화"""
    return re.sub(
        r"(등록번호\s*:\s*)" + re.escape(pseudo_id),
        lambda m: f"{m.group(1)}{original_id}",
        text
    )

def verify_patient_id_pseudonymization(text: str, id_pattern: str) -> bool:
    """등록번호가 가명화되어 있는지 검증 (id_pattern: 가명화된 ID의 정규표현식)"""
    return not bool(re.search(r"등록번호\s*:\s*\d{6,}", text)) and bool(re.search(id_pattern, text))