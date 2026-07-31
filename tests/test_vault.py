import unittest
import os
import tempfile
from secure_access.vault import (
    get_user_vault,
    atomic_write,
    encrypt_vault_file,
    decrypt_vault_file,
)
from secure_access.crypto import is_encrypted


class TestVault(unittest.TestCase):
    def test_get_user_vault_boundary_protection(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            vault_dir = os.path.join(tmp_dir, "vaults")
            vault_path = get_user_vault("alice", vault_dir=vault_dir)

            self.assertTrue(os.path.exists(vault_path))
            self.assertTrue(vault_path.startswith(os.path.abspath(tmp_dir)))

            with self.assertRaises(ValueError):
                get_user_vault("../invalid", vault_dir=vault_dir)

    def test_atomic_write(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            target = os.path.join(tmp_dir, "atomic.txt")
            data = b"Atomic Content"

            atomic_write(target, data)
            with open(target, "rb") as f:
                self.assertEqual(f.read(), data)
            self.assertFalse(os.path.exists(target + ".tmp"))

    def test_vault_encrypt_and_decrypt_flow(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            vault_dir = os.path.join(tmp_dir, "vaults")
            src_file = os.path.join(tmp_dir, "document.pdf")
            content = b"%PDF-1.4 sample PDF binary data"

            with open(src_file, "wb") as f:
                f.write(content)

            passcode = "VaultPass123"
            target_path, is_ext, orig = encrypt_vault_file(
                src_file, "bob", passcode, vault_dir=vault_dir
            )

            self.assertTrue(is_ext)
            self.assertTrue(is_encrypted(target_path))

            # Decrypt
            decrypt_vault_file(target_path, passcode)
            self.assertFalse(is_encrypted(target_path))
            with open(target_path, "rb") as f:
                self.assertEqual(f.read(), content)


if __name__ == "__main__":
    unittest.main()
