# ui/admin_window.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from core.online_manager import get_all_users

class AdminWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Panel de Administrador")
        self.setFixedSize(600, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Usuarios registrados:"))

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Email", "Fecha de registro", "Es admin"])
        layout.addWidget(self.table)

        self.load_users()

    def load_users(self):
        users = get_all_users()  # ← Debes implementar este endpoint en FastAPI
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(user["email"]))
            self.table.setItem(row, 1, QTableWidgetItem(user["created_at"]))
            self.table.setItem(row, 2, QTableWidgetItem("Sí" if user["is_admin"] else "No"))