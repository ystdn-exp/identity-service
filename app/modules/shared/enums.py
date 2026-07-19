from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


# Simplification: only email delivery is implemented for OTPs. Adding SMS
# would mean a new OTPType delivery layer (e.g. Eskiz) chosen
# by a per-user preference, plugged in next to send_otp_email the same way
# email is - the OTP creation/verification logic itself wouldn't change.
class OTPType(str, Enum):
    REGISTRATION = "registration"
    EMAIL_CHANGE = "email_change"
    PASSWORD_RESET = "password_reset"
