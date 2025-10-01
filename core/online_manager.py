# core/online_manager.py
import requests

# Usar backend local en desarrollo
SERVER_URL = "http://localhost:8000"

def register_user(email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{SERVER_URL}/auth/register",
            data={"email": email, "password": password},
            timeout=5
        )
        print(f"Registro → Código: {response.status_code}, Respuesta: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error en registro: {e}")
        return False

def login_user(email: str, password: str) -> str:
    try:
        response = requests.post(
            f"{SERVER_URL}/auth/login",
            data={"username": email, "password": password},
            timeout=5
        )
        print(f"Login → Código: {response.status_code}, Respuesta: {response.text}")
        if response.status_code == 200:
            return response.json().get("access_token")
        return None
    except Exception as e:
        print(f"Error en login: {e}")
        return None

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