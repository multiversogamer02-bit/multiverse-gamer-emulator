import sendgrid
from sendgrid.helpers.mail import Mail

def send_password_reset_email(to_email: str, token: str):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    reset_url = f"https://multiverse-server.onrender.com/auth/reset?token={token}"
    message = Mail(
        from_email=os.getenv("SENDGRID_FROM_EMAIL"),
        to_emails=to_email,
        subject="Restablece tu contraseña",
        html_content=f"<p>Haz clic <a href='{reset_url}'>aquí</a> para restablecer tu contraseña.</p>"
    )
    sg.send(message)