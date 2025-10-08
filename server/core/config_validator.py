# server/core/config_validator.py
import os
from typing import List

def validate_required_env_vars() -> None:
    """
    Valida que todas las variables de entorno críticas estén definidas.
    Lanza una excepción si falta alguna.
    """
    required_vars: List[str] = [
        "SECRET_KEY",
        "MERCADOPAGO_ACCESS_TOKEN",
        "MERCADOPAGO_WEBHOOK_SECRET",
        "DATABASE_URL",
        "SENDGRID_API_KEY",
        "SENDGRID_FROM_EMAIL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise EnvironmentError(
            f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}\n"
            "Configúralas en Render o en tu archivo .env."
        )
    
    # Validación adicional: DATABASE_URL debe ser PostgreSQL en producción
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url.startswith("sqlite") and not db_url.startswith("postgresql"):
        raise EnvironmentError("❌ DATABASE_URL debe usar 'postgresql://' en producción.")
    
    print("✅ Todas las variables de entorno críticas están configuradas.")