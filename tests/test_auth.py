import unittest
import os
import tempfile
from secure_access.auth import (
    sanitize_username,
    register_user,
    authenticate_user,
)


class TestAuth(unittest.TestCase):
    def test_sanitize_username(self):
        self.assertTrue(sanitize_username("valid_user123"))
        self.assertTrue(sanitize_username("user-name"))
        self.assertFalse(sanitize_username("../admin"))
        self.assertFalse(sanitize_username("user/dir"))
        self.assertFalse(sanitize_username("a"))  # too short
        self.assertFalse(sanitize_username("a" * 35))  # too long

    def test_register_and_authenticate_user(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_file = os.path.join(tmp_dir, "users_test.json")

            # Register valid user
            ok, msg = register_user("testuser", "password123", user_file=user_file)
            self.assertTrue(ok)
            self.assertIn("successfully", msg.lower())

            # Duplicate registration
            ok_dup, msg_dup = register_user("testuser", "password123", user_file=user_file)
            self.assertFalse(ok_dup)
            self.assertIn("already exists", msg_dup.lower())

            # Authenticate valid user
            ok_auth, _ = authenticate_user("testuser", "password123", user_file=user_file)
            self.assertTrue(ok_auth)

            # Authenticate wrong password
            ok_bad, _ = authenticate_user("testuser", "wrongpassword", user_file=user_file)
            self.assertFalse(ok_bad)


if __name__ == "__main__":
    unittest.main()
