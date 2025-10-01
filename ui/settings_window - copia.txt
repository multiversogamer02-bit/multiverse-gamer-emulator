# ui/settings_window.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QScrollArea, QWidget, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt
from ui.theme_manager import THEMES  # ← Importamos los temas
import sqlite3
import os

class SettingsWindow(QDialog):
    def __init__(self, parent=None, current_theme="Oscuro"):
        super().__init__(parent)
        self.setWindowTitle("Configuración de Emuladores")
        self.resize(800, 600)
        self.current_theme = current_theme
        self.selected_theme = current_theme  # Para devolver el valor al guardar
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 👇 Selector de tema (arriba de todo)
        theme_layout = QGridLayout()
        theme_layout.addWidget(QLabel("<b>Tema visual:</b>"), 0, 0)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(THEMES.keys())
        self.theme_combo.setCurrentText(self.current_theme)
        self.theme_combo.currentTextChanged.connect(self.on_theme_changed)
        theme_layout.addWidget(self.theme_combo, 0, 1, 1, 2)
        layout.addLayout(theme_layout)

        # 👇 Botón de licencia de prueba
        license_btn = QPushButton("Activar Licencia de Prueba (30 días)")
        license_btn.clicked.connect(self.activate_trial)
        layout.addWidget(license_btn)

        # Separador
        sep = QLabel()
        sep.setFixedHeight(20)
        layout.addWidget(sep)

        # Área desplazable para consolas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.grid = QGridLayout(content)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Botón guardar
        self.save_btn = QPushButton("Guardar Configuración")
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

            self.grid.addWidget(QLabel("Carpeta de ROMs:"), row, 0)
            roms_edit = QLineEdit()
            roms_edit.setText(roms_path or "")
            self.grid.addWidget(roms_edit, row, 1)
            roms_btn = QPushButton("Examinar...")
            roms_btn.clicked.connect(lambda _, e=roms_edit: self.select_folder(e))
            self.grid.addWidget(roms_btn, row, 2)
            row += 1

            self.grid.addWidget(QLabel("Emulador:"), row, 0)
            emulator_edit = QLineEdit()
            emulator_edit.setText(emulator_path or "")
            self.grid.addWidget(emulator_edit, row, 1)
            emulator_btn = QPushButton("Examinar...")
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
                    raise ValueError(f"La carpeta de ROMs no existe: {roms_path}")
                if emulator_path and not os.path.exists(emulator_path):
                    raise ValueError(f"El emulador no existe: {emulator_path}")

                cursor.execute("""
                    UPDATE consoles 
                    SET roms_path = ?, emulator_path = ? 
                    WHERE id = ?
                """, (roms_path, emulator_path, console_id))

            conn.commit()
            QMessageBox.information(self, "Éxito", "Configuración guardada correctamente.")
            self.accept()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{str(e)}")
        finally:
            conn.close()

    # 👇 Método para activar licencia de prueba
    def activate_trial(self):
        from utils.license_manager import save_license
        try:
            save_license(30)
            QMessageBox.information(self, "Éxito", "Licencia de prueba activada por 30 días.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo activar la licencia:\n{str(e)}")