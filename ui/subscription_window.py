# ui/subscription_window.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QComboBox, QCheckBox
)
from core.payment_manager import create_mercadopago_subscription
import webbrowser

class SubscriptionWindow(QDialog):
    def __init__(self, email: str, parent=None):
        super().__init__(parent)
        self.email = email
        self.parent_window = parent
        self.selected_plan = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Email: {self.email}"))
        layout.addWidget(QLabel("Selecciona un plan:"))

        # Checkbox de renovación automática
        self.auto_renewal = QCheckBox("✅ Renovar automáticamente cada mes")
        self.auto_renewal.setChecked(True)
        layout.addWidget(self.auto_renewal)

        monthly_btn = QPushButton("Mensual - $10.000 ARS")
        monthly_btn.clicked.connect(lambda: self.start_subscription("mensual"))
        layout.addWidget(monthly_btn)

        trimestral_btn = QPushButton("Trimestral - $27.000 ARS")
        trimestral_btn.clicked.connect(lambda: self.start_subscription("trimestral"))
        layout.addWidget(trimestral_btn)

        anual_btn = QPushButton("Anual - $96.000 ARS")
        anual_btn.clicked.connect(lambda: self.start_subscription("anual"))
        layout.addWidget(anual_btn)

    def start_subscription(self, plan: str):
        try:
            payment_url = create_mercadopago_subscription(self.email, plan)
            webbrowser.open(payment_url)
            QMessageBox.information(
                self, 
                "Pago", 
                "Se abrirá Mercado Pago para configurar tu suscripción.\n\n"
                "⚠️ Al aprobar, se activará la renovación automática."
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo iniciar la suscripción: {str(e)}")