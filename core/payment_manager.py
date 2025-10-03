# core/payment_manager.py
import mercadopago
import os

def create_mercadopago_payment(email: str, plan: str):
    sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN"))
    
    # Mapear planes a precios
    prices = {"mensual": 1000, "trimestral": 2700, "anual": 9600}
    amount = prices.get(plan, 1000)
    
    request_options = mercadopago.config.RequestOptions()
    request_options.custom_headers = {
        "X-Idempotency-Key": f"{email}-{plan}"  # Evita pagos duplicados
    }
    
    payment_data = {
        "transaction_amount": float(amount),
        "description": f"Suscripción {plan} - Multiverse Gamer",
        "payment_method_id": "visa",  # Opcional en sandbox
        "payer": {
            "email": email
        },
        "binary_mode": True,  # Solo pagos aprobados
        "auto_return": "approved",
        "back_urls": {
            "success": "https://multiverse-server.onrender.com/payment/success?email=" + email + "&plan=" + plan,
            "failure": "https://multiverse-server.onrender.com/payment/failure",
            "pending": "https://multiverse-server.onrender.com/payment/pending"
        }
    }
    
    result = sdk.payment().create(payment_data, request_options)
    if result["status"] == 201:
        return result["response"]["init_point"]  # URL de pago
    else:
        raise Exception(f"Error Mercado Pago: {result}")