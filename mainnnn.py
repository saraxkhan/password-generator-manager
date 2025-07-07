import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
import pyperclip
import random
import json
import os

SIMILAR_CHARS = "Il1O0"
AMBIGUOUS_CHARS = '{}[]()/\\"\'`~,;:.<>'

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
        new_pool = ""
        for char in char_pool:
            if char not in SIMILAR_CHARS:
                new_pool += char
        char_pool = new_pool

    if exclude_ambiguous:
        new_pool = ""
        for char in char_pool:
            if char not in AMBIGUOUS_CHARS:
                new_pool += char
        char_pool = new_pool

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
            view_win.geometry("500x450")

            for site, creds in data.items():
                frame = tb.Frame(view_win)
                frame.pack(fill=X, pady=5, padx=10)

                tb.Label(frame, text=f"{site}", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=W)
                tb.Label(frame, text=f"Email: {creds['email']}").grid(row=1, column=0, sticky=W)
                tb.Label(frame, text=f"Password: {creds['password']}").grid(row=2, column=0, sticky=W)

                tb.Button(frame, text="Edit", bootstyle="warning-outline", width=8,
                          command=lambda s=site: self.edit_entry(s)).grid(row=0, column=1, rowspan=3, padx=5)

                tb.Button(frame, text="Delete", bootstyle="danger-outline", width=8,
                          command=lambda s=site: self.delete_entry(s)).grid(row=0, column=2, rowspan=3)

                tb.Separator(view_win, bootstyle="secondary").pack(fill=X, padx=10, pady=5)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def edit_entry(self, site):
        with open("data.json", "r") as file:
            data = json.load(file)

        creds = data.get(site, {})
        if not creds:
            return

        edit_win = tb.Toplevel(self.root)
        edit_win.title(f"Edit: {site}")

        tb.Label(edit_win, text="Email/Username:").pack()
        email_entry = tb.Entry(edit_win, width=40)
        email_entry.insert(0, creds["email"])
        email_entry.pack(pady=(0, 10))

        tb.Label(edit_win, text="Password:").pack()
        pass_entry = tb.Entry(edit_win, width=40)
        pass_entry.insert(0, creds["password"])
        pass_entry.pack(pady=(0, 10))

        def save_changes():
            data[site] = {
                "email": email_entry.get(),
                "password": pass_entry.get()
            }
            with open("data.json", "w") as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Updated", f"Credentials for {site} updated!")
            edit_win.destroy()

        tb.Button(edit_win, text="Save Changes", command=save_changes, bootstyle="primary").pack(pady=10)

    def delete_entry(self, site):
        confirm = messagebox.askyesno("Delete", f"Are you sure you want to delete credentials for {site}?")
        if confirm:
            with open("data.json", "r") as file:
                data = json.load(file)

            if site in data:
                del data[site]
                with open("data.json", "w") as file:
                    json.dump(data, file, indent=4)
                messagebox.showinfo("Deleted", f"Credentials for {site} deleted!")

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = PasswordGeneratorApp(root)
    root.mainloop()