import tkinter as tk
from tkinter import messagebox, ttk
import tempfile
import webbrowser
import os
import datetime
import hashlib
import random
import string
import uuid
import re

# ==========================================
# --- SECURITY / AUTHENTICATION SYSTEM ---
# ==========================================
# Secret key used for cryptographic passkey calculation
MASTER_KEY = "SECRET_KEY_123"
AUTH_FILE = "auth_status.txt"
LICENSE_FILE = "app_license.lic"

# Pre-defined Master Activation Keys for permanent unlock
SPECIAL_KEYS = [
    "AUTH-A7X9-M4Q2-V8L1",
    "AUTH-K3B6-J9N5-W2P4",
    "AUTH-Y1T8-C5R7-H6F3",
    "AUTH-Z9E4-D2S8-G1M7",
    "AUTH-P5W3-L8K1-X7N9",
    "AUTH-Q2V6-T4Y9-B3C5",
    "AUTH-N8J1-F7H2-R9M4",
    "AUTH-E5G3-S1D6-A2X8",
    "AUTH-W4P7-K9L2-V5T1",
    "AUTH-C8B2-M6Q9-J3F7"
]

def get_hardware_id():
    """Generates a unique hardware identifier based on MAC address."""
    return str(uuid.getnode())

def is_permanently_unlocked():
    """Checks if the application has been permanently unlocked on this device."""
    try:
        if os.path.exists(LICENSE_FILE):
            with open(LICENSE_FILE, "r") as f:
                stored_hash = f.read().strip()
            hardware_id = get_hardware_id()
            for key in SPECIAL_KEYS:
                expected_hash = hashlib.sha256(f"{key}{hardware_id}".encode('utf-8')).hexdigest()
                if stored_hash == expected_hash:
                    return True
    except Exception:
        pass
    return False

def save_permanent_unlock(special_key):
    """Saves the hashed special key bound to the hardware node ID."""
    hardware_id = get_hardware_id()
    key_hash = hashlib.sha256(f"{special_key}{hardware_id}".encode('utf-8')).hexdigest()
    try:
        with open(LICENSE_FILE, "w") as f:
            f.write(key_hash)
    except Exception:
        pass

def calculate_passkey(spl_code, secret_key):
    """Calculates a 6-digit numeric passkey using SHA-256 digest of the Spl code + secret key."""
    combined_data = f"{spl_code}{secret_key}".encode('utf-8')
    hash_hex = hashlib.sha256(combined_data).hexdigest()
    return str(int(hash_hex[:8], 16) % 1000000).zfill(6)

def is_authenticated_today():
    """Checks if daily authentication was already completed for today."""
    try:
        if os.path.exists(AUTH_FILE):
            with open(AUTH_FILE, "r") as f:
                last_auth_date = f.read().strip()
            if last_auth_date == str(datetime.date.today()):
                return True
    except Exception:
        pass
    return False

def save_auth_today():
    """Saves today's date upon successful daily authentication."""
    try:
        with open(AUTH_FILE, "w") as f:
            f.write(str(datetime.date.today()))
    except Exception:
        pass


