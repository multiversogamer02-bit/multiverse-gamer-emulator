# core/emulator_manager.py
import subprocess
import os
import sqlite3
from pathlib import Path

EMULATOR_COMMANDS = {
    "PS1": ["{emulator}", "{rom}"],      # DuckStation: .cue o .m3u
    "PS2": ["{emulator}", "{rom}"],      # PCSX2: ya configurado
    "PS3": ["{emulator}", "{rom}"],      # RPCS3: carpeta PS3_GAME
    "Xbox 360": ["{emulator}", "{rom}"], # Xenia
    "Wii": ["{emulator}", "-e", "{rom}"],# Dolphin
    "WiiU": ["{emulator}", "-g", "{rom}"],# Cemu: carpeta del juego
    "Switch": ["{emulator}", "-g", "{rom}"],# Yuzu
    "NES": ["{emulator}", "{rom}"]       # Mesen
}

def launch_game(game_id):
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
        return True
    except:
        return False