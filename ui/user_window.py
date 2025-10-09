# ui/user_window.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox
)
from core.online_manager import load_refresh_token, save_refresh_token
import requests

class UserWindow(QDialog):
    def __init__(self, parent=None, user_token=None):
        super().__init__(parent)
        self.user_token = user_token
        self.parent_window = parent
        self.setWindowTitle("Usuario")
        self.resize(400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Botón para cancelar suscripción
        cancel_btn = QPushButton("Cancelar Suscripción")
        cancel_btn.clicked.connect(self.cancel_subscription)
        layout.addWidget(cancel_btn)

        # Botón para cerrar sesión
        logout_btn = QPushButton("Cerrar Sesión")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        # Botón para cerrar ventana
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def cancel_subscription(self):
        # Aquí necesitas el ID de la suscripción activa
        # Por ahora, asumiremos que se obtiene de la base de datos local o del servidor
        subscription_id = self.get_active_subscription_id()
        if not subscription_id:
            QMessageBox.warning(self, "Error", "No tienes una suscripción activa.")
            return

        try:
            response = requests.post(
                "https://multiverse-server.onrender.com/subscription/cancel",
                headers={"Authorization": f"Bearer {self.user_token}"},
                data={"subscription_id": subscription_id},
                timeout=10
            )
            if response.status_code == 200:
                QMessageBox.information(self, "Éxito", "Suscripción cancelada correctamente.")
                self.accept()
            else:
                error = response.json().get("detail", "Error desconocido")
                QMessageBox.critical(self, "Error", f"No se pudo cancelar: {error}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error de conexión: {str(e)}")

    def get_active_subscription_id(self):
        # Aquí debes implementar la lógica para obtener el ID de la suscripción activa
        # Esto podría ser una consulta al servidor o una base de datos local
        # Por ahora, devolveremos None
        return None

    def logout(self):
        # Borra el token local
        save_refresh_token(None)
        QMessageBox.information(self, "Éxito", "Sesión cerrada correctamente.")
        if self.parent_window:
            self.parent_window.user_token = None
        self.accept()