# core/favorite_manager.py
import sqlite3

def toggle_favorite(game_id):
    conn = sqlite3.connect("database/multiverse.db")
    cursor = conn.cursor()
    cursor.execute("SELECT is_favorite FROM games WHERE id = ?", (game_id,))
    current = cursor.fetchone()
    if current is None:
        return False
    new_state = not bool(current[0])
    cursor.execute("UPDATE games SET is_favorite = ? WHERE id = ?", (int(new_state), game_id))
    conn.commit()
    conn.close()
    return new_state

def is_favorite(game_id):
    conn = sqlite3.connect("database/multiverse.db")
    cursor = conn.cursor()
    cursor.execute("SELECT is_favorite FROM games WHERE id = ?", (game_id,))
    result = cursor.fetchone()
    conn.close()
    return bool(result[0]) if result else False