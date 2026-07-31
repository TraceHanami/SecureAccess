import os
import hashlib
import hmac
import base64
import struct
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from .config import MAGIC, VERSION, ITERATIONS, SALT_SIZE


def hash_password(pwd: str, salt: bytes | str | None = None) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256 with a random salt."""
    if salt is None:
        salt_bytes = os.urandom(16)
    elif isinstance(salt, str):
        salt_bytes = bytes.fromhex(salt)
    else:
        salt_bytes = salt
    key = hashlib.pbkdf2_hmac("sha256", pwd.encode("utf-8"), salt_bytes, 200_000)
    return f"{salt_bytes.hex()}${key.hex()}"


def verify_password(pwd: str, stored_hash: str) -> bool:
    """Verify password against a stored PBKDF2 or legacy SHA-256 hash in constant time."""
    if "$" in stored_hash:
        salt_hex, _ = stored_hash.split("$", 1)
        computed = hash_password(pwd, salt=salt_hex)
        return hmac.compare_digest(computed, stored_hash)
    else:
        # Legacy unsalted SHA-256 fallback for backwards compatibility
        computed = hashlib.sha256(pwd.encode("utf-8")).hexdigest()
        return hmac.compare_digest(computed, stored_hash)


def derive_key(passcode: str, salt: bytes, iterations: int = ITERATIONS) -> bytes:
    """Derive a URL-safe base64 Fernet key using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return base64.urlsafe_b64encode(kdf.derive(passcode.encode()))


def is_encrypted(path: str) -> bool:
    """Check whether a file contains the SecureAccess magic byte header."""
    try:
        with open(path, "rb") as f:
            return f.read(4) == MAGIC
    except (OSError, Exception):
        return False


def encrypt_bytes(plaintext: bytes, passcode: str) -> bytes:
    """Encrypt raw plaintext bytes and return full payload with custom header."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(passcode, salt, iterations=ITERATIONS)
    fernet = Fernet(key)
    ciphertext = fernet.encrypt(plaintext)

    header = (
        MAGIC +
        struct.pack(">B", VERSION) +
        salt +
        struct.pack(">I", ITERATIONS)
    )
    return header + ciphertext


def decrypt_bytes(payload: bytes, passcode: str) -> bytes:
    """Decrypt payload bytes using passcode, extracting header parameters."""
    if len(payload) < 25 or payload[:4] != MAGIC:
        raise ValueError("File is not a valid encrypted vault file")

    version = struct.unpack(">B", payload[4:5])[0]
    salt = payload[5:21]
    iterations = struct.unpack(">I", payload[21:25])[0]
    ciphertext = payload[25:]

    key = derive_key(passcode, salt, iterations=iterations)
    fernet = Fernet(key)
    return fernet.decrypt(ciphertext)
