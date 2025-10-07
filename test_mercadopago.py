# test_mercadopago.py
import os
import mercadopago

# Configura tu Access Token de prueba
ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "TU_ACCESS_TOKEN_DE_PRUEBA")

def test_create_payment():
    """Crea un pago de prueba en modo sandbox."""
    sdk = mercadopago.SDK(ACCESS_TOKEN)
    
    payment_data = {
        "transaction_amount": 10000.0,  # $10.000 ARS
        "description": "Suscripción mensual - Multiverse Gamer",
        "payment_method_id": "visa",
        "payer": {
            "email": "test_user_12345678@testuser.com"  # Email de prueba de Mercado Pago
        },
        "binary_mode": True,
        "auto_return": "approved",
        "back_urls": {
            "success": "https://multiverse-server.onrender.com/payment/success?email=test_user_12345678@testuser.com&plan=mensual",
            "failure": "https://multiverse-server.onrender.com/payment/failure",
            "pending": "https://multiverse-server.onrender.com/payment/pending"
        }
    }
    
    try:
        result = sdk.payment().create(payment_data)
        if result["status"] == 201:
            payment = result["response"]
            print("✅ Pago creado exitosamente!")
            print(f"ID del pago: {payment['id']}")
            print(f"Estado: {payment['status']}")
            print(f"URL de pago: {payment['init_point']}")
            print("\n👉 Abre esta URL en tu navegador para probar el pago:")
            print(payment['init_point'])
        else:
            print(f"❌ Error al crear el pago: {result}")
    except Exception as e:
        print(f"⚠️ Excepción: {e}")

if __name__ == "__main__":
    test_create_payment()