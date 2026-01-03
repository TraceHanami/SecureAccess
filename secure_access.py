import customtkinter as ctk
from customtkinter import CTkImage
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import os, json, hashlib, base64, struct, shutil, time , platform, subprocess

# ================= CONFIG =================
USER_FILE = "users.json"
VAULT_DIR = "vaults"

MAGIC = b"SVLT"
VERSION = 1
ITERATIONS = 300_000
SALT_SIZE = 16
MAX_ATTEMPTS = 3
AUTO_LOGOUT_MS = 300000  # 5 minutes

# ================= GUI SETUP =================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("540x640")
app.title("SecureAccess – Personal File Vault")

# ================= HELPERS =================
def hash_password(pwd):
    return hashlib.sha256(pwd.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

def derive_key(passcode: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(passcode.encode()))

def is_encrypted(path):
    try:
        with open(path, "rb") as f:
            return f.read(4) == MAGIC
    except:
        return False

def get_user_vault():
    """Return path to the current user's vault folder."""
    path = os.path.join(VAULT_DIR, current_user)
    os.makedirs(path, exist_ok=True)
    return path

# ================= SESSION =================
current_user = None
login_attempts = 0
auto_logout_timer = None

# ================= FRAMES =================
login_frame = ctk.CTkFrame(app)
signup_frame = ctk.CTkFrame(app)
dashboard_frame = ctk.CTkFrame(app)

def switch(frame):
    global auto_logout_timer
    # Cancel auto-logout timer when switching frames
    if auto_logout_timer:
        app.after_cancel(auto_logout_timer)
        auto_logout_timer = None
    for f in (login_frame, signup_frame, dashboard_frame):
        f.pack_forget()
    frame.pack(fill="both", expand=True)

# ================= LOGIN =================
ctk.CTkLabel(login_frame, text="SecureAccess Login", font=("Arial", 20)).pack(pady=20)
login_user = ctk.CTkEntry(login_frame, placeholder_text="Username")
login_pass = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*")
login_user.pack(pady=5)
login_pass.pack(pady=5)

def reset_auto_logout():
    """Reset auto-logout timer."""
    global auto_logout_timer
    if auto_logout_timer:
        app.after_cancel(auto_logout_timer)
    auto_logout_timer = app.after(AUTO_LOGOUT_MS, logout)

def require_login():
    if not current_user:
        messagebox.showerror("Unauthorized", "Please login first")
        switch(login_frame)
        return False
    reset_auto_logout()
    return True

def logout():
    global current_user, login_attempts, auto_logout_timer
    current_user = None
    login_attempts = 0
    status_box.delete("1.0", "end")
    switch(login_frame)
    if auto_logout_timer:
        app.after_cancel(auto_logout_timer)
        auto_logout_timer = None

def login():
    global current_user, login_attempts
    users = load_users()
    u, p = login_user.get(), login_pass.get()

    if u not in users or users[u] != hash_password(p):
        login_attempts += 1
        if login_attempts >= MAX_ATTEMPTS:
            messagebox.showerror("Locked", "Too many wrong attempts! Try later.")
            login_attempts = 0
            return
        messagebox.showerror("Login Failed", "Invalid credentials")
        return

    current_user = u
    login_attempts = 0
    switch(dashboard_frame)
    reset_auto_logout()

ctk.CTkButton(login_frame, text="Login", command=login).pack(pady=10)
ctk.CTkButton(login_frame, text="Create Account", command=lambda: switch(signup_frame)).pack()

# ================= SIGNUP =================
ctk.CTkLabel(signup_frame, text="Create Account", font=("Arial", 20)).pack(pady=20)
new_user = ctk.CTkEntry(signup_frame, placeholder_text="Username")
new_pass = ctk.CTkEntry(signup_frame, placeholder_text="Password", show="*")
new_user.pack(pady=5)
new_pass.pack(pady=5)

def signup():
    users = load_users()
    u, p = new_user.get(), new_pass.get()

    if not u or not p:
        messagebox.showwarning("Error", "All fields required")
        return
    if u in users:
        messagebox.showerror("Error", "User already exists")
        return

    users[u] = hash_password(p)
    save_users(users)
    messagebox.showinfo("Success", "Account created")
    switch(login_frame)

ctk.CTkButton(signup_frame, text="Register", command=signup).pack(pady=10)
ctk.CTkButton(signup_frame, text="Back", command=lambda: switch(login_frame)).pack()

# ================= DASHBOARD =================
ctk.CTkLabel(dashboard_frame, text="Secure Vault", font=("Arial", 20)).pack(pady=15)

status_box = ctk.CTkTextbox(dashboard_frame, height=220)
status_box.pack(padx=15, pady=10, fill="x")

def log(msg):
    status_box.insert("end", msg + "\n")
    status_box.see("end")
    reset_auto_logout()

# ================= ENCRYPT FILE =================
def encrypt_file():
    if not require_login():
        return

    path = filedialog.askopenfilename()
    if not path:
        return

    if is_encrypted(path):
        messagebox.showwarning("Already Encrypted", "This file is already encrypted")
        return

    passcode = simpledialog.askstring("Passcode", "Enter encryption passcode", show="*")
    if not passcode:
        return

    # Copy file to user's vault
    vault = get_user_vault()
    dest = os.path.join(vault, os.path.basename(path))
    shutil.copy2(path, dest)
    path = dest

    with open(path, "rb") as f:
        plaintext = f.read()

    salt = os.urandom(SALT_SIZE)
    key = derive_key(passcode, salt)
    fernet = Fernet(key)
    ciphertext = fernet.encrypt(plaintext)

    header = (
        MAGIC +
        struct.pack(">B", VERSION) +
        salt +
        struct.pack(">I", ITERATIONS)
    )

    with open(path, "wb") as f:
        f.write(header + ciphertext)

    log(f"[+] Encrypted: {os.path.basename(path)}")

# ================= DECRYPT FILE =================
def decrypt_file():
    if not require_login():
        return

    path = filedialog.askopenfilename()
    if not path:
        return

    if not is_encrypted(path):
        messagebox.showwarning("Not Encrypted", "This file is not encrypted")
        return

    passcode = simpledialog.askstring("Passcode", "Enter decryption passcode", show="*")
    if not passcode:
        return

    with open(path, "rb") as f:
        magic = f.read(4)
        version = struct.unpack(">B", f.read(1))[0]
        salt = f.read(SALT_SIZE)
        iterations = struct.unpack(">I", f.read(4))[0]
        ciphertext = f.read()

    try:
        key = derive_key(passcode, salt)
        fernet = Fernet(key)
        plaintext = fernet.decrypt(ciphertext)
    except InvalidToken:
        messagebox.showerror("Failed", "Wrong passcode or file tampered")
        return

    with open(path, "wb") as f:
        f.write(plaintext)

    log(f"[+] Decrypted: {os.path.basename(path)}")

# ================= OPEN VAULT =================
def open_vault():
    if not require_login():
        return
    vault = get_user_vault()
    try:
        system_platform = platform.system()
        if system_platform == "Windows":
            os.startfile(vault)
        elif system_platform == "Darwin":  # macOS
            subprocess.run(["open", vault])
        else:  # Linux / Unix
            subprocess.run(["xdg-open", vault])
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open vault folder:\n{e}")

# ================= BUTTONS =================
ctk.CTkButton(dashboard_frame, text="Encrypt File", command=encrypt_file).pack(pady=6)
ctk.CTkButton(dashboard_frame, text="Decrypt File", command=decrypt_file).pack(pady=6)
ctk.CTkButton(dashboard_frame, text="Open My Vault Folder", command=open_vault).pack(pady=6)
ctk.CTkButton(dashboard_frame, text="Logout", command=logout, fg_color="gray").pack(pady=20)

# ================= START =================
switch(login_frame)
app.mainloop()
