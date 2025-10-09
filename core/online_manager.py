# core/online_manager.py
import requests
import os
from utils.license_manager import get_machine_id
from cryptography.fernet import Fernet, InvalidToken
import base64
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (solo en desarrollo local)
load_dotenv()

SERVER_URL = "https://multiverse-server.onrender.com"

def _get_fernet_key():
    """Obtiene y valida la clave Fernet desde la variable de entorno o .env."""
    key_b64 = os.getenv('FERNET_KEY')
    if not key_b64:
        raise ValueError(
            "❌ La variable de entorno FERNET_KEY no está definida. "
            "Configúrela en Render (producción) o en su archivo .env (desarrollo)."
        )
    try:
        # Verifica que la clave sea válida para Fernet (32 bytes, base64)
        key_bytes = base64.urlsafe_b64decode(key_b64)
        if len(key_bytes) != 32:
            raise ValueError("La clave FERNET_KEY no tiene 32 bytes.")
        # Devolvemos la clave en formato base64 string, como la espera Fernet()
        return key_b64.encode()
    except (base64.binascii.Error, ValueError) as e:
        raise ValueError(f"La FERNET_KEY proporcionada no es válida: {e}")

def register_user(email: str, password: str) -> bool:
    try:
        response = requests.post(
            f"{SERVER_URL}/register",
            data={"email": email, "password": password},
            timeout=10
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
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        else:
            # Opcional: loguear el mensaje de error del servidor
            # error_msg = response.json().get('detail', 'Error desconocido')
            # print(f"Error de login: {error_msg}")
            pass
        return None
    except Exception as e:
        print(f"Error en login: {e}")
        return None

def request_password_reset(email: str) -> bool:
    try:
        response = requests.post(
            f"{SERVER_URL}/auth/forgot-password",
            data={"email": email},
            timeout=10
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
            json={"machine_id": machine_id}, # Enviamos como JSON
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error en validación de licencia: {e}")
        return False

def get_user_role(token: str) -> str:
    try:
        # Importar aquí para evitar problemas si no se usa
        import jwt
        SECRET_KEY = os.getenv("JWT_SECRET") # Debe estar en Render o .env
        if not SECRET_KEY:
            raise EnvironmentError("JWT_SECRET no está definida.")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        return "admin" if email == "rodrigoaguirre196@gmail.com" else "user"
    except Exception as e:
        print(f"Error al decodificar token: {e}")
        return "user"

def get_all_users(token: str) -> list:
    try:
        response = requests.get(
            f"{SERVER_URL}/admin/users",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Excepción al obtener usuarios: {e}")
        return []

def save_refresh_token(token: str):
    """Guarda el refresh token en un archivo local seguro."""
    if not token:
        print("⚠️ Advertencia: Se intentó guardar un token vacío o None.")
        return

    os.makedirs(os.path.expanduser("~/.multiverse"), exist_ok=True)
    token_path = os.path.expanduser("~/.multiverse/refresh.token")

    try:
        fernet_key_b64 = _get_fernet_key()
        fernet = Fernet(fernet_key_b64)
        encrypted = fernet.encrypt(token.encode())
        with open(token_path, "wb") as f:
            f.write(encrypted)
        print(f"✅ Refresh token guardado en {token_path}")
    except Exception as e:
        print(f"❌ Error al guardar el refresh token: {e}")

def load_refresh_token() -> str:
    """Carga el refresh token desde el archivo local."""
    token_path = os.path.expanduser("~/.multiverse/refresh.token")
    if os.path.exists(token_path):
        try:
            with open(token_path, "rb") as f:
                encrypted = f.read()
            fernet_key_b64 = _get_fernet_key()
            fernet = Fernet(fernet_key_b64)
            decrypted = fernet.decrypt(encrypted)
            token_str = decrypted.decode('utf-8')
            print("✅ Refresh token cargado correctamente.")
            return token_str
        except InvalidToken:
            print("❌ Error: El refresh token no se pudo descifrar. Puede estar corrupto o la clave FERNET_KEY es incorrecta.")
            # Opcional: eliminar el archivo corrupto
            # os.remove(token_path)
        except Exception as e:
            print(f"❌ Error al cargar/descifrar el refresh token: {e}")
    else:
        print("ℹ️  Archivo de refresh token no encontrado.")
    return None
