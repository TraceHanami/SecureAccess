import unittest
import os
import tempfile
from cryptography.fernet import InvalidToken
from secure_access.crypto import (
    hash_password,
    verify_password,
    derive_key,
    encrypt_bytes,
    decrypt_bytes,
    is_encrypted,
)


class TestCrypto(unittest.TestCase):
    def test_password_hashing_and_verification(self):
        pwd = "SecretPassword123"
        hashed = hash_password(pwd)
        self.assertIn("$", hashed)
        self.assertTrue(verify_password(pwd, hashed))
        self.assertFalse(verify_password("WrongPassword", hashed))

    def test_legacy_sha256_verification(self):
        import hashlib
        pwd = "LegacyPassword"
        legacy_hash = hashlib.sha256(pwd.encode()).hexdigest()
        self.assertTrue(verify_password(pwd, legacy_hash))
        self.assertFalse(verify_password("WrongPassword", legacy_hash))

    def test_encryption_decryption_roundtrip(self):
        data = b"Hello, World! Sensitive Vault Data"
        passcode = "MyPasscode123"

        payload = encrypt_bytes(data, passcode)
        self.assertTrue(payload.startswith(b"SVLT"))
        self.assertGreater(len(payload), 25)

        decrypted = decrypt_bytes(payload, passcode)
        self.assertEqual(decrypted, data)

    def test_decryption_wrong_passcode(self):
        data = b"Top Secret"
        passcode = "RightPasscode"

        payload = encrypt_bytes(data, passcode)
        with self.assertRaises(InvalidToken):
            decrypt_bytes(payload, "WrongPasscode")

    def test_is_encrypted_header_check(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            enc_path = os.path.join(tmp_dir, "enc_test.bin")
            plain_path = os.path.join(tmp_dir, "plain_test.txt")

            payload = encrypt_bytes(b"data", "pass")
            with open(enc_path, "wb") as f:
                f.write(payload)
            with open(plain_path, "wb") as f:
                f.write(b"Normal plain text file")

            self.assertTrue(is_encrypted(enc_path))
            self.assertFalse(is_encrypted(plain_path))


if __name__ == "__main__":
    unittest.main()
