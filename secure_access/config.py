import os

# Configuration Constants
USER_FILE = "users.json"
VAULT_DIR = "vaults"

MAGIC = b"SVLT"
VERSION = 1
ITERATIONS = 300_000
SALT_SIZE = 16
MAX_ATTEMPTS = 3
AUTO_LOGOUT_MS = 300000  # 5 minutes
