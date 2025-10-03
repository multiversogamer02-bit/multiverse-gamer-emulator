# ui/login_window.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from core.online_manager import register_user, login_user

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔐 Iniciar Sesión")
        self.setFixedSize(400, 300)
        self.token = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel("Multiverse Gamer")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Iniciar Sesión")
        self.login_btn.clicked.connect(self.login)
        btn_layout.addWidget(self.login_btn)
        self.register_btn = QPushButton("Crear Cuenta")
        self.register_btn.clicked.connect(self.register)
        btn_layout.addWidget(self.register_btn)
        layout.addLayout(btn_layout)

    def login(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Error", "Completa todos los campos.")
            return
        token = login_user(email, password)
        if token:
            self.token = token
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Credenciales inválidas.")

    def register(self):
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        if not email or not password:
            QMessageBox.warning(self, "Error", "Completa todos los campos.")
            return
        success = register_user(email, password)
        if success:
            QMessageBox.information(self, "Éxito", "Cuenta creada. Ahora inicia sesión.")
        else:
            QMessageBox.critical(self, "Error", "No se pudo crear la cuenta.")