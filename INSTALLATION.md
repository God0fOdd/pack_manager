# Installation and Configuration (Windows)

## 1) Install Python

- Install Python 3.11+ from https://www.python.org/downloads/
- During setup, enable **Add Python to PATH**.

## 2) Install dependencies

Open **PowerShell** in the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

If `face-recognition` fails to install, install Visual C++ Build Tools and CMake.
Face unlock is optional, so you can still run the app without it.

## 3) Run the app

```powershell
python app.py
```

## 4) First-time configuration

1. Create a master account.
2. Choose your custom salt.
3. Log in and start saving entries.
4. (Optional) Enroll face unlock profile.
5. (Optional) Export `.env` key pack from **Security tools** tab.

## 5) Build `.exe` file

```powershell
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name LocalPasswordManager app.py
```

Generated executable:

- `dist\LocalPasswordManager.exe`

## 6) Distribution checklist

- Share only the `.exe` and user guide.
- Do **not** share your local vault or exported key pack files.
- Recommend users backup `%USERPROFILE%\.local_password_manager\` securely.
