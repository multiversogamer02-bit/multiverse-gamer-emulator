@echo off
echo 🚀 Iniciando despliegue a GitHub...
cd /d "%~dp0"

REM 1. Agregar todos los cambios
echo 📁 Agregando archivos...
git add .

REM 2. Hacer commit
echo 📝 Creando commit...
git commit -m "Fix: backend listo para Render (importaciones, __init__.py, sintaxis)"

REM 3. Forzar push a GitHub
echo 📤 Subiendo a GitHub...
git push -u origin master --force

echo ✅ ¡Despliegue completado!
echo 👉 Ahora ve a Render y haz "Manual Deploy > Deploy latest"
pause