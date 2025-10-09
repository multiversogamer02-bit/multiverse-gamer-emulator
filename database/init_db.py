# database/init_db.py
import sqlite3
import os

DB_PATH = "database/multiverse.db"

def init_database():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tablas existentes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS consoles (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            emulator_path TEXT,
            roms_path TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY,
            title TEXT,
            path TEXT,
            console_id INTEGER,
            cover_path TEXT,
            is_favorite BOOLEAN DEFAULT 0,
            graphics_profile TEXT DEFAULT '{}',
            FOREIGN KEY(console_id) REFERENCES consoles(id)
        )
    """)

    # NUEVA TABLA para guardar el ID de la suscripción
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_subscription (
            id INTEGER PRIMARY KEY,
            mp_subscription_id TEXT UNIQUE,
            user_email TEXT,
            plan TEXT,
            status TEXT DEFAULT 'active',
            start_date TIMESTAMP,
            end_date TIMESTAMP
        )
    """)

    # Tabla existente de estadísticas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_stats (
            game_id INTEGER PRIMARY KEY,
            play_count INTEGER DEFAULT 0,
            total_time INTEGER DEFAULT 0,
            last_played TIMESTAMP
        )
    """)

    # Datos iniciales de consolas
    consoles = [
        ("PS1", "", ""),
        ("PS2", "", ""),
        ("PS3", "", ""),
        ("Xbox 360", "", ""),
        ("Wii", "", ""),
        ("WiiU", "", ""),
        ("Switch", "", ""),
        ("NES", "", "")
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO consoles (name, emulator_path, roms_path) VALUES (?, ?, ?)",
        consoles
    )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()