# ui/subscription_window.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from core.online_manager import create_subscription
import webbrowser

class SubscriptionWindow(QDialog):
    def __init__(self, email: str, parent=None):
        super().__init__(parent)
        self.email = email
        self.setWindowTitle("💎 Suscripción - Multiverse Gamer")
        self.setFixedSize(300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Elige tu plan:"))

        btn_mensual = QPushButton("Mensual - $10.000 ARS")
        btn_mensual.clicked.connect(lambda: self.start_payment("mensual"))
        layout.addWidget(btn_mensual)

        btn_trimestral = QPushButton("Trimestral - $27.000 ARS (10% off)")
        btn_trimestral.clicked.connect(lambda: self.start_payment("trimestral"))
        layout.addWidget(btn_trimestral)

        btn_anual = QPushButton("Anual - $96.000 ARS (20% off)")
        btn_anual.clicked.connect(lambda: self.start_payment("anual"))
        layout.addWidget(btn_anual)

    def start_payment(self, plan: str):
        url = create_subscription(self.email, plan)
        if url:
            webbrowser.open(url)
            QMessageBox.information(self, "Pago", "Se abrirá el navegador para completar el pago.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo iniciar el pago.")