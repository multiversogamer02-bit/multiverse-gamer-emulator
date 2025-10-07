# core/payment_manager.py
import mercadopago
import os
from dotenv import load_dotenv

# Cargar variables de .env (solo si existe)
load_dotenv()

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
        
def create_paypal_payment(email: str, plan: str) -> str:
    """
    Crea un pago en PayPal usando la API REST.
    """
    # 1. Obtener access token
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise Exception("Faltan credenciales de PayPal")
    
    auth = (client_id, client_secret)
    token_url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    token_data = {"grant_type": "client_credentials"}
    token_resp = requests.post(token_url, auth=auth, data=token_data)
    access_token = token_resp.json()["access_token"]

    # 2. Crear orden de pago
    prices = {"mensual": 10000, "trimestral": 27000, "anual": 96000}
    amount = prices.get(plan, 10000)

    order_url = "https://api.sandbox.paypal.com/v2/checkout/orders"
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {"currency_code": "ARS", "value": str(amount)},
            "description": f"Suscripción {plan} - Multiverse Gamer"
        }],
        "application_context": {
            "return_url": f"https://multiverse-server.onrender.com/payment/success?email={email}&plan={plan}",
            "cancel_url": "https://multiverse-server.onrender.com/payment/failure"
        }
    }
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    order_resp = requests.post(order_url, json=order_data, headers=headers)
    
    # 3. Obtener URL de aprobación
    for link in order_resp.json()["links"]:
        if link["rel"] == "approve":
            return link["href"]
    
    raise Exception("No se pudo crear la orden de PayPal")