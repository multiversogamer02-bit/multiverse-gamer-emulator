# ui/subscription_window.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QComboBox
)
from core.payment_manager import create_mercadopago_payment, create_paypal_payment
from core.online_manager import validate_license_online
from utils.license_manager import get_machine_id
import webbrowser
import requests
import os

class SubscriptionWindow(QDialog):
    def __init__(self, email: str, parent=None):
        super().__init__(parent)
        self.email = email
        self.parent_window = parent
        self.payment_method = "mercadopago"
        self.selected_plan = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Email: {self.email}"))
        layout.addWidget(QLabel("Selecciona un plan:"))

        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Metodo de pago:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Mercado Pago", "PayPal"])
        self.method_combo.currentIndexChanged.connect(self.on_payment_method_changed)
        method_layout.addWidget(self.method_combo)
        layout.addLayout(method_layout)

        monthly_btn = QPushButton("Mensual - $10.000 ARS")
        monthly_btn.clicked.connect(lambda: self.select_plan("mensual"))
        layout.addWidget(monthly_btn)

        trimestral_btn = QPushButton("Trimestral - $27.000 ARS")
        trimestral_btn.clicked.connect(lambda: self.select_plan("trimestral"))
        layout.addWidget(trimestral_btn)

        anual_btn = QPushButton("Anual - $96.000 ARS")
        anual_btn.clicked.connect(lambda: self.select_plan("anual"))
        layout.addWidget(anual_btn)

        activate_btn = QPushButton("✅ Activar licencia (si ya pagaste)")
        activate_btn.clicked.connect(self.activate_existing_license)
        layout.addWidget(activate_btn)

    def on_payment_method_changed(self, index):
        self.payment_method = "mercadopago" if index == 0 else "paypal"

    def select_plan(self, plan: str):
        self.selected_plan = plan
        try:
            if self.payment_method == "mercadopago":
                payment_url = create_mercadopago_payment(self.email, plan)
            elif self.payment_method == "paypal":
                payment_url = create_paypal_payment(self.email, plan)
            if payment_url:
                webbrowser.open(payment_url)
                QMessageBox.information(
                    self, 
                    "Pago iniciado", 
                    "Se abrio el navegador para completar el pago.\n\n"
                    "⚠️ Despues de aprobar el pago, regresa aqui y haz clic en 'Activar licencia'."
                )
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "No se pudo generar la URL de pago.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo iniciar el pago: {str(e)}")

    def activate_existing_license(self):
        if not self.parent_window or not self.parent_window.user_token:
            QMessageBox.warning(self, "Error", "Debes iniciar sesion primero.")
            return

        token = self.parent_window.user_token
        machine_id = get_machine_id()
        plan = self.selected_plan or "mensual"

        try:
            response = requests.post(
                "https://multiverse-server.onrender.com/license/activate",
                headers={"Authorization": f"Bearer {token}"},
                json={"machine_id": machine_id, "plan": plan},
                timeout=10
            )
            if response.status_code == 200:
                QMessageBox.information(self, "✅ Exito", "¡Licencia activada correctamente!\nYa puedes jugar.")
                if self.parent_window:
                    self.parent_window.validate_online_license()
            else:
                error_msg = response.json().get("detail", "Error desconocido")
                QMessageBox.critical(self, "❌ Error", f"No se pudo activar la licencia:\n{error_msg}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"Error de conexion:\n{str(e)}")