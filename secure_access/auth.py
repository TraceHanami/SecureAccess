import os
import json
import re
import platform
from .config import USER_FILE
from .crypto import hash_password, verify_password


def sanitize_username(username: str) -> bool:
    """Enforce alphanumeric usernames (3-32 chars) to prevent path traversal."""
    if not username or not re.match(r"^[a-zA-Z0-9_-]{3,32}$", username):
        return False
    return True


def load_users(user_file: str = USER_FILE) -> dict:
    """Load user credentials from JSON store."""
    if not os.path.exists(user_file):
        return {}
    try:
        with open(user_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_users(users: dict, user_file: str = USER_FILE) -> None:
    """Save user credentials to JSON store with secure file permissions."""
    with open(user_file, "w") as f:
        json.dump(users, f, indent=2)
    if platform.system() != "Windows":
        try:
            os.chmod(user_file, 0o600)
        except Exception:
            pass


def register_user(username: str, password: str, user_file: str = USER_FILE) -> tuple[bool, str]:
    """Register a new user account."""
    username = username.strip()
    if not username or not password:
        return False, "All fields are required"
    if not sanitize_username(username):
        return False, "Username must be 3-32 characters long (letters, numbers, underscores, hyphens)"
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"

    users = load_users(user_file)
    if username in users:
        return False, "User already exists"

    users[username] = hash_password(password)
    save_users(users, user_file)
    return True, "Account created successfully"


def authenticate_user(username: str, password: str, user_file: str = USER_FILE) -> tuple[bool, str]:
    """Authenticate user credentials and upgrade legacy hashes transparently."""
    username = username.strip()
    if not sanitize_username(username):
        return False, "Invalid credentials"

    users = load_users(user_file)
    if username not in users or not verify_password(password, users[username]):
        return False, "Invalid credentials"

    # Transparently upgrade legacy SHA-256 password hash to PBKDF2
    if "$" not in users[username]:
        users[username] = hash_password(password)
        save_users(users, user_file)

    return True, "Login successful"
