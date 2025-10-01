# core/streaming_manager.py
import subprocess
from pathlib import Path

def start_sunshine():
    sunshine_path = "C:/Sunshine/sunshine.exe"
    if Path(sunshine_path).exists():
        subprocess.Popen([sunshine_path], cwd=Path(sunshine_path).parent)