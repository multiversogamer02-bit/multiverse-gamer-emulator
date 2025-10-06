# core/email_manager.py
import os
import sendgrid
from sendgrid.helpers.mail import Mail

def send_password_reset_email(to_email: str, token: str):
    """Envía un email de recuperación de contraseña."""
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
        reset_url = f"https://multiverse-server.onrender.com/auth/reset?token={token}"
        message = Mail(
            from_email=os.getenv("SENDGRID_FROM_EMAIL"),
            to_emails=to_email,
            subject="Restablece tu contraseña - Multiverse Gamer",
            html_content=f"""
            <h2>¿Olvidaste tu contraseña?</h2>
            <p>Haz clic en el siguiente enlace para restablecerla:</p>
            <a href="{reset_url}" style="background-color: #0078d7; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Restablecer contraseña
            </a>
            <p>El enlace expira en 1 hora.</p>
            """
        )
        sg.send(message)
        print(f"✅ Email enviado a {to_email}")
    except Exception as e:
        print(f"❌ Error al enviar email: {e}")