# ui/login_window.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt
from core.online_manager import register_user, login_user, save_refresh_token

class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("?? Iniciar Sesi車n - Multiverse Gamer")
        self.resize(400, 300)
        self.token = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()
        self.login_tab = self.create_login_tab()
        self.register_tab = self.create_register_tab()
        tabs.addTab(self.login_tab, "Iniciar Sesi車n")
        tabs.addTab(self.register_tab, "Crear Cuenta")
        layout.addWidget(tabs)

    def create_login_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Email:"))
        self.login_email = QLineEdit()
        layout.addWidget(self.login_email)
        layout.addWidget(QLabel("Contrase?a:"))
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.login_password)
        login_btn = QPushButton("Iniciar Sesi車n")
        login_btn.clicked.connect(self.handle_login)
        layout.addWidget(login_btn)
        return widget

    def create_register_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Email:"))
        self.reg_email = QLineEdit()
        layout.addWidget(self.reg_email)
        layout.addWidget(QLabel("Contrase?a:"))
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.reg_password)
        reg_btn = QPushButton("Crear Cuenta")
        reg_btn.clicked.connect(self.handle_register)
        layout.addWidget(reg_btn)
        return widget

    def handle_login(self):
        email = self.login_email.text()
        password = self.login_password.text()
        if not email or not password:
            QMessageBox.warning(self, "Error", "Completa todos los campos.")
            return
        result = login_user(email, password)
        if result and "access_token" in result:
            self.token = result["access_token"]
            save_refresh_token(result["refresh_token"])
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Credenciales inv芍lidas.")

    def handle_register(self):
        email = self.reg_email.text()
        password = self.reg_password.text()
        if not email or not password or len(password) < 6:
            QMessageBox.warning(self, "Error", "Email v芍lido y contrase?a de 6+ caracteres.")
            return
        if register_user(email, password):
            QMessageBox.information(self, "谷xito", "Cuenta creada. Ahora inicia sesi車n.")
            self.reg_email.clear()
            self.reg_password.clear()
        else:
            QMessageBox.critical(self, "Error", "El email ya est芍 registrado.")