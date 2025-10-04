# ui/main_window.py
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QLabel, QPushButton,
    QScrollArea, QVBoxLayout, QHBoxLayout, QMenuBar, QAction, QMessageBox, 
    QListWidget, QListWidgetItem, QToolButton, QApplication, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from core.game_scanner import scan_games
from ui.settings_window import SettingsWindow
from utils.cover_finder import find_cover
from ui.theme_manager import apply_theme
from utils.gamepad_manager import GamepadManager
from utils.license_manager import is_license_valid
from utils.fps_overlay import FPSOverlay
import sqlite3
import os
import requests

class MultiverseMainWindow(QMainWindow):
    def __init__(self, user_token=None, lang="es"):
        super().__init__()
        self.lang = lang
        self.translations = {
            "es": {
                "app_title": "Multiverse Gamer Emulador",
                "view": "Vista",
                "change_theme": "Cambiar Tema",
                "big_picture": "Modo Big Picture",
                "config": "Configuración",
                "paths_emulators": "Rutas y Emuladores",
                "user": "Usuario",
                "subscribe": "Suscribirse",
                "stats": "Estadísticas",
                "games_played": "Juegos más jugados",
                "total_hours": "Horas totales",
                "no_games": "No se encontraron juegos.\nConfigura las rutas en 'Configuración'.",
                "play": "Jugar",
                "favorites": "Favoritos",
                "graphics": "Gráficos"
            },
            "en": {
                "app_title": "Multiverse Gamer Emulator",
                "view": "View",
                "change_theme": "Change Theme",
                "big_picture": "Big Picture Mode",
                "config": "Configuration",
                "paths_emulators": "Paths and Emulators",
                "user": "User",
                "subscribe": "Subscribe",
                "stats": "Statistics",
                "games_played": "Most Played Games",
                "total_hours": "Total Hours",
                "no_games": "No games found.\nConfigure paths in 'Configuration'.",
                "play": "Play",
                "favorites": "Favorites",
                "graphics": "Graphics"
            }
        }
        self.setWindowTitle(self.translations[self.lang]["app_title"])
        self.resize(1200, 800)
        self.current_console_filter = None
        self.is_big_picture = False
        self.current_theme = "Oscuro"
        self.selected_game_id = None
        self.user_token = user_token
        self.fps_overlay = FPSOverlay(self)

        if not is_license_valid():
            print("⚠️ Licencia no válida, pero continuando en modo prueba.")
        
        self.theme = apply_theme(QApplication.instance(), self.current_theme)
        self.init_ui()
        scan_games()
        self.load_consoles_sidebar()
        self.load_games()
        self.gamepad = GamepadManager()
        self.gamepad.start()

        if self.user_token:
            try:
                response = requests.post(
                    "https://multiverse-server.onrender.com/validate-license",
                    headers={"Authorization": f"Bearer {self.user_token}"},
                    json={"machine_id": "desktop-local"}
                )
                if response.status_code == 200:
                    print("✅ Licencia online válida.")
                else:
                    print("❌ Licencia online inválida o expirada.")
            except Exception as e:
                print(f"⚠️ Error al conectar con el servidor: {e}")

    def tr(self, key):
        return self.translations[self.lang].get(key, key)

    def init_ui(self):
        menubar = self.menuBar()
        view_menu = menubar.addMenu(self.tr("view"))
        theme_action = QAction(self.tr("change_theme"), self)
        theme_action.triggered.connect(self.open_settings)
        view_menu.addAction(theme_action)
        bp_action = QAction(self.tr("big_picture"), self)
        bp_action.setShortcut("Ctrl+B")
        bp_action.triggered.connect(self.toggle_big_picture)
        view_menu.addAction(bp_action)
        
        config_menu = menubar.addMenu(self.tr("config"))
        settings_action = QAction(self.tr("paths_emulators"), self)
        settings_action.triggered.connect(self.open_settings)
        config_menu.addAction(settings_action)
        
        user_menu = menubar.addMenu(self.tr("user"))
        subscribe_action = QAction(self.tr("subscribe"), self)
        subscribe_action.triggered.connect(self.open_subscription)
        user_menu.addAction(subscribe_action)
        
        stats_menu = menubar.addMenu(self.tr("stats"))
        stats_action = QAction(self.tr("stats"), self)
        stats_action.triggered.connect(self.open_stats)
        stats_menu.addAction(stats_action)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.update_sidebar_style()
        self.sidebar.itemClicked.connect(self.on_console_selected)
        main_layout.addWidget(self.sidebar)
        
        right_layout = QVBoxLayout()
        main_layout.addLayout(right_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.grid_widget)
        right_layout.addWidget(scroll)

    def update_sidebar_style(self):
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: {self.theme['main_bg']};
                color: {self.theme['text']};
                border: none;
            }}
            QListWidget::item {{
                padding: 10px;
                font-size: {'20px' if self.is_big_picture else '14px'};
            }}
            QListWidget::item:selected {{
                background-color: {self.theme['accent']};
                color: white;
            }}
        """)

    def toggle_big_picture(self):
        self.is_big_picture = not self.is_big_picture
        if self.is_big_picture:
            self.showFullScreen()
        else:
            self.showNormal()
        self.update_sidebar_style()
        self.load_games()

    def load_consoles_sidebar(self):
        self.sidebar.clear()
        all_item = QListWidgetItem("🎮 " + self.tr("favorites"))
        all_item.setData(Qt.UserRole, None)
        self.sidebar.addItem(all_item)
        
        conn = sqlite3.connect("database/multiverse.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM consoles ORDER BY name")
        consoles = cursor.fetchall()
        conn.close()
        
        for console_id, name in consoles:
            item = QListWidgetItem(f"🕹️ {name}")
            item.setData(Qt.UserRole, console_id)
            self.sidebar.addItem(item)
        self.sidebar.setCurrentRow(0)

    def on_console_selected(self, item):
        console_id = item.data(Qt.UserRole)
        self.current_console_filter = console_id
        self.load_games()

    def load_games(self):
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        conn = sqlite3.connect("database/multiverse.db")
        cursor = conn.cursor()
        if self.current_console_filter is None:
            cursor.execute("""
                SELECT g.id, g.title, c.name, g.is_favorite, g.path
                FROM games g 
                JOIN consoles c ON g.console_id = c.id
            """)
        else:
            cursor.execute("""
                SELECT g.id, g.title, c.name, g.is_favorite, g.path
                FROM games g 
                JOIN consoles c ON g.console_id = c.id
                WHERE c.id = ?
            """, (self.current_console_filter,))
        games = cursor.fetchall()
        conn.close()
        
        if not games:
            placeholder = QLabel(self.tr("no_games"))
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet(f"color: {self.theme['text_secondary']}; font-size: 16px;")
            self.grid_layout.addWidget(placeholder, 0, 0)
        else:
            for i, (game_id, title, console, is_favorite, path) in enumerate(games):
                cover_path = find_cover(path, console)
                card = self.create_game_card(title, console, game_id, bool(is_favorite), cover_path)
                row = i // (2 if self.is_big_picture else 5)
                col = i % (2 if self.is_big_picture else 5)
                self.grid_layout.addWidget(card, row, col)

    def create_game_card(self, title, console, game_id, is_favorite, cover_path):
        card_width = 400 if self.is_big_picture else 200
        card_height = 500 if self.is_big_picture else 300
        card = QWidget()
        card.setFixedSize(card_width, card_height)
        card.setStyleSheet(f"background-color: {self.theme['card_bg']}; border-radius: 10px;")
        card.setFocusPolicy(Qt.StrongFocus)
        card.game_id = game_id
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignTop)
        
        fav_btn = QToolButton()
        fav_btn.setFixedSize(30 if self.is_big_picture else 24, 30 if self.is_big_picture else 24)
        self.update_favorite_icon(fav_btn, is_favorite)
        fav_btn.clicked.connect(lambda _, gid=game_id, btn=fav_btn: self.toggle_favorite(gid, btn))
        layout.addWidget(fav_btn, alignment=Qt.AlignRight)
        
        cover_label = QLabel()
        cover_size = 360 if self.is_big_picture else 180
        cover_label.setFixedSize(cover_size, cover_size)
        if cover_path and os.path.exists(cover_path):
            pixmap = QPixmap(cover_path).scaled(
                cover_size, cover_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            cover_label.setPixmap(pixmap)
        else:
            cover_label.setStyleSheet(f"background-color: #444; border-radius: 8px;")
        layout.addWidget(cover_label, alignment=Qt.AlignCenter)
        
        title_label = QLabel(title[:30] + "..." if len(title) > 30 else title)
        title_label.setStyleSheet(f"color: {self.theme['text']}; font-size: {'24px' if self.is_big_picture else '14px'}; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        console_label = QLabel(console)
        console_label.setStyleSheet(f"color: {self.theme['text_secondary']}; font-size: {'18px' if self.is_big_picture else '12px'};")
        console_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(console_label)
        
        play_btn = QPushButton(self.tr("play"))
        play_btn.setStyleSheet(f"""
            background-color: {self.theme['accent']}; 
            color: white; 
            border-radius: 5px;
            font-size: {'20px' if self.is_big_picture else '14px'};
            padding: 10px;
        """)
        play_btn.clicked.connect(lambda _, gid=game_id: self.launch_game_by_id(gid))
        layout.addWidget(play_btn)
        
        config_btn = QPushButton("⚙️")
        config_btn.setFixedSize(30, 30)
        config_btn.clicked.connect(lambda _, gid=game_id: self.open_graphics_settings(gid))
        layout.addWidget(config_btn, alignment=Qt.AlignRight | Qt.AlignTop)
        
        return card

    def update_favorite_icon(self, button, is_favorite):
        icon = "★" if is_favorite else "☆"
        color = self.theme['favorite']
        size = "24px" if self.is_big_picture else "20px"
        button.setText(icon)
        button.setStyleSheet(f"color: {color}; background: transparent; border: none; font-size: {size};")

    def toggle_favorite(self, game_id, button):
        conn = sqlite3.connect("database/multiverse.db")
        cursor = conn.cursor()
        cursor.execute("SELECT is_favorite FROM games WHERE id = ?", (game_id,))
        current = cursor.fetchone()
        if current is not None:
            new_state = not bool(current[0])
            cursor.execute("UPDATE games SET is_favorite = ? WHERE id = ?", (int(new_state), game_id))
            conn.commit()
            self.update_favorite_icon(button, new_state)
        conn.close()

    def launch_game_by_id(self, game_id):
        from core.emulator_manager import launch_game
        success = launch_game(game_id)
        if success:
            self.start_fps_counter()
        else:
            QMessageBox.warning(self, "Error", "No se pudo iniciar el juego.\nVerifica las rutas en Configuración.")

    def start_fps_counter(self):
        """Simula el conteo de FPS."""
        self.fps_timer = QTimer()
        self.fps_timer.timeout.connect(self.fps_overlay.count_frame)
        self.fps_timer.start(16)
        QTimer.singleShot(2000, self.fps_overlay.toggle)

    def open_settings(self):
        from ui.settings_window import SettingsWindow
        settings = SettingsWindow(self, current_theme=self.current_theme, current_lang=self.lang)
        if settings.exec_() == SettingsWindow.Accepted:
            self.current_theme = settings.selected_theme
            self.lang = settings.selected_lang
            self.theme = apply_theme(QApplication.instance(), self.current_theme)
            self.update_sidebar_style()
            scan_games()
            self.load_games()

    def open_subscription(self):
        email, ok = QInputDialog.getText(self, "Suscripción", "Email:")
        if ok and email:
            from ui.subscription_window import SubscriptionWindow
            sub_window = SubscriptionWindow(email, self)
            sub_window.exec_()

    def open_stats(self):
        from ui.stats_window import StatsWindow
        stats = StatsWindow(self, lang=self.lang)
        stats.exec_()

    def open_graphics_settings(self, game_id):
        import sqlite3
        import json
        conn = sqlite3.connect("database/multiverse.db")
        cursor = conn.cursor()
        cursor.execute("SELECT graphics_profile FROM games WHERE id = ?", (game_id,))
        result = cursor.fetchone()
        conn.close()
        current_profile = json.loads(result[0]) if result and result[0] else {}
        
        from ui.graphics_settings_window import GraphicsSettingsWindow
        dialog = GraphicsSettingsWindow(self, current_profile)
        if dialog.exec_() == QDialog.Accepted:
            new_profile = dialog.get_profile()
            conn = sqlite3.connect("database/multiverse.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE games SET graphics_profile = ? WHERE id = ?", (json.dumps(new_profile), game_id))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Éxito", "Configuración gráfica guardada.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape and self.is_big_picture:
            self.toggle_big_picture()
        else:
            super().keyPressEvent(event)

    def focus_previous(self):
        widgets = [self.grid_layout.itemAt(i).widget() for i in range(self.grid_layout.count())]
        widgets = [w for w in widgets if w]
        current = self.grid_widget.focusWidget()
        if current in widgets:
            idx = widgets.index(current)
            if idx > 0:
                widgets[idx - 1].setFocus()
        elif widgets:
            widgets[0].setFocus()

    def focus_next(self):
        widgets = [self.grid_layout.itemAt(i).widget() for i in range(self.grid_layout.count())]
        widgets = [w for w in widgets if w]
        current = self.grid_widget.focusWidget()
        if current in widgets:
            idx = widgets.index(current)
            if idx < len(widgets) - 1:
                widgets[idx + 1].setFocus()
        elif widgets:
            widgets[0].setFocus()

    def play_selected(self):
        current = self.grid_widget.focusWidget()
        if current and hasattr(current, 'game_id'):
            self.launch_game_by_id(current.game_id)

    def exit_big_picture(self):
        if self.is_big_picture:
            self.toggle_big_picture()