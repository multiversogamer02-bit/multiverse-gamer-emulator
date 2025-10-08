# core/payment_manager.py
import mercadopago
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno (solo si existe .env en desarrollo)
load_dotenv()

def create_mercadopago_payment(email: str, plan: str) -> str:
    """
    Crea un pago en Mercado Pago en modo PRODUCCIÓN.
    """
    # Validar variables de entorno
    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not access_token or not access_token.startswith("APP_USR-"):
        raise Exception("MERCADOPAGO_ACCESS_TOKEN no está configurado para producción")
    
    # Precios en ARS (ajusta según tu región)
    prices = {
        "mensual": 10000,
        "trimestral": 27000,
        "anual": 96000
    }
    amount = prices.get(plan, 10000)

    # Inicializar SDK de Mercado Pago
    sdk = mercadopago.SDK(access_token)

    # Datos del pago
    payment_data = {
        "transaction_amount": float(amount),
        "description": f"Suscripción {plan} - Multiverse Gamer",
        "payment_method_id": "visa",  # Se detecta automáticamente en producción
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

    # Crear pago
    result = sdk.payment().create(payment_data)
    if result["status"] == 201:
        return result["response"]["init_point"]
    else:
        error = result.get("response", {}).get("message", "Error desconocido")
        raise Exception(f"Error Mercado Pago: {error}")

def create_paypal_payment(email: str, plan: str) -> str:
    """
    Crea un pago en PayPal en modo PRODUCCIÓN.
    """
    # Validar credenciales
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise Exception("Faltan credenciales de PayPal para producción")

    # Obtener access token de PayPal (producción)
    auth_url = "https://api.paypal.com/v1/oauth2/token"
    auth = (client_id, client_secret)
    token_data = {"grant_type": "client_credentials"}
    token_resp = requests.post(auth_url, auth=auth, data=token_data)
    if token_resp.status_code != 200:
        raise Exception("No se pudo autenticar con PayPal")
    access_token = token_resp.json()["access_token"]

    # Precios en ARS
    prices = {"mensual": 10000, "trimestral": 27000, "anual": 96000}
    amount = prices.get(plan, 10000)

    # Crear orden de pago
    order_url = "https://api.paypal.com/v2/checkout/orders"
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
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    order_resp = requests.post(order_url, json=order_data, headers=headers)
    
    if order_resp.status_code != 201:
        raise Exception("No se pudo crear la orden de PayPal")

    # Obtener URL de aprobación
    for link in order_resp.json()["links"]:
        if link["rel"] == "approve":
            return link["href"]
    
    raise Exception("No se encontró URL de aprobación en PayPal")