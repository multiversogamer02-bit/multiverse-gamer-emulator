# ui/graphics_settings_window.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QComboBox, QPushButton
import json

class GraphicsSettingsWindow(QDialog):
    def __init__(self, parent=None, current_profile=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Configuración Gráfica")
        self.current_profile = current_profile or {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["Nativo", "1280x720", "1920x1080", "2560x1440"])
        self.resolution_combo.setCurrentText(self.current_profile.get("resolution", "Nativo"))
        form.addRow("Resolución:", self.resolution_combo)
        
        self.texture_combo = QComboBox()
        self.texture_combo.addItems(["Baja", "Media", "Alta", "Ultra"])
        self.texture_combo.setCurrentText(self.current_profile.get("textures", "Alta"))
        form.addRow("Texturas:", self.texture_combo)
        
        self.fps_combo = QComboBox()
        self.fps_combo.addItems(["30", "60", "120", "Sin límite"])
        self.fps_combo.setCurrentText(str(self.current_profile.get("fps_limit", 60)))
        form.addRow("Límite de FPS:", self.fps_combo)
        
        layout.addLayout(form)
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

    def get_profile(self):
        return {
            "resolution": self.resolution_combo.currentText(),
            "textures": self.texture_combo.currentText(),
            "fps_limit": int(self.fps_combo.currentText()) if self.fps_combo.currentText() != "Sin límite" else 0
        }