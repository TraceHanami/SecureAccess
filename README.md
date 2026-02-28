# 🔐 SecureAccess — Personal File Vault

> A desktop application for encrypting and protecting sensitive files with strong cryptography and user authentication.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet)](https://github.com/TomSchimansky/CustomTkinter)
[![Cryptography](https://img.shields.io/badge/Crypto-Fernet%20%7C%20PBKDF2-orange)](https://cryptography.io)

---

## Overview

**SecureAccess** is a desktop-based personal file vault that enables users to encrypt and decrypt sensitive files using industry-standard cryptographic techniques. It combines secure user authentication with authenticated encryption to ensure that only authorized users can access protected files.

This project demonstrates practical implementation of applied cryptography, secure access control, and desktop application security using Python.

---

## Features

| Feature | Description |
|---|---|
| 🔑 User Authentication | Secure login and signup with persistent user accounts |
| 🔒 Password Hashing | SHA-256 hashing for stored credentials |
| 🧂 Key Derivation | PBKDF2 with salt and high iteration count for strong key derivation |
| 🛡️ Authenticated Encryption | Fernet (AES-128-CBC + HMAC-SHA256) for file encryption |
| 📁 In-Place Operations | Encrypt and decrypt files without creating duplicates |
| 🏷️ Encrypted File Headers | Custom header validation to verify file integrity |
| 🖥️ Modern GUI | Clean, responsive interface built with CustomTkinter |
| 🔓 Session Management | Secure session handling with logout support |

---

## Tech Stack

- **Language:** Python 3.8+
- **GUI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Cryptography:** [cryptography](https://cryptography.io) — Fernet, PBKDF2HMAC
- **Storage:** Local JSON-based user store

---

## Security Architecture

```
Password
   │
   ▼
SHA-256 Hash ──────────────► Stored in users.json
   │
   ▼
PBKDF2HMAC (salt + iterations)
   │
   ▼
Derived Key
   │
   ▼
Fernet (AES-128-CBC + HMAC-SHA256)
   │
   ▼
Encrypted File (with custom header)
```

- **Key derivation** uses PBKDF2 with a unique salt per user and a high iteration count, making brute-force attacks computationally expensive.
- **Fernet encryption** provides authenticated encryption, guaranteeing both confidentiality and integrity of encrypted files.
- **Custom file headers** allow SecureAccess to validate encrypted files before attempting decryption.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/TraceHanami/SecureAccess.git
cd SecureAccess
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the application**

```bash
python secure_access.py
```

---

## Usage

1. **Sign Up** — Create a new account with a username and password.
2. **Log In** — Authenticate with your credentials to start a session.
3. **Encrypt a File** — Select any file to encrypt it in place. The file is protected with your derived key.
4. **Decrypt a File** — Select an encrypted file to restore it to its original form.
5. **Log Out** — End your session securely.

> ⚠️ **Important:** If you forget your password, encrypted files cannot be recovered. There is no password reset mechanism by design.

---

## Project Structure

```
SecureAccess/
├── secure_access.py      # Main application entry point
├── requirements.txt      # Python dependencies
├── users.json            # Local user credential store (auto-generated)
└── README.md
```

---

## Requirements

```
customtkinter
cryptography
```

Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a pull request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Author

**TraceHanami**  
GitHub: [@TraceHanami](https://github.com/TraceHanami/SecureAccess)

---

*Built as a demonstration of applied cryptography and secure desktop application development in Python.*