class AuthWindow:
    """Authentication UI Window for College Mini Project."""
    def __init__(self, root, spl_code, correct_passkey):
        self.root = root
        self.spl_code = spl_code
        self.correct_passkey = correct_passkey
        self.authenticated = False
        
        self.win = tk.Toplevel(root)
        self.win.title("College Mini Project - Secure Authenticator")
        self.win.geometry("550x430")
        self.win.configure(bg="#050510") 
        
        self.win.update_idletasks()
        width, height = 550, 430
        x = (self.win.winfo_screenwidth() // 2) - (width // 2)
        y = (self.win.winfo_screenheight() // 2) - (height // 2)
        self.win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        self.win.resizable(False, False)
        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        
        main_frame = tk.Frame(self.win, bg="#050510", highlightbackground="#00e5ff", highlightthickness=2)
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)
        
        header = tk.Label(main_frame, text="✦ SECURE AUTHENTICATOR ✦", font=("Impact", 24), fg="#ff0055", bg="#050510")
        header.pack(pady=(20, 5))
        
        sub = tk.Label(main_frame, text="COLLEGE MINI PROJECT // SECURE LOGIN ACCESS", font=("Courier", 10, "bold"), fg="#aaaaaa", bg="#050510")
        sub.pack(pady=(0, 20))
        
        code_frame = tk.Frame(main_frame, bg="#111122", highlightbackground="#00e5ff", highlightthickness=1)
        code_frame.pack(pady=10, ipadx=40, ipady=15)
        
        tk.Label(code_frame, text=">>> DAILY SECURITY TOKEN <<<", font=("Courier", 10, "bold"), fg="#00e5ff", bg="#111122").pack(pady=(0, 8))
        tk.Label(code_frame, text=self.spl_code, font=("Consolas", 32, "bold"), fg="#00ff88", bg="#111122").pack()
        
        tk.Label(main_frame, text="INPUT ACTIVATION PASSKEY:", font=("Arial", 11, "bold"), fg="#ffffff", bg="#050510").pack(pady=(20, 5))
        
        self.key_entry = tk.Entry(main_frame, font=("Courier", 18, "bold"), justify="center", bg="#1a1a2e", fg="#00e5ff", insertbackground="#00e5ff", relief="flat")
        self.key_entry.pack(pady=5, ipadx=10, ipady=8)
        self.key_entry.focus()
        self.key_entry.bind("<Return>", self.check_auth)
        
        submit_btn = tk.Button(main_frame, text="[ Verify Passkey ]", font=("Courier", 13, "bold"), bg="#00e5ff", fg="#050510", activebackground="#00ff88", activeforeground="#050510", relief="flat", cursor="hand2", command=self.check_auth)
        submit_btn.pack(pady=20, ipadx=6, ipady=2)
        
    def check_auth(self, event=None):
        user_input = self.key_entry.get().strip()
        if user_input in SPECIAL_KEYS:
            save_permanent_unlock(user_input)
            messagebox.showinfo("License Activated", "Special Master Key Accepted!\nThis device is now permanently unlocked.", parent=self.win)
            self.authenticated = True
            self.win.destroy()
        elif user_input == self.correct_passkey:
            save_auth_today()
            messagebox.showinfo("Success", "Daily Authentication Successful!", parent=self.win)
            self.authenticated = True
            self.win.destroy()
        else:
            messagebox.showerror("Access Denied", "Incorrect Key! Please try again.", parent=self.win)
            self.key_entry.delete(0, tk.END)
            
    def on_close(self):
        self.authenticated = False
        self.win.destroy()


def run_authentication(root_window):
    """Executes authentication flow."""
    if is_permanently_unlocked():
        return True
    if is_authenticated_today():
        return True

    length = random.randint(4, 8)
    chars = string.ascii_letters + string.digits + "@#$*&"
    spl_code = "".join(random.choice(chars) for _ in range(length))
    correct_daily_passkey = calculate_passkey(spl_code, MASTER_KEY)

    auth_ui = AuthWindow(root_window, spl_code, correct_daily_passkey)
    root_window.wait_window(auth_ui.win) 

    return auth_ui.authenticated


# ==========================================
# MAIN APPLICATION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main root window during authentication

    # Run authentication directly without declaration window
    if run_authentication(root):
        root.deiconify()
        root.title("College Mini Project - Main Application")
        root.geometry("600x400")
        
        # Center main window
        w, h = 600, 400
        sx = (root.winfo_screenwidth() // 2) - (w // 2)
        sy = (root.winfo_screenheight() // 2) - (h // 2)
        root.geometry(f"{w}x{h}+{sx}+{sy}")
        root.configure(bg="#0f172a")
        
        main_card = tk.Frame(root, bg="#1e293b", padx=30, pady=30, highlightbackground="#38bdf8", highlightthickness=1)
        main_card.pack(expand=True, padx=20, pady=20)
        
        tk.Label(main_card, text="✦ COLLEGE MINI PROJECT ✦", font=("Impact", 22), fg="#38bdf8", bg="#1e293b").pack(pady=(0, 10))
        tk.Label(main_card, text="Authentication Successful!", font=("Helvetica", 14, "bold"), fg="#4ade80", bg="#1e293b").pack(pady=5)
        tk.Label(main_card, text="Welcome to the main application interface.", font=("Helvetica", 11), fg="#94a3b8", bg="#1e293b").pack(pady=10)
        
        tk.Button(main_card, text="Exit Application", font=("Helvetica", 11, "bold"), bg="#ef4444", fg="#ffffff", relief="flat", padx=15, pady=5, cursor="hand2", command=root.destroy).pack(pady=(15, 0))
        
        root.mainloop()
    else:
        root.destroy()
