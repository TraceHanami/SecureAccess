# 🔐 SecureAccess — Personal File Vault

> A desktop application for encrypting and protecting sensitive files with strong cryptography and secure user authentication.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet)](https://github.com/TomSchimansky/CustomTkinter)
[![Cryptography](https://img.shields.io/badge/Crypto-Fernet%20%7C%20PBKDF2-orange)](https://cryptography.io)
[![CI](https://github.com/TraceHanami/SecureAccess/actions/workflows/ci.yml/badge.svg)](https://github.com/TraceHanami/SecureAccess/actions)

---

## 🌟 Overview

**SecureAccess** is a desktop-based personal file vault that enables users to encrypt and decrypt sensitive files using industry-standard cryptographic techniques. It combines secure user authentication with authenticated encryption to ensure that only authorized users can access protected files.

This project demonstrates practical implementation of applied cryptography, secure access control, and modular Python application design.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🔑 **User Authentication** | Secure login and signup with sanitized username boundary checks |
| 🔒 **Password Hashing** | PBKDF2-HMAC-SHA256 with 200,000 iterations & random 16-byte salt |
| 🧂 **Key Derivation** | PBKDF2 key derivation with 300,000 iterations per encryption task |
| 🛡️ **Authenticated Encryption** | Fernet (AES-128-CBC + HMAC-SHA256) for payload confidentiality & integrity |
| ⚛️ **Atomic File Operations** | Prevents file corruption during unexpected crashes via temporary staging |
| 🏷️ **Header Validation** | 25-byte binary header (`b"SVLT"`) format to verify file integrity |
| 🖥️ **Modern GUI** | Responsive dark mode interface built with CustomTkinter |
| 🔓 **Session Hardening** | 5-minute inactivity auto-logout and 3-attempt account lockout |

---

## 🏗️ Security Architecture

```
Password
   │
   ▼
PBKDF2-HMAC-SHA256 (200k iterations + 16B salt) ──► Stored in users.json (0o600)
   │
   ▼
Passcode + File Salt (16B) ──► PBKDF2HMAC (300k iterations)
                                    │
                                    ▼
Derived 32-Byte Key ──► Fernet (AES-128-CBC + HMAC-SHA256)
                                    │
                                    ▼
                Encrypted Vault File (Header: b"SVLT" | Version 1 | Salt | Iterations)
```

---

## 📁 Modular Project Structure

```
SecureAccess/
├── .github/workflows/ci.yml # GitHub Actions CI automation
├── secure_access/           # Main application package
│   ├── __init__.py          # Package initialization & versioning
│   ├── config.py            # Global constants & configuration
│   ├── crypto.py            # Key derivation & Fernet encryption engines
│   ├── auth.py              # User authentication & PBKDF2 hashing
│   ├── vault.py             # Vault path validation & atomic file writing
│   └── gui.py               # CustomTkinter GUI application
├── tests/                   # Automated test suite
│   ├── test_crypto.py       # Crypto unit tests
│   ├── test_auth.py         # Authentication unit tests
│   └── test_vault.py        # Vault & atomic file write tests
├── secure_access.py         # Root entry point launcher script
├── pyproject.toml           # Modern Python package build configuration
├── requirements.txt         # Dependencies
├── LICENSE                  # MIT License
└── README.md                # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TraceHanami/SecureAccess.git
   cd SecureAccess
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python secure_access.py
   ```

---

## 🧪 Running Unit Tests

The repository includes a comprehensive unit test suite:

```bash
python -m unittest discover -s tests
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**TraceHanami**  
GitHub: [@TraceHanami](https://github.com/TraceHanami/SecureAccess)
