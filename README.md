# 🔐 SecureAccess – Personal File Vault

SecureAccess is a desktop-based personal file vault designed to securely encrypt and decrypt sensitive files using strong cryptographic techniques and user authentication.

This project demonstrates practical implementation of applied cryptography, secure access control, and desktop application security using Python.

---

## ✨ Features

- User authentication (Login & Signup)
- Secure password hashing (SHA-256)
- PBKDF2 key derivation with salt and high iteration count
- Authenticated file encryption using Fernet (AES)
- In-place file encryption and decryption
- Custom encrypted file header for validation
- Modern GUI built with CustomTkinter
- Secure session handling and logout

---

## 🛠 Tech Stack

- **Language:** Python  
- **GUI:** CustomTkinter  
- **Cryptography:** Cryptography (Fernet, PBKDF2)  
- **Storage:** Local JSON-based user storage  

---

## 🚀 How to Run

### 1. Clone the repository
```bash
git clone https://github.com/TraceHanami/SecureAccess.git
cd SecureAccess

## Install dependencies
pip install -r requirements.txt

## Run the Application
python secure_access.py
