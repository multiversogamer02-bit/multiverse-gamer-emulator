# core/online_manager.py
import requests
from utils.license_manager import get_machine_id

# 👇 URL CORRECTA de tu backend en Render (sin /auth/)
SERVER_URL = "https://multiverse-server.onrender.com"

def register_user(email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{SERVER_URL}/register",  # ← Sin /auth/
            data={"email": email, "password": password},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error en registro: {e}")
        return False

def login_user(email: str, password: str) -> str:
    try:
        response = requests.post(
            f"{SERVER_URL}/token",  # ← Sin /auth/
            data={"username": email, "password": password},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"Error en login: {e}")
        return None

def validate_license_online(email: str) -> bool:
    try:
        machine_id = get_machine_id()
        response = requests.post(
            f"{SERVER_URL}/validate-license",
            data={"machine_id": machine_id},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error en validación de licencia: {e}")
        return False

def get_user_role(token: str) -> str:
    try:
        import jwt
        payload = jwt.decode(token, options={"verify_signature": False})
        email = payload.get("sub")
        admin_emails = ["rodrigoaguirre196@gmail.com"]
        return "admin" if email in admin_emails else "user"
    except Exception as e:
        print(f"Error al decodificar token: {e}")
        return "user"

def get_all_users() -> list:
    """Obtiene la lista de usuarios desde el servidor (solo para admins)."""
    try:
        response = requests.get(f"{SERVER_URL}/admin/users", timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al obtener usuarios: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Excepción al obtener usuarios: {e}")
        return []
        
def create_subscription(email: str, plan: str) -> str:
    """Devuelve la URL de pago para el plan seleccionado."""
    try:
        response = requests.post(
            f"{SERVER_URL}/payment/mercadopago",
            json={"email": email, "plan": plan},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("payment_url")
        return None
    except Exception as e:
        print(f"Error al crear suscripción: {e}")
        return None        