import logging
import random
import secrets
import string

logger = logging.getLogger(__name__)


def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def generate_token(length=40):
    return secrets.token_hex(length // 2)


def send_otp(user, otp):
    # No SMS/email provider is configured yet - log it so it's visible during development.
    logger.info("OTP for %s: %s", user.username, otp)
