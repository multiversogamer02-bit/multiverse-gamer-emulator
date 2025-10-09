# core/payment_manager.py
import mercadopago
import os
from dotenv import load_dotenv

load_dotenv()

def create_mercadopago_payment(email: str, plan: str) -> str:
    access_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if not access_token or not access_token.startswith("APP_USR-"):
        raise Exception("MERCADOPAGO_ACCESS_TOKEN debe ser de producción (APP_USR-...)")
    
    prices = {"mensual": 10000, "trimestral": 27000, "anual": 96000}
    amount = prices.get(plan, 10000)

    sdk = mercadopago.SDK(access_token)

    payment_data = {
        "items": [{
            "title": f"Suscripción {plan} - Multiverse Gamer",
            "quantity": 1,
            "unit_price": float(amount),
            "currency_id": "ARS"
        }],
        "payer": {"email": email},
        "back_urls": {
            "success": f"https://multiverse-server.onrender.com/payment/success?email={email}&plan={plan}",
            "failure": "https://multiverse-server.onrender.com/payment/failure",
            "pending": "https://multiverse-server.onrender.com/payment/pending"
        },
        "auto_return": "approved",  # ← Sí se permite en preference
        "binary_mode": True
    }

    result = sdk.preference().create(payment_data)  # ← ¡CAMBIO CLAVE!
    if result["status"] == 201:
        return result["response"]["init_point"]
    else:
        error = result.get("response", {}).get("message", "Error desconocido")
        raise Exception(f"Error Mercado Pago: {error}")

def create_paypal_payment(email: str, plan: str) -> str:
    client_id = os.getenv("PAYPAL_CLIENT_ID")
    client_secret = os.getenv("PAYPAL_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise Exception("Faltan credenciales de PayPal para producción")

    auth_url = "https://api.paypal.com/v1/oauth2/token"
    order_url = "https://api.paypal.com/v2/checkout/orders"

    auth = (client_id, client_secret)
    token_data = {"grant_type": "client_credentials"}
    token_resp = requests.post(auth_url, auth=auth, data=token_data)
    if token_resp.status_code != 200:
        raise Exception("No se pudo autenticar con PayPal")
    access_token = token_resp.json()["access_token"]

    prices = {"mensual": 10000, "trimestral": 27000, "anual": 96000}
    amount = prices.get(plan, 10000)

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
    
    if order_resp.status_code != 201:
        raise Exception("No se pudo crear la orden de PayPal")

    for link in order_resp.json()["links"]:
        if link["rel"] == "approve":
            return link["href"]
    
    raise Exception("No se encontró URL de aprobación en PayPal")