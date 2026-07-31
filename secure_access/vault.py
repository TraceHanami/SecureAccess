import os
import shutil
from .config import VAULT_DIR
from .auth import sanitize_username
from .crypto import encrypt_bytes, decrypt_bytes, is_encrypted


def get_user_vault(username: str, vault_dir: str = VAULT_DIR) -> str:
    """Return path to user's vault folder safely within directory boundaries."""
    if not username or not sanitize_username(username):
        raise ValueError("Invalid username or session state")
    vault_base = os.path.abspath(vault_dir)
    path = os.path.abspath(os.path.join(vault_base, username))
    if not path.startswith(vault_base):
        raise ValueError("Vault path boundary violation")
    os.makedirs(path, exist_ok=True)
    return path


def atomic_write(target_path: str, data: bytes) -> None:
    """Write data to target_path atomically using a temporary file."""
    tmp_path = target_path + ".tmp"
    try:
        with open(tmp_path, "wb") as f:
            f.write(data)
        os.replace(tmp_path, target_path)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        raise


def encrypt_vault_file(source_path: str, username: str, passcode: str, vault_dir: str = VAULT_DIR) -> tuple[str, bool, str]:
    """
    Encrypt a file into the user's vault directory.
    Returns (encrypted_file_path, is_external_file, original_file_path).
    """
    if is_encrypted(source_path):
        raise ValueError("This file is already encrypted")

    vault = get_user_vault(username, vault_dir)
    is_external = os.path.dirname(os.path.abspath(source_path)) != os.path.abspath(vault)
    target_path = os.path.join(vault, os.path.basename(source_path))

    if is_external:
        shutil.copy2(source_path, target_path)

    with open(target_path, "rb") as f:
        plaintext = f.read()

    encrypted_data = encrypt_bytes(plaintext, passcode)
    atomic_write(target_path, encrypted_data)

    return target_path, is_external, source_path


def decrypt_vault_file(target_path: str, passcode: str) -> None:
    """Decrypt a file in place in the user's vault."""
    if not is_encrypted(target_path):
        raise ValueError("This file is not encrypted")

    with open(target_path, "rb") as f:
        payload = f.read()

    plaintext = decrypt_bytes(payload, passcode)
    atomic_write(target_path, plaintext)
