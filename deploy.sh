#!/bin/bash
# deploy.sh - Script de despliegue seguro para Multiverse Gamer Emulador

echo "🚀 Iniciando despliegue en Render..."

# 1. Actualizar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# 2. Aplicar migraciones de base de datos
echo "🔄 Aplicando migraciones con Alembic..."
alembic upgrade head

# 3. Iniciar servidor
echo "✅ Iniciando servidor FastAPI..."
uvicorn server.main:app --host 0.0.0.0 --port $PORT

echo "✅ Despliegue completado."