# core/online_manager.py
import requests
import os
from utils.license_manager import get_machine_id
from cryptography.fernet import Fernet
import base64

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
    if not token:  # ✅ Añadido: si token es None o vacío, no guarda nada
        return
    os.makedirs(os.path.expanduser("~/.multiverse"), exist_ok=True)
    token_path = os.path.expanduser("~/.multiverse/refresh.token")
    # Generar clave Fernet (debería estar guardada en una variable de entorno o archivo seguro)
    # Para este ejemplo, usaremos una clave fija (¡en producción, usa una clave secreta!)
    # Clave Fernet válida (32 bytes, URL-safe Base64)
    key = b"ZkVrNnJzRlBvUWtHcXJjMm9xQ1ZwYzFqZjg0bGdLZ0pTQWdEaG1hZGdDQ1pOaWpR"
    fernet = Fernet(key)
    encrypted = fernet.encrypt(token.encode())  # ✅ Ahora token no es None
    with open(token_path, "wb") as f:  # ✅ Usa 'wb' para escribir bytes
        f.write(encrypted)

def load_refresh_token() -> str:
    """Carga el refresh token desde el archivo local."""
    token_path = os.path.expanduser("~/.multiverse/refresh.token")
    if os.path.exists(token_path):
        with open(token_path, "rb") as f:  # ✅ Usa 'rb' para leer bytes
            encrypted = f.read()
        try:
            # Usar la misma clave Fernet
            key = b"ZkVrNnJzRlBvUWtHcXJjMm9xQ1ZwYzFqZjg0bGdLZ0pTQWdEaG1hZGdDQ1pOaWpR"
            fernet = Fernet(key)
            decrypted = fernet.decrypt(encrypted)
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Error al descifrar token: {e}")
            return None
    return None