# tests/test_fpe.py

from ff3 import FF3Cipher

key = '0123456789abcdef0123456789abcdef'  # 128-bit = 32 hex
tweak = 'abcdef12345678'                  # ✅ 56 bits = 14 hex (7 bytes)

cipher = FF3Cipher.withCustomAlphabet(key, tweak, '0123456789')

plaintext = '12345678'
ciphertext = cipher.encrypt(plaintext)
decrypted = cipher.decrypt(ciphertext)

print(f"암호화: {ciphertext}")
print(f"복호화: {decrypted}")

