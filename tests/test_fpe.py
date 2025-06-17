from FPE import FF3

def test_fpe_encryption_decryption():
    key = b'0123456789abcdef'
    tweak = b'abcdef123456'
    ff3 = FF3(key, tweak)

    original = '12345678'
    ciphertext = ff3.encrypt(original)
    decrypted = ff3.decrypt(ciphertext)

    assert decrypted == original  # 복호화된 값이 원본과 같은지 테스트
