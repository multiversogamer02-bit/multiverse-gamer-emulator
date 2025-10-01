# main.py
import sys
import os
from PyQt5.QtWidgets import QApplication
from ui.main_window import MultiverseMainWindow

# Inicializar base de datos si no existe
if not os.path.exists("database/multiverse.db"):
    print("🔧 Creando base de datos...")
    from database.init_db import init_database
    init_database()
    print("✅ Base de datos creada.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MultiverseMainWindow()
    window.show()
    sys.exit(app.exec_())