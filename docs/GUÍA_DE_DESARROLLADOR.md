# Cómo agregar una nueva consola

1. Edita `EXTENSIONS` en `core/game_scanner.py`.
2. Asegúrate de que el nombre coincida con la DB.
3. (Opcional) Agrega icono en `ui/assets/consoles/`.
4. La interfaz ya la mostrará al escanear.

# Cómo agregar un nuevo método de pago

1. Crea un módulo en `payments/` (ej: `mercado_pago.py`).
2. Implementa `process_payment(amount, user_id)`.
3. Conéctalo al botón en `ui/payment_window.py`.