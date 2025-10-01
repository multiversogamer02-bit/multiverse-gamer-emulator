# utils/cover_finder.py
import os
from pathlib import Path

def find_cover(game_path: str, console_name: str) -> str:
    """
    Busca una carátula para el juego.
    - Para PS1, PS3, WiiU: busca en la carpeta del juego.
    - Para otros: busca en la misma carpeta que el archivo.
    """
    game_path = Path(game_path)
    
    # Definir dónde buscar según la consola
    if console_name in ("PS1", "PS3", "WiiU"):
        # game_path es una carpeta → buscar dentro
        search_dir = game_path if game_path.is_dir() else game_path.parent
    else:
        # game_path es un archivo → buscar en su carpeta
        search_dir = game_path.parent

    if not search_dir.exists():
        return ""

    # Extensiones comunes de carátulas
    cover_names = ["cover", "boxart", "front", "fanart"]
    cover_exts = [".png", ".jpg", ".jpeg", ".webp"]

    for name in cover_names:
        for ext in cover_exts:
            cover_path = search_dir / (name + ext)
            if cover_path.exists():
                return str(cover_path)

    return ""