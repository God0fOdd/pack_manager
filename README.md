# Local Password Manager (Windows-first)

A local-first password manager written in Python with these features:

- Master account with custom user-selected salt.
- Encrypted vault storage (Fernet + PBKDF2 key derivation).
- Password generator (random or deterministic with salt/seed).
- Profile-based entries (`profile`, `name`, `description`, `password`).
- Export `.env` style key pack for controlled decryption workflows.
- Optional face unlock (if `opencv-python` and `face-recognition` are installed).
- Audio steganography module (embed/extract secret text in `.wav`).
- Packaged into `.exe` using PyInstaller.

## Project files

- `app.py` — Tkinter GUI application.
- `vault.py` — master account + encrypted vault storage logic.
- `security_tools.py` — password generation.
- `face_unlock.py` — optional camera face enrollment/verification.
- `steganography_audio.py` — WAV steganography utilities.
- `INSTALLATION.md` — setup and build instructions.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Notes

- Vault files are saved under: `~/.local_password_manager/`.
- Face unlock is optional and only enabled when dependencies are available.
- Protect exported key packs (`.env`) as sensitive secrets.
