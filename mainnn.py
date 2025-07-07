import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import pyperclip
import random
import json
import os

SIMILAR_CHARS = "Il1O0"
AMBIGUOUS_CHARS = '{}[]()/\\\"`~,;:.<>'

def generate_password(length, use_lower, use_upper, use_digits, use_symbols, exclude_similar, exclude_ambiguous):
    lower = "abcdefghijklmnopqrstuvwxyz"
    upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    symbols = "!@#$%^&*()-_+=<>?/"

    char_pool = ""
    if use_lower:
        char_pool += lower
    if use_upper:
        char_pool += upper
    if use_digits:
        char_pool += digits
    if use_symbols:
        char_pool += symbols

    if exclude_similar:
        char_pool = ''.join(c for c in char_pool if c not in SIMILAR_CHARS)
    if exclude_ambiguous:
        char_pool = ''.join(c for c in char_pool if c not in AMBIGUOUS_CHARS)

    if not char_pool:
        raise ValueError("No character types selected")

    return ''.join(random.choice(char_pool) for _ in range(length))

def get_strength_level(password):
    length = len(password)
    categories = 0

    if any(c.islower() for c in password):
        categories += 1
    if any(c.isupper() for c in password):
        categories += 1
    if any(c.isdigit() for c in password):
        categories += 1
    if any(c in "!@#$%^&*()-_+=<>?/" for c in password):
        categories += 1

    if length >= 12 and categories >= 3:
        return "Strong", "success"
    elif length >= 8 and categories >= 2:
        return "Medium", "warning"
    else:
        return "Weak", "danger"

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator & Manager")
        self.create_widgets()

    def create_widgets(self):
        tb.Label(self.root, text="Password Length:").pack(pady=(10, 0))
        self.length_entry = tb.Entry(self.root, width=10)
        self.length_entry.insert(0, "12")
        self.length_entry.pack(pady=(0, 10))

        self.use_lower = tb.BooleanVar(value=True)
        self.use_upper = tb.BooleanVar(value=True)
        self.use_digits = tb.BooleanVar(value=True)
        self.use_symbols = tb.BooleanVar(value=True)
        self.exclude_similar = tb.BooleanVar()
        self.exclude_ambiguous = tb.BooleanVar()

        options = [
            ("Include Lowercase", self.use_lower),
            ("Include Uppercase", self.use_upper),
            ("Include Numbers", self.use_digits),
            ("Include Symbols", self.use_symbols),
            ("Exclude Similar Characters", self.exclude_similar),
            ("Exclude Ambiguous Characters", self.exclude_ambiguous)
        ]

        for label, var in options:
            tb.Checkbutton(self.root, text=label, variable=var).pack(anchor="w", padx=20)

        tb.Button(self.root, text="Generate Password", command=self.generate, bootstyle="success").pack(pady=10)

        self.output = tb.Entry(self.root, width=35, justify="center")
        self.output.pack(pady=(0, 10))

        tb.Button(self.root, text="Copy to Clipboard", command=self.copy_to_clipboard, bootstyle="info").pack()

        self.strength_label = tb.Label(self.root, text="", font=("Arial", 10, "bold"))
        self.strength_label.pack(pady=(10, 10))

        tb.Label(self.root, text="Website:").pack()
        self.website_entry = tb.Entry(self.root, width=35)
        self.website_entry.pack(pady=(0, 5))

        tb.Label(self.root, text="Email/Username:").pack()
        self.username_entry = tb.Entry(self.root, width=35)
        self.username_entry.pack(pady=(0, 5))

        tb.Button(self.root, text="Save to File", command=self.save_password, bootstyle="primary").pack(pady=10)

        tb.Button(self.root, text="View Saved Credentials", command=self.view_saved_credentials, bootstyle="secondary").pack(pady=5)

    def generate(self):
        try:
            length = int(self.length_entry.get())
            password = generate_password(
                length=length,
                use_lower=self.use_lower.get(),
                use_upper=self.use_upper.get(),
                use_digits=self.use_digits.get(),
                use_symbols=self.use_symbols.get(),
                exclude_similar=self.exclude_similar.get(),
                exclude_ambiguous=self.exclude_ambiguous.get()
            )
            self.output.delete(0, tb.END)
            self.output.insert(0, password)
            strength, color = get_strength_level(password)
            self.strength_label.config(text=f"Strength:  {strength}", bootstyle=color)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def copy_to_clipboard(self):
        password = self.output.get()
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!")
        else:
            messagebox.showwarning("Empty", "No password to copy.")

    def save_password(self):
        website = self.website_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.output.get().strip()

        if not website or not username or not password:
            messagebox.showwarning("Incomplete", "Please fill all fields to save.")
            return

        new_data = {
            website: {
                "email": username,
                "password": password
            }
        }

        try:
            if os.path.exists("data.json"):
                with open("data.json", "r") as file:
                    data = json.load(file)
            else:
                data = {}

            data.update(new_data)

            with open("data.json", "w") as file:
                json.dump(data, file, indent=4)

            messagebox.showinfo("Saved", f"Credentials for {website} saved!")
            self.website_entry.delete(0, tb.END)
            self.username_entry.delete(0, tb.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def view_saved_credentials(self):
        if not os.path.exists("data.json"):
            messagebox.showinfo("No Data", "No credentials saved yet.")
            return

        try:
            with open("data.json", "r") as file:
                data = json.load(file)

            view_win = tb.Toplevel(self.root)
            view_win.title("Saved Credentials")
            view_win.geometry("400x400")
            text_area = tb.ScrolledText(view_win, wrap="word", width=50, height=20)
            text_area.pack(padx=10, pady=10, fill=BOTH, expand=True)

            for site, creds in data.items():
                entry = f"Website: {site}\nEmail: {creds['email']}\nPassword: {creds['password']}\n{'-'*40}\n"
                text_area.insert(END, entry)

            text_area.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = PasswordGeneratorApp(root)
    root.mainloop()
