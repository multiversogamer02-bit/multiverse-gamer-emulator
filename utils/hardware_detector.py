# utils/hardware_detector.py
import psutil
import platform

def get_hardware_info():
    return {
        "os": platform.system(),
        "cpu": f"{psutil.cpu_count(logical=False)} núcleos",
        "gpu": "No disponible (requiere WMI)",
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1)
    }