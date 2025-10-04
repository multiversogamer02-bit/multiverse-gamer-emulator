# core/payment_manager.py
import mercadopago
import os

def create_mercadopago_payment(email: str, plan: str):
    # 👇 Precios actualizados en ARS
    prices = {
        "mensual": 10000,
        "trimestral": 27000,
        "anual": 96000
    }
    amount = prices.get(plan, 10000)
    
    request_options = mercadopago.config.RequestOptions()
    request_options.custom_headers = {
        "X-Idempotency-Key": f"{email}-{plan}"  # Evita pagos duplicados
    }
    
    payment_data = {
        "transaction_amount": float(amount),  # Ej: 10000.0
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