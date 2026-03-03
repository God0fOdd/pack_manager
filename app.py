from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from face_unlock import capture_face_encoding, dependencies_available, verify_face
from security_tools import generate_password
from steganography_audio import embed_secret_in_wav, extract_secret_from_wav
from vault import VaultManager


class PasswordManagerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Local Password Manager")
        self.root.geometry("900x650")

        self.vault: VaultManager | None = None
        self.generated_password = tk.StringVar(value="")

        self.container = ttk.Frame(root, padding=16)
        self.container.pack(fill=tk.BOTH, expand=True)

        if VaultManager.app_initialized():
            self.show_login()
        else:
            self.show_setup()

    def clear(self):
        for child in self.container.winfo_children():
            child.destroy()

    def show_setup(self):
        self.clear()
        ttk.Label(self.container, text="Create Master Account", font=("Segoe UI", 16, "bold")).pack(anchor="w")

        master = tk.StringVar()
        confirm = tk.StringVar()
        user_salt = tk.StringVar()

        form = ttk.Frame(self.container, padding=(0, 16))
        form.pack(fill=tk.X)

        ttk.Label(form, text="Master password").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=master, show="*").grid(row=0, column=1, sticky="ew", padx=8)

        ttk.Label(form, text="Confirm password").grid(row=1, column=0, sticky="w")
        ttk.Entry(form, textvariable=confirm, show="*").grid(row=1, column=1, sticky="ew", padx=8)

        ttk.Label(form, text="User salt (custom)").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=user_salt).grid(row=2, column=1, sticky="ew", padx=8)

        form.columnconfigure(1, weight=1)

        def create_master():
            if not master.get() or not user_salt.get():
                messagebox.showerror("Missing", "Master password and salt are required.")
                return
            if master.get() != confirm.get():
                messagebox.showerror("Mismatch", "Passwords do not match.")
                return
            VaultManager.init_master(master.get(), user_salt.get())
            messagebox.showinfo("Done", "Master account created.")
            self.show_login()

        ttk.Button(self.container, text="Create account", command=create_master).pack(anchor="w")

    def show_login(self):
        self.clear()
        ttk.Label(self.container, text="Unlock Vault", font=("Segoe UI", 16, "bold")).pack(anchor="w")

        master = tk.StringVar()
        use_face = tk.BooleanVar(value=False)

        form = ttk.Frame(self.container, padding=(0, 16))
        form.pack(fill=tk.X)

        ttk.Label(form, text="Master password").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=master, show="*").grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Checkbutton(form, text="Require face verification", variable=use_face).grid(row=1, column=0, columnspan=2, sticky="w")
        form.columnconfigure(1, weight=1)

        def unlock():
            valid, user_salt = VaultManager.validate_master(master.get())
            if not valid:
                messagebox.showerror("Error", "Invalid master password.")
                return
            self.vault = VaultManager(master.get(), user_salt)
            if use_face.get():
                blob = self.vault.load_face_profile()
                if not blob:
                    messagebox.showerror("Face", "No face profile enrolled.")
                    return
                if not dependencies_available():
                    messagebox.showerror("Face", "Install face-recognition and opencv-python first.")
                    return
                try:
                    if not verify_face(blob):
                        messagebox.showerror("Face", "Face verification failed.")
                        return
                except Exception as exc:
                    messagebox.showerror("Face", str(exc))
                    return
            self.show_main()

        ttk.Button(self.container, text="Unlock", command=unlock).pack(anchor="w")

    def show_main(self):
        self.clear()
        notebook = ttk.Notebook(self.container)
        notebook.pack(fill=tk.BOTH, expand=True)

        vault_tab = ttk.Frame(notebook, padding=12)
        generator_tab = ttk.Frame(notebook, padding=12)
        tools_tab = ttk.Frame(notebook, padding=12)

        notebook.add(vault_tab, text="Vault")
        notebook.add(generator_tab, text="Generator")
        notebook.add(tools_tab, text="Security tools")

        self.build_vault_tab(vault_tab)
        self.build_generator_tab(generator_tab)
        self.build_tools_tab(tools_tab)

    def build_vault_tab(self, parent: ttk.Frame):
        profile = tk.StringVar()
        name = tk.StringVar()
        password = tk.StringVar()
        description = tk.StringVar()

        fields = ttk.Frame(parent)
        fields.pack(fill=tk.X)
        ttk.Label(fields, text="Profile").grid(row=0, column=0, sticky="w")
        ttk.Entry(fields, textvariable=profile).grid(row=0, column=1, sticky="ew", padx=6)

        ttk.Label(fields, text="Name").grid(row=1, column=0, sticky="w")
        ttk.Entry(fields, textvariable=name).grid(row=1, column=1, sticky="ew", padx=6)

        ttk.Label(fields, text="Description").grid(row=2, column=0, sticky="w")
        ttk.Entry(fields, textvariable=description).grid(row=2, column=1, sticky="ew", padx=6)

        ttk.Label(fields, text="Password").grid(row=3, column=0, sticky="w")
        ttk.Entry(fields, textvariable=password).grid(row=3, column=1, sticky="ew", padx=6)

        fields.columnconfigure(1, weight=1)

        columns = ("profile", "name", "description", "password", "updated_at")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=16)
        for col in columns:
            tree.heading(col, text=col.title())
            tree.column(col, width=150 if col != "description" else 250)
        tree.pack(fill=tk.BOTH, expand=True, pady=12)

        def refresh():
            for i in tree.get_children():
                tree.delete(i)
            entries = self.vault.read_entries() if self.vault else []
            for e in entries:
                tree.insert("", tk.END, values=(e.profile, e.name, e.description, e.password, e.updated_at))

        def save_entry():
            if not self.vault:
                return
            if not profile.get() or not name.get() or not password.get():
                messagebox.showerror("Missing", "Profile, name and password are required.")
                return
            self.vault.upsert_entry(profile.get(), name.get(), description.get(), password.get())
            refresh()
            messagebox.showinfo("Saved", "Entry stored in encrypted vault.")

        ttk.Button(parent, text="Save / Update", command=save_entry).pack(anchor="w")
        ttk.Button(parent, text="Refresh", command=refresh).pack(anchor="w", pady=4)
        refresh()

    def build_generator_tab(self, parent: ttk.Frame):
        length = tk.IntVar(value=18)
        salt = tk.StringVar()
        seed = tk.StringVar()

        upper = tk.BooleanVar(value=True)
        lower = tk.BooleanVar(value=True)
        digits = tk.BooleanVar(value=True)
        symbols = tk.BooleanVar(value=True)

        ttk.Label(parent, text="Password generator", font=("Segoe UI", 13, "bold")).pack(anchor="w")

        grid = ttk.Frame(parent)
        grid.pack(fill=tk.X, pady=8)

        ttk.Label(grid, text="Length").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(grid, from_=8, to=128, textvariable=length, width=8).grid(row=0, column=1, sticky="w")

        ttk.Label(grid, text="Salt").grid(row=1, column=0, sticky="w")
        ttk.Entry(grid, textvariable=salt).grid(row=1, column=1, sticky="ew")

        ttk.Label(grid, text="Deterministic seed (optional)").grid(row=2, column=0, sticky="w")
        ttk.Entry(grid, textvariable=seed).grid(row=2, column=1, sticky="ew")

        ttk.Checkbutton(grid, text="Upper", variable=upper).grid(row=3, column=0, sticky="w")
        ttk.Checkbutton(grid, text="Lower", variable=lower).grid(row=3, column=1, sticky="w")
        ttk.Checkbutton(grid, text="Digits", variable=digits).grid(row=4, column=0, sticky="w")
        ttk.Checkbutton(grid, text="Symbols", variable=symbols).grid(row=4, column=1, sticky="w")
        grid.columnconfigure(1, weight=1)

        ttk.Entry(parent, textvariable=self.generated_password).pack(fill=tk.X, pady=8)

        def do_generate():
            try:
                value = generate_password(
                    length=length.get(),
                    use_upper=upper.get(),
                    use_lower=lower.get(),
                    use_digits=digits.get(),
                    use_symbols=symbols.get(),
                    salt=salt.get(),
                    deterministic_seed=seed.get(),
                )
                self.generated_password.set(value)
            except Exception as exc:
                messagebox.showerror("Generator", str(exc))

        ttk.Button(parent, text="Generate", command=do_generate).pack(anchor="w")

    def build_tools_tab(self, parent: ttk.Frame):
        ttk.Label(parent, text="Security tools", font=("Segoe UI", 13, "bold")).pack(anchor="w")

        def export_keypack():
            if not self.vault:
                return
            out = filedialog.asksaveasfilename(defaultextension=".env", filetypes=[("Env", "*.env"), ("All", "*.*")])
            if not out:
                return
            self.vault.export_env(out)
            messagebox.showinfo("Exported", "Key pack exported. Keep this file private.")

        def enroll_face():
            if not self.vault:
                return
            if not dependencies_available():
                messagebox.showerror("Face", "Install face-recognition and opencv-python first.")
                return
            try:
                blob = capture_face_encoding()
                self.vault.save_face_profile(blob)
                messagebox.showinfo("Face", "Face profile enrolled.")
            except Exception as exc:
                messagebox.showerror("Face", str(exc))

        secret_var = tk.StringVar()

        def embed_audio():
            secret = secret_var.get().strip()
            if not secret:
                messagebox.showerror("Audio", "Enter secret text first.")
                return
            in_file = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
            if not in_file:
                return
            out_file = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")])
            if not out_file:
                return
            try:
                embed_secret_in_wav(in_file, out_file, secret)
                messagebox.showinfo("Audio", "Secret embedded in WAV file.")
            except Exception as exc:
                messagebox.showerror("Audio", str(exc))

        def extract_audio():
            in_file = filedialog.askopenfilename(filetypes=[("WAV", "*.wav")])
            if not in_file:
                return
            try:
                text = extract_secret_from_wav(in_file)
                messagebox.showinfo("Audio secret", text)
            except Exception as exc:
                messagebox.showerror("Audio", str(exc))

        ttk.Button(parent, text="Export decryption key pack (.env)", command=export_keypack).pack(anchor="w", pady=6)
        ttk.Button(parent, text="Enroll face unlock profile", command=enroll_face).pack(anchor="w", pady=6)

        ttk.Label(parent, text="Secret text for WAV steganography").pack(anchor="w", pady=(16, 0))
        ttk.Entry(parent, textvariable=secret_var).pack(fill=tk.X)
        ttk.Button(parent, text="Embed secret into WAV", command=embed_audio).pack(anchor="w", pady=6)
        ttk.Button(parent, text="Extract secret from WAV", command=extract_audio).pack(anchor="w", pady=6)


def main():
    root = tk.Tk()
    style = ttk.Style()
    if "vista" in style.theme_names():
        style.theme_use("vista")
    app = PasswordManagerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
