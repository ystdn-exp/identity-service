import smtplib

from app.core.celery_app import celery_app
from app.modules.shared.email import send_email
from app.modules.shared.enums import OTPType

OTP_EMAIL_SUBJECTS = {
    OTPType.REGISTRATION: "Verify your email",
    OTPType.EMAIL_CHANGE: "Confirm your new email",
    OTPType.PASSWORD_RESET: "Reset your password",
}


@celery_app.task(
    name="app.modules.users.tasks.email_verification.send_otp_email",
    autoretry_for=(smtplib.SMTPException, OSError),
    retry_backoff=True,
    retry_backoff_max=60,
    max_retries=3,
)
def send_otp_email(email: str, otp_type: str, code: str) -> None:
    """Send an OTP code to the given email address."""
    subject = OTP_EMAIL_SUBJECTS.get(OTPType(otp_type), "Your verification code")
    body = f"Your verification code is: {code}\n\nThis code will expire in 5 minutes."

    send_email(email, subject, body)
