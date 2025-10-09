# ui/settings_window.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QScrollArea, QWidget, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from ui.theme_manager import THEMES
import sqlite3
import os

class SettingsWindow(QDialog):
    def __init__(self, parent=None, current_theme="Oscuro", current_lang="es"):
        super().__init__(parent)
        self.current_lang = current_lang
        self.translations = {
            "es": {
                "window_title": "Configuración de Emuladores",
                "theme_label": "Tema visual:",
                "trial_btn": "Activar Licencia de Prueba (30 días)",
                "roms_label": "Carpeta de ROMs:",
                "emulator_label": "Emulador:",
                "browse_btn": "Examinar...",
                "save_btn": "Guardar Configuración",
                "success_save": "Configuración guardada correctamente.",
                "error_save": "No se pudo guardar:\n{error}",
                "success_trial": "Licencia de prueba activada por 30 días.",
                "error_trial": "No se pudo activar la licencia:\n{error}",
                "roms_not_exist": "La carpeta de ROMs no existe: {path}",
                "emulator_not_exist": "El emulador no existe: {path}",
                "terms_btn": "Ver Términos de Uso"
            },
            "en": {
                "window_title": "Emulator Settings",
                "theme_label": "Visual Theme:",
                "trial_btn": "Activate Trial License (30 days)",
                "roms_label": "ROMs Folder:",
                "emulator_label": "Emulator:",
                "browse_btn": "Browse...",
                "save_btn": "Save Configuration",
                "success_save": "Configuration saved successfully.",
                "error_save": "Could not save:\n{error}",
                "success_trial": "Trial license activated for 30 days.",
                "error_trial": "Could not activate license:\n{error}",
                "roms_not_exist": "ROMs folder does not exist: {path}",
                "emulator_not_exist": "Emulator does not exist: {path}",
                "terms_btn": "View Terms of Use"
            }
        }
        self.setWindowTitle(self.tr("window_title"))
        self.resize(800, 600)
        self.current_theme = current_theme
        self.selected_theme = current_theme
        self.selected_lang = current_lang
        self.init_ui()
        self.load_settings()

    def tr(self, key):
        return self.translations[self.current_lang].get(key, key)

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Tema
        theme_layout = QGridLayout()
        theme_layout.addWidget(QLabel(f"<b>{self.tr('theme_label')}</b>"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.setCurrentText(self.current_theme)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo, 0, 1, 1, 2)
        layout.addLayout(theme_layout)

        # Idioma
        lang_layout = QGridLayout()
        lang_layout.addWidget(QLabel("<b>Idioma / Language:</b>"), 0, 0)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Español", "English"])
        self.lang_combo.setCurrentIndex(0 if self.current_lang == "es" else 1)
        lang_layout.addWidget(self.lang_combo, 0, 1, 1, 2)
        layout.addLayout(lang_layout)

        # Botón de licencia de prueba
        license_btn = QPushButton(self.tr("trial_btn"))
        license_btn.clicked.connect(self.activate_trial)
        layout.addWidget(license_btn)

        # Botón de Términos de Uso
        terms_btn = QPushButton(self.tr("terms_btn"))
        terms_btn.clicked.connect(self.show_terms)
        layout.addWidget(terms_btn)

        # Separador
        sep = QLabel()
        sep.setFixedHeight(20)
        layout.addWidget(sep)

        # Configuración de consolas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.grid = QGridLayout(content)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Botón de guardar
        self.save_btn = QPushButton(self.tr("save_btn"))
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

        self.fields = {}

    def on_theme_changed(self, theme_name):
        self.selected_theme = theme_name

    def load_settings(self):
        conn = sqlite3.connect("database/multiverse.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, roms_path, emulator_path FROM consoles ORDER BY name")
        consoles = cursor.fetchall()
        conn.close()

        row = 0
        for console_id, name, roms_path, emulator_path in consoles:
            label = QLabel(f"<b>{name}</b>")
            label.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(label, row, 0, 1, 3)
            row += 1

            self.grid.addWidget(QLabel(self.tr("roms_label")), row, 0)
            roms_edit = QLineEdit()
            roms_edit.setText(roms_path or "")
            self.grid.addWidget(roms_edit, row, 1)
            roms_btn = QPushButton(self.tr("browse_btn"))
            roms_btn.clicked.connect(lambda _, e=roms_edit: self.select_folder(e))
            self.grid.addWidget(roms_btn, row, 2)
            row += 1

            self.grid.addWidget(QLabel(self.tr("emulator_label")), row, 0)
            emulator_edit = QLineEdit()
            emulator_edit.setText(emulator_path or "")
            self.grid.addWidget(emulator_edit, row, 1)
            emulator_btn = QPushButton(self.tr("browse_btn"))
            emulator_btn.clicked.connect(lambda _, e=emulator_edit: self.select_emulator(e))
            self.grid.addWidget(emulator_btn, row, 2)
            row += 1

            sep = QLabel()
            sep.setFixedHeight(20)
            self.grid.addWidget(sep, row, 0, 1, 3)
            row += 1

            self.fields[console_id] = {
                "roms": roms_edit,
                "emulator": emulator_edit
            }

    def select_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de ROMs")
        if folder:
            line_edit.setText(folder)

    def select_emulator(self, line_edit):
        if os.name == 'nt':
            file_filter = "Ejecutables (*.exe)"
        else:
            file_filter = "Archivos (*)"
        file, _ = QFileDialog.getOpenFileName(self, "Seleccionar emulador", "", file_filter)
        if file:
            line_edit.setText(file)

    def save_settings(self):
        conn = sqlite3.connect("database/multiverse.db")
        cursor = conn.cursor()
        try:
            for console_id, fields in self.fields.items():
                roms_path = fields["roms"].text().strip()
                emulator_path = fields["emulator"].text().strip()
                if roms_path and not os.path.exists(roms_path):
                    raise ValueError(self.tr("roms_not_exist").format(path=roms_path))
                if emulator_path and not os.path.exists(emulator_path):
                    raise ValueError(self.tr("emulator_not_exist").format(path=emulator_path))
                cursor.execute("""
                    UPDATE consoles 
                    SET roms_path = ?, emulator_path = ? 
                    WHERE id = ?
                """, (roms_path, emulator_path, console_id))
            conn.commit()
            QMessageBox.information(self, "Éxito", self.tr("success_save"))
            self.selected_lang = "es" if self.lang_combo.currentIndex() == 0 else "en"
            self.accept()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", self.tr("error_save").format(error=str(e)))
        finally:
            conn.close()

    def activate_trial(self):
        from utils.license_manager import save_license
        try:
            save_license(30)
            QMessageBox.information(self, "Éxito", self.tr("success_trial"))
        except Exception as e:
            QMessageBox.critical(self, "Error", self.tr("error_trial").format(error=str(e)))

    def show_terms(self):
        from PyQt5.QtWidgets import QTextBrowser
        terms_window = QDialog(self)
        terms_window.setWindowTitle("📜 " + self.tr("terms_btn"))
        terms_window.resize(600, 500)
        layout = QVBoxLayout(terms_window)
        browser = QTextBrowser()
        try:
            with open("TERMS.md", "r", encoding="utf-8") as f:
                browser.setMarkdown(f.read())
        except:
            browser.setPlainText("No se pudo cargar el archivo de términos.")
        layout.addWidget(browser)
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(terms_window.accept)
        layout.addWidget(close_btn)
        terms_window.exec_()