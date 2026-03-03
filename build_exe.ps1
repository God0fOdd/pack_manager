python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name LocalPasswordManager app.py
Write-Host "Build complete. Output: dist\\LocalPasswordManager.exe"
