# core/payment_manager.py
import mercadopago
import os

def create_mercadopago_payment(email: str, plan: str) -> str:
    # 1. Validar que el token exista y sea string
    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not isinstance(access_token, str) or not access_token.strip():
        raise Exception("MERCADOPAGO_ACCESS_TOKEN no está configurado correctamente")

    # 2. Inicializar SDK
    sdk = mercadopago.SDK(access_token)

    # 3. Crear datos del pago
    prices = {
        "mensual": 10000,
        "trimestral": 27000,
        "anual": 96000
    }
    amount = prices.get(plan, 10000)

    payment_data = {
        "transaction_amount": float(amount),
        "description": f"Suscripción {plan} - Multiverse Gamer",
        "payment_method_id": "visa",
        "payer": {
            "email": email
        },
        "binary_mode": True,
        "auto_return": "approved",
        "back_urls": {
            "success": f"https://multiverse-server.onrender.com/payment/success?email={email}&plan={plan}",
            "failure": "https://multiverse-server.onrender.com/payment/failure",
            "pending": "https://multiverse-server.onrender.com/payment/pending"
        }
    }

    # 4. Crear preferencia
    result = sdk.payment().create(payment_data)
    if result["status"] == 201:
        return result["response"]["init_point"]
    else:
        raise Exception(f"Error Mercado Pago: {result}")