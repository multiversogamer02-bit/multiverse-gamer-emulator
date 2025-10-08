# utils/license_manager.py
import os
import hashlib
import json
import uuid
import platform
from pathlib import Path

LICENSE_FILE = Path.home() / ".multiverse" / "license.dat"

def get_machine_id():
    """Genera un ID único basado en hardware del sistema."""
    try:
        # Componentes estables del sistema
        components = [
            str(uuid.getnode()),  # MAC address
            platform.machine(),
            platform.processor(),
            platform.system(),
            os.environ.get("COMPUTERNAME", os.environ.get("HOSTNAME", ""))
        ]
        combined = "".join(components).encode()
        return hashlib.sha256(combined).hexdigest()
    except:
        # Fallback seguro
        return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()

def save_license(expiry_days=30):
    LICENSE_FILE.parent.mkdir(exist_ok=True)
    machine_id = get_machine_id()
    license_data = {
        "machine_id": machine_id,
        "valid_until_days": expiry_days
    }
    with open(LICENSE_FILE, "w") as f:
        json.dump(license_data, f)

def is_license_valid():
    if not LICENSE_FILE.exists():
        return False
    try:
        with open(LICENSE_FILE, "r") as f:
            data = json.load(f)
        return data.get("machine_id") == get_machine_id()
    except:
        return False