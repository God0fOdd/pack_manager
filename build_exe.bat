@echo off
python -m venv .venv
call .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name LocalPasswordManager app.py
echo Build complete. Output: dist\LocalPasswordManager.exe
