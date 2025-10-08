# utils/hardware_detector.py
import platform
import psutil
import subprocess
import re

def get_gpu_info():
    system = platform.system()
    try:
        if system == "Windows":
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                return lines[1].strip()
        elif system == "Linux":
            result = subprocess.run(
                ["lspci"], capture_output=True, text=True, check=True
            )
            for line in result.stdout.split("\n"):
                if "VGA" in line or "3D" in line:
                    return line.split(":")[-1].strip()
        elif system == "Darwin":
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"], capture_output=True, text=True
            )
            for line in result.stdout.split("\n"):
                if "Chip\|GPU" in line or "Vendor" in line:
                    return line.strip()
    except:
        pass
    return "Desconocida"

def get_hardware_info():
    return {
        "os": platform.platform(),
        "cpu": platform.processor() or "Desconocido",
        "gpu": get_gpu_info(),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024 ** 3), 1)
    }