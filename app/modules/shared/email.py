import smtplib

from email.message import EmailMessage

from app.core.settings import settings


def send_email(to: str, subject: str, body: str) -> None:
    """Send a plain-text email via SMTP."""
    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(host=settings.smtp_host, port=settings.smtp_port, timeout=10) as server:
        if settings.smtp_use_tls:
            server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(message)
