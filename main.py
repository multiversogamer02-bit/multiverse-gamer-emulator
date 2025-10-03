# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import MultiverseMainWindow
from ui.login_window import LoginWindow  # ← Importar ventana de login

# Inicializar base de datos si no existe
if not os.path.exists("database/multiverse.db"):
    print("🔧 Base de datos no encontrada. Creando estructura inicial...")
    from database.init_db import init_database
    init_database()
    print("✅ Base de datos creada con éxito.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Estilo consistente y profesional
    # 👇 Mostrar ventana de login primero
    login_window = LoginWindow()
    if login_window.exec_() == LoginWindow.Accepted:
        # Solo iniciar la app principal si el login fue exitoso
        window = MultiverseMainWindow(user_token=login_window.token)  # ← Pasar el token
        window.show()
        sys.exit(app.exec_())
    else:
        # Salir si el usuario cierra la ventana de login
        sys.exit()