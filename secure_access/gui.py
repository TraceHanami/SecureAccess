import os
import platform
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from cryptography.fernet import InvalidToken

from .config import AUTO_LOGOUT_MS, MAX_ATTEMPTS
from .auth import register_user, authenticate_user
from .vault import get_user_vault, encrypt_vault_file, decrypt_vault_file, is_encrypted


class SecureAccessApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.app = ctk.CTk()
        self.app.geometry("540x640")
        self.app.title("SecureAccess – Personal File Vault")

        self.current_user = None
        self.login_attempts = 0
        self.auto_logout_timer = None

        self._build_ui()
        self.switch(self.login_frame)

    def _build_ui(self):
        # Frames
        self.login_frame = ctk.CTkFrame(self.app)
        self.signup_frame = ctk.CTkFrame(self.app)
        self.dashboard_frame = ctk.CTkFrame(self.app)

        # Login Frame
        ctk.CTkLabel(self.login_frame, text="SecureAccess Login", font=("Arial", 20)).pack(pady=20)
        self.login_user_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username")
        self.login_pass_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Password", show="*")
        self.login_user_entry.pack(pady=5)
        self.login_pass_entry.pack(pady=5)

        ctk.CTkButton(self.login_frame, text="Login", command=self.login).pack(pady=10)
        ctk.CTkButton(self.login_frame, text="Create Account", command=lambda: self.switch(self.signup_frame)).pack()

        # Signup Frame
        ctk.CTkLabel(self.signup_frame, text="Create Account", font=("Arial", 20)).pack(pady=20)
        self.signup_user_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="Username")
        self.signup_pass_entry = ctk.CTkEntry(self.signup_frame, placeholder_text="Password", show="*")
        self.signup_user_entry.pack(pady=5)
        self.signup_pass_entry.pack(pady=5)

        ctk.CTkButton(self.signup_frame, text="Register", command=self.signup).pack(pady=10)
        ctk.CTkButton(self.signup_frame, text="Back", command=lambda: self.switch(self.login_frame)).pack()

        # Dashboard Frame
        ctk.CTkLabel(self.dashboard_frame, text="Secure Vault", font=("Arial", 20)).pack(pady=15)

        self.status_box = ctk.CTkTextbox(self.dashboard_frame, height=220)
        self.status_box.pack(padx=15, pady=10, fill="x")

        ctk.CTkButton(self.dashboard_frame, text="Encrypt File", command=self.encrypt_file).pack(pady=6)
        ctk.CTkButton(self.dashboard_frame, text="Decrypt File", command=self.decrypt_file).pack(pady=6)
        ctk.CTkButton(self.dashboard_frame, text="Open My Vault Folder", command=self.open_vault).pack(pady=6)
        ctk.CTkButton(self.dashboard_frame, text="Logout", command=self.logout, fg_color="gray").pack(pady=20)

    def switch(self, frame):
        if self.auto_logout_timer:
            self.app.after_cancel(self.auto_logout_timer)
            self.auto_logout_timer = None
        for f in (self.login_frame, self.signup_frame, self.dashboard_frame):
            f.pack_forget()
        frame.pack(fill="both", expand=True)

    def reset_auto_logout(self):
        if self.auto_logout_timer:
            self.app.after_cancel(self.auto_logout_timer)
        self.auto_logout_timer = self.app.after(AUTO_LOGOUT_MS, self.logout)

    def require_login(self):
        if not self.current_user:
            messagebox.showerror("Unauthorized", "Please login first")
            self.switch(self.login_frame)
            return False
        self.reset_auto_logout()
        return True

    def log(self, msg):
        self.status_box.insert("end", msg + "\n")
        self.status_box.see("end")
        self.reset_auto_logout()

    def login(self):
        u = self.login_user_entry.get()
        p = self.login_pass_entry.get()

        success, msg = authenticate_user(u, p)
        if not success:
            self.login_attempts += 1
            if self.login_attempts >= MAX_ATTEMPTS:
                messagebox.showerror("Locked", "Too many wrong attempts! Try later.")
                self.login_attempts = 0
                return
            messagebox.showerror("Login Failed", msg)
            return

        self.current_user = u.strip()
        self.login_attempts = 0
        self.login_pass_entry.delete(0, "end")
        self.switch(self.dashboard_frame)
        self.reset_auto_logout()

    def signup(self):
        u = self.signup_user_entry.get()
        p = self.signup_pass_entry.get()

        success, msg = register_user(u, p)
        if not success:
            messagebox.showerror("Registration Error", msg)
            return

        self.signup_user_entry.delete(0, "end")
        self.signup_pass_entry.delete(0, "end")
        messagebox.showinfo("Success", msg)
        self.switch(self.login_frame)

    def logout(self):
        self.current_user = None
        self.login_attempts = 0
        self.login_user_entry.delete(0, "end")
        self.login_pass_entry.delete(0, "end")
        self.signup_user_entry.delete(0, "end")
        self.signup_pass_entry.delete(0, "end")
        self.status_box.delete("1.0", "end")
        self.switch(self.login_frame)
        if self.auto_logout_timer:
            self.app.after_cancel(self.auto_logout_timer)
            self.auto_logout_timer = None

    def encrypt_file(self):
        if not self.require_login():
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

        if not self.current_user:
            messagebox.showerror("Unauthorized", "Session expired. Please login again.")
            self.switch(self.login_frame)
            return

        try:
            target_path, is_external, orig_path = encrypt_vault_file(path, self.current_user, passcode)
            if is_external:
                self.log(f"[+] Encrypted copy created in vault: {os.path.basename(target_path)}")
                if messagebox.askyesno("Delete Original?", f"File encrypted in vault!\nDo you want to delete the unencrypted original?\n\n{orig_path}"):
                    try:
                        os.remove(orig_path)
                        self.log(f"[-] Deleted unencrypted original: {os.path.basename(orig_path)}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to delete original file:\n{e}")
            else:
                self.log(f"[+] Encrypted: {os.path.basename(target_path)}")
        except Exception as e:
            messagebox.showerror("Encryption Error", f"Failed to encrypt file:\n{e}")

    def decrypt_file(self):
        if not self.require_login():
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

        if not self.current_user:
            messagebox.showerror("Unauthorized", "Session expired. Please login again.")
            self.switch(self.login_frame)
            return

        try:
            decrypt_vault_file(path, passcode)
            self.log(f"[+] Decrypted: {os.path.basename(path)}")
        except InvalidToken:
            messagebox.showerror("Failed", "Wrong passcode or file tampered")
        except Exception as e:
            messagebox.showerror("Decryption Error", f"Failed to decrypt file:\n{e}")

    def open_vault(self):
        if not self.require_login():
            return
        try:
            vault = get_user_vault(self.current_user)
            system_platform = platform.system()
            if system_platform == "Windows":
                os.startfile(vault)
            elif system_platform == "Darwin":
                subprocess.run(["open", vault])
            else:
                subprocess.run(["xdg-open", vault])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open vault folder:\n{e}")

    def run(self):
        self.app.mainloop()


def main():
    app = SecureAccessApp()
    app.run()


if __name__ == "__main__":
    main()
