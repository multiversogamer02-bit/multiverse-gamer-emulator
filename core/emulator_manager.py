# core/emulator_manager.py
import subprocess
import os
import sqlite3
from pathlib import Path
import time
import threading
from datetime import datetime

EMULATOR_COMMANDS = {
    "PS1": ["{emulator}", "{rom}"],
    "PS2": ["{emulator}", "{rom}"],
    "PS3": ["{emulator}", "{rom}"],
    "Xbox 360": ["{emulator}", "{rom}"],
    "Wii": ["{emulator}", "-e", "{rom}"],
    "WiiU": ["{emulator}", "-g", "{rom}"],
    "Switch": ["{emulator}", "-g", "{rom}"],
    "NES": ["{emulator}", "{rom}"]
}

_game_start_time = None
_current_game_id = None

def launch_game(game_id):
    global _game_start_time, _current_game_id
    conn = sqlite3.connect("database/multiverse.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT g.path, c.name, c.emulator_path
        FROM games g
        JOIN consoles c ON g.console_id = c.id
        WHERE g.id = ?
    """, (game_id,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return False
    rom_path, console_name, emulator_path = result
    if not emulator_path or not os.path.exists(emulator_path) or not os.path.exists(rom_path):
        return False
    cmd_template = EMULATOR_COMMANDS.get(console_name, ["{emulator}", "{rom}"])
    cmd = [part.format(emulator=emulator_path, rom=rom_path) for part in cmd_template]
    try:
        subprocess.Popen(cmd, cwd=Path(emulator_path).parent)
        _game_start_time = time.time()
        _current_game_id = game_id
        threading.Thread(target=_monitor_game, args=(game_id,), daemon=True).start()
        return True
    except:
        return False

def _monitor_game(game_id):
    """Registra estadísticas cuando el juego termina."""
    global _game_start_time, _current_game_id
    try:
        time.sleep(10)
        if _current_game_id == game_id and _game_start_time:
            duration = int(time.time() - _game_start_time)
            _save_game_stats(game_id, duration)
            _game_start_time = None
            _current_game_id = None
    except Exception as e:
        print(f"Error al registrar estadísticas: {e}")

def _save_game_stats(game_id, duration):
    """Guarda las estadísticas en la base de datos local."""
    conn = sqlite3.connect("database/multiverse.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_stats (
        game_id INTEGER PRIMARY KEY,
        play_count INTEGER DEFAULT 0,
        total_time INTEGER DEFAULT 0,
        last_played TIMESTAMP
    )""")
    cursor.execute("""
        INSERT INTO game_stats (game_id, play_count, total_time, last_played)
        VALUES (?, 1, ?, ?)
        ON CONFLICT(game_id) DO UPDATE SET
            play_count = play_count + 1,
            total_time = total_time + ?,
            last_played = ?
    """, (game_id, duration, datetime.now(), duration, datetime.now()))
    conn.commit()
    conn.close()