import os
import hvac
import hashlib
from pathlib import Path

VAULT_ADDR = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")  # 또는 AppRole 인증 사용 가능
TRANSIT_PATH = "transit/encrypt/patient-id"

RAW_DIR = Path("../data/raw")
OUT_DIR = Path("../data/pseudonymized")
OUT_DIR.mkdir(exist_ok=True)

client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

def pseudonymize(patient_id: str) -> str:
    """Vault로 암호화하고, pseudo_ 접두어 + 20자리 고정 문자열 반환"""
    encrypted = client.secrets.transit.encrypt_data(
        name="patient-id",
        plaintext=patient_id.encode("utf-8").hex()
    )["data"]["ciphertext"]
    hashval = hashlib.sha256(encrypted.encode()).hexdigest()
    return "pseudo_" + hashval[:20 - len("pseudo_")]

def process_file(filepath: Path):
    output_path = OUT_DIR / filepath.name
    with filepath.open("r", encoding="utf-8") as fin, output_path.open("w", encoding="utf-8") as fout:
        for line in fin:
            raw_id = line.strip()
            if raw_id:
                pseudo_id = pseudonymize(raw_id)
                fout.write(pseudo_id + "\n")

def main():
    for file in RAW_DIR.glob("*.txt"):
        print(f"Processing: {file.name}")
        process_file(file)
    print("✅ Pseudonymization complete.")

if __name__ == "__main__":
    main()
