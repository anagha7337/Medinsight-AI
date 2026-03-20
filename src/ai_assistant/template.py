import os
from pathlib import Path 
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

# Go to project root (2 levels up from src/ai_assistant/)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

list_of_files = [
    # Root files
    ROOT_DIR / "app.py",
    ROOT_DIR / "requirements.txt",
    ROOT_DIR / ".env",
    ROOT_DIR / ".gitignore",

    # AI Assistant module (current folder)
    ROOT_DIR / "src/ai_assistant/__init__.py",
    ROOT_DIR / "src/ai_assistant/helper.py",
    ROOT_DIR / "src/ai_assistant/prompt.py",

    # Report Analyzer module
    ROOT_DIR / "src/report_analyzer/__init__.py",
    ROOT_DIR / "src/report_analyzer/ocr_utils.py",
    ROOT_DIR / "src/report_analyzer/report_parser.py",
    ROOT_DIR / "src/report_analyzer/range_checker.py",
    ROOT_DIR / "src/report_analyzer/ai_interpreter.py",
    ROOT_DIR / "src/report_analyzer/scan_interpreter.py",

    # Database module (optional)
    ROOT_DIR / "src/database/__init__.py",
    ROOT_DIR / "src/database/db.py",

    # Templates
    ROOT_DIR / "templates/index.html",
    ROOT_DIR / "templates/dashboard.html",
    ROOT_DIR / "templates/report_analyzer.html",
    ROOT_DIR / "templates/scan_analyzer.html",
    ROOT_DIR / "templates/medicine_lookup.html",
    ROOT_DIR / "templates/ai_assistant.html",

    # Static files
    ROOT_DIR / "static/css/style.css",
    ROOT_DIR / "static/js/main.js",
    ROOT_DIR / "static/js/chatbot.js",

    # Uploads
    ROOT_DIR / "uploads/.gitkeep",

    # RAG script
    ROOT_DIR / "store_index.py"
]

for filepath in list_of_files:
    filedir = filepath.parent
    filename = filepath.name

    if not filedir.exists():
        filedir.mkdir(parents=True, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file: {filename}")

    if (not filepath.exists()) or (filepath.stat().st_size == 0):
        with open(filepath, "w") as f:
            pass
        logging.info(f"Creating empty file: {filepath}")

    else:
        logging.info(f"{filename} already exists")