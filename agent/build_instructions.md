# Build the Agent EXE (Windows)

1. Install Python 3.11+ and Git.
2. Create venv and install requirements:
   ```bash
   python -m venv .venv
   . .venv\Scripts\activate
   pip install -r ..\requirements.txt
   pip install pyinstaller
   ```
3. Build:
   ```bash
   pyinstaller --onefile agent.py
   ```
4. Distribute `dist\agent.exe` with `config.ini` in the same folder.
