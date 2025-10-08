# test_db.py
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./server.db")

engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        print("✅ Conexión exitosa a la base de datos")
except Exception as e:
    print(f"❌ Error al conectar: {e}")