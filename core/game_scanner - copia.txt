# core/game_scanner.py
import os
import sqlite3
from pathlib import Path
import re

def extract_base_name(filename: str) -> str:
    name = Path(filename).stem
    name = re.sub(r"\s*\([^)]*\)", "", name)
    name = re.sub(r"\s*\[.*?\]", "", name)
    return name.strip() or filename

def scan_games():
    conn = sqlite3.connect("database/multiverse.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, roms_path FROM consoles")
    consoles = cursor.fetchall()

    for console_id, name, roms_path in consoles:
        if not roms_path or not os.path.exists(roms_path):
            cursor.execute("DELETE FROM games WHERE console_id = ?", (console_id,))
            continue

        cursor.execute("DELETE FROM games WHERE console_id = ?", (console_id,))
        games_to_add = []
        roms_path_obj = Path(roms_path)

        # === PS1: escanear subcarpetas, usar nombre de carpeta ===
        if name == "PS1":
            for item in roms_path_obj.iterdir():
                if item.is_dir():
                    # Buscar .m3u primero
                    m3u_files = list(item.glob("*.m3u"))
                    if m3u_files:
                        for m3u in m3u_files:
                            games_to_add.append((item.name, str(m3u), console_id, None, False))
                        continue
                    # Si no hay .m3u, buscar .cue
                    cue_files = list(item.glob("*.cue"))
                    if cue_files:
                        games_to_add.append((item.name, str(cue_files[0]), console_id, None, False))

        # === PS2: solo .iso en raíz ===
        elif name == "PS2":
            for file in roms_path_obj.iterdir():
                if file.is_file() and file.suffix.lower() == ".iso":
                    games_to_add.append((file.stem, str(file), console_id, None, False))

        # === Wii: .iso, .wbfs, .rvz en raíz ===
        elif name == "Wii":
            for file in roms_path_obj.iterdir():
                if file.is_file() and file.suffix.lower() in (".iso", ".wbfs", ".rvz"):
                    games_to_add.append((file.stem, str(file), console_id, None, False))

        # === WiiU: carpetas con /code ===
        elif name == "WiiU":
            for folder in roms_path_obj.iterdir():
                if folder.is_dir() and (folder / "code").exists():
                    games_to_add.append((folder.name, str(folder), console_id, None, False))

        # === Switch: .nsp/.xci en raíz ===
        elif name == "Switch":
            for file in roms_path_obj.iterdir():
                if file.is_file() and file.suffix.lower() in (".nsp", ".xci"):
                    games_to_add.append((file.stem, str(file), console_id, None, False))

        # === PS3: carpetas con /PS3_GAME ===
        elif name == "PS3":
            for folder in roms_path_obj.iterdir():
                if folder.is_dir() and (folder / "PS3_GAME").exists():
                    games_to_add.append((folder.name, str(folder / "PS3_GAME"), console_id, None, False))

        # === Xbox 360 y NES: mantener como antes ===
        elif name == "Xbox 360":
            for ext in (".iso", ".xex"):
                for file in roms_path_obj.rglob(f"*{ext}"):
                    if file.is_file():
                        games_to_add.append((file.parent.name, str(file), console_id, None, False))
        elif name == "NES":
            for file in roms_path_obj.iterdir():
                if file.is_file() and file.suffix.lower() == ".nes":
                    games_to_add.append((file.stem, str(file), console_id, None, False))

        # Insertar
        if games_to_add:
            cursor.executemany(
                "INSERT INTO games (title, path, console_id, cover_path, is_favorite) VALUES (?, ?, ?, ?, ?)",
                games_to_add
            )

    conn.commit()
    conn.close()
def generate_m3u_for_ps1(roms_path: str):
    """Genera archivos .m3u DENTRO de cada carpeta de juego multidisco, usando el nombre de la carpeta."""
    if not os.path.exists(roms_path):
        return

    roms_path_obj = Path(roms_path)
    
    # Recorrer cada subcarpeta (cada juego)
    for game_folder in roms_path_obj.iterdir():
        if not game_folder.is_dir():
            continue

        # Buscar archivos .cue en la carpeta
        cue_files = list(game_folder.glob("*.cue"))
        if len(cue_files) <= 1:
            continue  # Solo un disco → no necesita .m3u

        # ✅ Usar el NOMBRE DE LA CARPETA como nombre del .m3u
        m3u_name = game_folder.name + ".m3u"
        m3u_path = game_folder / m3u_name

        # Solo generar si no existe
        if not m3u_path.exists():
            try:
                with open(m3u_path, "w", encoding="utf-8") as f:
                    for cue in sorted(cue_files):
                        # Ruta relativa al .m3u (solo el nombre del archivo)
                        f.write(cue.name + "\n")
                print(f"✅ Generado .m3u: {m3u_path}")
            except Exception as e:
                print(f"❌ Error al crear {m3u_path}: {e}")