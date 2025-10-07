# ui/subscription_window.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QComboBox
from core.payment_manager import create_mercadopago_payment, create_paypal_payment
import webbrowser

class SubscriptionWindow(QDialog):
    def __init__(self, email: str, parent=None):
        super().__init__(parent)
        self.email = email
        self.payment_method = "mercadopago"  # Valor por defecto
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Email: {self.email}"))
        layout.addWidget(QLabel("Selecciona un plan:"))

        # Selector de método de pago
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Método de pago:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["Mercado Pago", "PayPal"])
        self.method_combo.currentIndexChanged.connect(self.on_payment_method_changed)
        method_layout.addWidget(self.method_combo)
        layout.addLayout(method_layout)

        # Botones de planes
        monthly_btn = QPushButton("Mensual - $10.000 ARS")
        monthly_btn.clicked.connect(lambda: self.start_payment("mensual"))
        layout.addWidget(monthly_btn)

        trimestral_btn = QPushButton("Trimestral - $27.000 ARS")
        trimestral_btn.clicked.connect(lambda: self.start_payment("trimestral"))
        layout.addWidget(trimestral_btn)

        anual_btn = QPushButton("Anual - $96.000 ARS")
        anual_btn.clicked.connect(lambda: self.start_payment("anual"))
        layout.addWidget(anual_btn)

    def on_payment_method_changed(self, index):
        self.payment_method = "mercadopago" if index == 0 else "paypal"
        
    def start_payment(self, plan: str):
        try:
            if self.payment_method == "mercadopago":
                payment_url = create_mercadopago_payment(self.email, plan)
            elif self.payment_method == "paypal":
                payment_url = create_paypal_payment(self.email, plan)
        
            if payment_url:
                webbrowser.open(payment_url)
                QMessageBox.information(self, "Pago", "Se abrirá el navegador para completar el pago.")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "No se pudo generar la URL de pago.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo iniciar el pago: {str(e)}")