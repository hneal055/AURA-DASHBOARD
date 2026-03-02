import os
from pathlib import Path
import shutil

# Determine project root (two directories above this file)
ROOT = Path(__file__).resolve().parent.parent

# Folder structure to create
FOLDERS = [
    "app",
    "data/uploads",
    "data/samples",
    "logs",
    "static/css",
    "static/js",
    "templates",
    "tests"
]

# Files to create or ensure exist
FILES_TO_CREATE = {
    "app/__init__.py": "",
    "app/parser_core.py": (
        "def process_input(text):\n"
        "    return {'original': text, 'processed': text.upper()}\n"
    ),
    "app/utils.py": (
        "def safe_print(msg):\n"
        "    print(f'[UTIL] {msg}')\n"
    ),
    "templates/index.html": "<h1>Production Parser Running</h1>",
    "run_server.py": (
        "from app.web_app import app\n\n"
        "if __name__ == '__main__':\n"
        "    app.run(debug=True, host='0.0.0.0', port=5000)\n"
    ),
    "requirements.txt": "Flask==3.0.0\n",
}


def ensure_folders():
    for folder in FOLDERS:
        path = ROOT / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"[OK] Folder ensured: {path}")


def move_web_app():
    old_path = ROOT / "web_app.py"
    new_path = ROOT / "app" / "web_app.py"

    if old_path.exists():
        shutil.move(str(old_path), str(new_path))
        print("[OK] Moved web_app.py to app/")
    else:
        print("[WARN] web_app.py not found in project root.")


def create_files():
    for rel_path, content in FILES_TO_CREATE.items():
        file_path = ROOT / rel_path

        if not file_path.exists():
            file_path.write_text(content, encoding="utf-8")
            print(f"[OK] Created: {file_path}")
        else:
            print(f"[SKIP] Exists: {file_path}")


def main():
    print("\n--- Organizing Production-Parser Project ---\n")
    ensure_folders()
    move_web_app()
    create_files()
    print("\n--- Project structure is now Flask-ready! ---\n")


if __name__ == "__main__":
    main()
