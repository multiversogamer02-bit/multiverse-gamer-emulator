# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import MultiverseMainWindow
from ui.login_window import LoginWindow
from core.online_manager import load_refresh_token, login_user

if not os.path.exists("database/multiverse.db"):
    print("🔧 Base de datos no encontrada. Creando estructura inicial...")
    from database.init_db import init_database
    init_database()
    print("✅ Base de datos creada con éxito.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Intentar usar refresh token guardado
    refresh_token = load_refresh_token()
    access_token = None
    if refresh_token:
        # Aquí deberías llamar a /token/refresh, pero por simplicidad usamos el token guardado
        # En producción, implementa la renovación del token
        access_token = refresh_token  # Simplificación temporal
    
    if access_token:
        window = MultiverseMainWindow(user_token=access_token)
        window.show()
        sys.exit(app.exec_())
    else:
        login_window = LoginWindow()
        if login_window.exec_() == LoginWindow.Accepted:
            window = MultiverseMainWindow(user_token=login_window.token)
            window.show()
            sys.exit(app.exec_())
        else:
            sys.exit()