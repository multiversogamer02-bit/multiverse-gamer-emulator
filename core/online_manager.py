# core/online_manager.py
import requests
import os
import jwt
from cryptography.fernet import Fernet
from utils.license_manager import get_machine_id

SERVER_URL = "https://multiverse-server.onrender.com"
TOKEN_PATH = os.path.expanduser("~/.multiverse/refresh.token")
KEY_PATH = os.path.expanduser("~/.multiverse/crypto.key")

def _get_crypto_key():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)
        with open(KEY_PATH, "wb") as f:
            f.write(key)
    else:
        with open(KEY_PATH, "rb") as f:
            key = f.read()
    return key

def save_refresh_token(token: str):
    key = _get_crypto_key()
    fernet = Fernet(key)
    encrypted = fernet.encrypt(token.encode())
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, "wb") as f:
        f.write(encrypted)

def load_refresh_token() -> str:
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        key = _get_crypto_key()
        fernet = Fernet(key)
        with open(TOKEN_PATH, "rb") as f:
            encrypted = f.read()
        return fernet.decrypt(encrypted).decode()
    except:
        return None

def register_user(email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{SERVER_URL}/register",
            data={"email": email, "password": password},
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def login_user(email: str, password: str) -> dict:
    try:
        response = requests.post(
            f"{SERVER_URL}/token",
            data={"username": email, "password": password},
            timeout=10
        )
        return response.json() if response.status_code == 200 else None
    except:
        return None

def validate_license_online(token: str) -> bool:
    try:
        machine_id = get_machine_id()
        response = requests.post(
            f"{SERVER_URL}/validate-license",
            headers={"Authorization": f"Bearer {token}"},
            json={"machine_id": machine_id},
            timeout=10
        )
        return response.status_code == 200
    except:
        return False

def get_user_role(token: str) -> str:
    try:
        # Verificar firma con clave secreta del servidor (simulado)
        SECRET_KEY = os.getenv("JWT_SECRET", "fallback_inseguro")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        return "admin" if email == "rodrigoaguirre196@gmail.com" else "user"
    except:
        return "user"