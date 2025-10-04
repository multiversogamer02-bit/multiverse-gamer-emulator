# ui/stats_window.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
import sqlite3

class StatsWindow(QDialog):
    def __init__(self, parent=None, lang="es"):
        super().__init__(parent)
        self.lang = lang
        self.translations = {
            "es": {"title": "📊 Estadísticas", "games_played": "Juegos más jugados", "total_hours": "Horas totales"},
            "en": {"title": "📊 Statistics", "games_played": "Most Played Games", "total_hours": "Total Hours"}
        }
        self.setWindowTitle(self.translations[self.lang]["title"])
        self.setFixedSize(600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(self.translations[self.lang]["games_played"] + ":"))
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            self.translations[self.lang]["games_played"],
            "Veces jugado",
            self.translations[self.lang]["total_hours"]
        ])
        layout.addWidget(self.table)
        self.load_stats()

    def load_stats(self):
        try:
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
                SELECT g.title, s.play_count, s.total_time
                FROM game_stats s
                JOIN games g ON s.game_id = g.id
                ORDER BY s.total_time DESC
                LIMIT 10
            """)
            stats = cursor.fetchall()
            conn.close()
            self.table.setRowCount(len(stats))
            for row, (title, count, seconds) in enumerate(stats):
                hours = seconds // 3600
                self.table.setItem(row, 0, QTableWidgetItem(title))
                self.table.setItem(row, 1, QTableWidgetItem(str(count)))
                self.table.setItem(row, 2, QTableWidgetItem(str(hours)))
        except Exception as e:
            print(f"Error al cargar estadísticas: {e}")
            self.table.setRowCount(0)