import tkinter as tk
from tkinter import messagebox
import pyperclip
from tkinter import ttk
from unicodedata import category

from main import generate_password  # import from step 2 file
def get_strength_level(password):
    length=len(password)
    categories = 0

    if any(c.islower() for c in password):
        categories += 1
    if any(c.isupper() for c in password):
        categories += 1
    if any(c.isdigit() for c in password):
        categories += 1
    if any(c in "!@#$^&*()-_<>?/" for c in password):
        categories += 1

    #scoring logic
    if length >= 12 and categories >= 3:
        return "Strong", "green"
    elif length >= 8 and categories >= 2:
        return "Medium", "orange"
    else:
        return "Weak", "red"

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("400x400")
        self.root.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):
        # Password Length
        ttk.Label(self.root, text="Password Length:").pack(pady=(10, 0))
        self.length_entry = ttk.Entry(self.root, width=10)
        self.length_entry.pack(pady=(0, 10))
        self.length_entry.insert(0, "12")

        # Checkboxes for options
        self.use_lower = tk.BooleanVar(value=True)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_similar = tk.BooleanVar()
        self.exclude_ambiguous = tk.BooleanVar()

        options = [
            ("Include Lowercase", self.use_lower),
            ("Include Uppercase", self.use_upper),
            ("Include Numbers", self.use_digits),
            ("Include Symbols", self.use_symbols),
            ("Exclude Similar Characters", self.exclude_similar),
            ("Exclude Ambiguous Characters", self.exclude_ambiguous),
        ]

        for label, var in options:
            ttk.Checkbutton(self.root, text=label, variable=var).pack(anchor="w", padx=20)

        # Generate button
        ttk.Button(self.root, text="Generate Password", command=self.generate).pack(pady=10)

        # Display password
        self.output = ttk.Entry(self.root, width=35, justify="center")
        self.output.pack(pady=10)

        # Copy button
        ttk.Button(self.root, text="Copy to Clipboard", command=self.copy_to_clipboard).pack()

        #Strength indicator
        self.strength_label = tk.Label(self.root, text="", font=("Arial", 10, "bold"))
        self.strength_label.pack()


    def generate(self):

        try:
            length = int(self.length_entry.get())
            password = generate_password(
                length = length,
                use_lower=self.use_lower.get(),
                use_upper=self.use_upper.get(),
                use_digits=self.use_digits.get(),
                use_symbols=self.use_symbols.get(),
                exclude_similar=self.exclude_similar.get(),
                exclude_ambiguous=self.exclude_ambiguous.get()
            )
            self.output.delete(0, tk.END)
            self.output.insert(0,password)
        except Exception as e:
            messagebox.showerror("Error", str(e))

        strength, color = get_strength_level(password)
        self.strength_label.config(text=f"Strength: {strength}", fg=color)


    def copy_to_clipboard(self):
        password = self.output.get()
        if password:
            pyperclip.copy(password)
            messagebox.showinfo("Copied", "Password copied to clipboard!")

        else:
            messagebox.showwarning("Empty","No password to copy.")

# Launch app
if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()



