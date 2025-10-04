# core/online_manager.py
import requests
import os
from utils.license_manager import get_machine_id

SERVER_URL = "https://multiverse-server.onrender.com"

def register_user(email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{SERVER_URL}/register",
            data={"email": email, "password": password},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error en registro: {e}")
        return False

def login_user(email: str, password: str) -> dict:
    try:
        response = requests.post(
            f"{SERVER_URL}/token",
            data={"username": email, "password": password},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error en login: {e}")
        return None

def request_password_reset(email: str) -> bool:
    try:
        response = requests.post(
            f"{SERVER_URL}/auth/forgot-password",
            data={"email": email},
            timeout=5
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error en recuperación: {e}")
        return False

def validate_license_online(token: str) -> bool:
    try:
        machine_id = get_machine_id()
        response = requests.post(
            f"{SERVER_URL}/validate-license",
            headers={"Authorization": f"Bearer {token}"},
            json={"machine_id": machine_id},
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
    try:
        response = requests.get(f"{SERVER_URL}/admin/users", timeout=5)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Excepción al obtener usuarios: {e}")
        return []

def save_refresh_token(token: str):
    """Guarda el refresh token en un archivo local seguro."""
    os.makedirs(os.path.expanduser("~/.multiverse"), exist_ok=True)
    token_path = os.path.expanduser("~/.multiverse/refresh.token")
    with open(token_path, "w") as f:
        f.write(token)

def load_refresh_token() -> str:
    """Carga el refresh token desde el archivo local."""
    token_path = os.path.expanduser("~/.multiverse/refresh.token")
    if os.path.exists(token_path):
        with open(token_path, "r") as f:
            return f.read().strip()
    return None