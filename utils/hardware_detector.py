# utils/hardware_detector.py
import platform

def get_hardware_info():
    info = {
        "os": platform.system(),
        "cpu": "No disponible",
        "gpu": "No disponible",
        "ram_total_gb": 0
    }
    
    try:
        import psutil
        info["ram_total_gb"] = round(psutil.virtual_memory().total / (1024**3), 1)
    except:
        pass

    try:
        import wmi
        c = wmi.WMI()
        # CPU
        cpus = c.Win32_Processor()
        if cpus:
            info["cpu"] = cpus[0].Name.strip()
        # GPU
        gpus = c.Win32_VideoController()
        if gpus:
            info["gpu"] = gpus[0].Name.strip()
    except Exception as e:
        print(f"Error al obtener hardware con WMI: {e}")
        # Fallback a psutil si WMI falla
        try:
            import psutil
            info["cpu"] = f"{psutil.cpu_count(logical=False)} núcleos"
        except:
            pass

    return info