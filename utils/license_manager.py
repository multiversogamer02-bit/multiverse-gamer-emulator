# utils/license_manager.py
import os
import uuid
import hashlib
import json
from pathlib import Path

LICENSE_FILE = "license.dat"

def get_machine_id():
    mac = hex(uuid.getnode()).replace('0x', '').upper()
    hostname = os.environ.get('COMPUTERNAME', os.environ.get('HOSTNAME', 'unknown'))
    return hashlib.sha256((mac + hostname).encode()).hexdigest()

def save_license(expiry_days=30):
    machine_id = get_machine_id()
    license_data = {"machine_id": machine_id, "valid_until": expiry_days}
    with open(LICENSE_FILE, "w") as f:
        json.dump(license_data, f)

def is_license_valid():
    if not Path(LICENSE_FILE).exists():
        return False
    try:
        with open(LICENSE_FILE, "r") as f:
            data = json.load(f)
        return data.get("machine_id") == get_machine_id()
    except:
        return False