# utils/hardware_detector.py
import psutil
import platform
import subprocess

def get_hardware_info():
    return {
        "os": platform.system(),
        "cpu": get_cpu_info(),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "gpu": get_gpu_info()
    }

def get_cpu_info():
    if platform.system() == "Windows":
        try:
            result = subprocess.check_output("wmic cpu get name", shell=True).decode()
            return result.strip().split("\n")[1].strip()
        except:
            return "CPU desconocido"
    return "CPU desconocido"

def get_gpu_info():
    if platform.system() == "Windows":
        try:
            result = subprocess.check_output("wmic path win32_VideoController get name", shell=True).decode()
            gpus = [line.strip() for line in result.strip().split("\n")[1:] if line.strip()]
            return gpus[0] if gpus else "GPU desconocida"
        except:
            return "GPU desconocida"
    return "GPU desconocida"