from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from myapp.utils import generate_otp, generate_token


class User(AbstractUser):
    ROLE_CHOICES = {
        'superadmin': 'Super Admin',
        'admin': 'Admin',
        'user': 'User',
    }
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True, default='user')
    phone = models.CharField(max_length=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Token(models.Model):
    token = models.CharField(max_length=64, unique=True)
    otp = models.CharField(max_length=10, null=True, blank=True)
    fcm_id = models.CharField(max_length=50, null=True, blank=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='tokens')
    is_verified = models.BooleanField(default=False)
    otp_expired_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.token}"

    def is_otp_expired(self):
        if not self.otp_expired_at:
            return True
        return timezone.now() > self.otp_expired_at

    def is_token_expired(self):
        if not self.expired_at:
            return True
        return timezone.now() > self.expired_at

    def verify_otp(self, otp):
        if self.is_otp_expired():
            return False
        if self.otp != otp:
            return False
        self.is_verified = True
        self.otp = None
        self.expired_at = timezone.now() + timedelta(days=settings.TOKEN_VALID_DAYS)
        self.save(update_fields=['is_verified', 'otp', 'expired_at', 'updated_at'])
        return True

    def refresh(self):
        self.token = generate_token()
        self.expired_at = timezone.now() + timedelta(days=settings.TOKEN_VALID_DAYS)
        self.save(update_fields=['token', 'expired_at', 'updated_at'])
        return self

    def regenerate_otp(self):
        self.otp = generate_otp()
        self.otp_expired_at = timezone.now() + timedelta(minutes=settings.OTP_VALID_MINUTES)
        self.is_verified = False
        self.save(update_fields=['otp', 'otp_expired_at', 'is_verified', 'updated_at'])
        return self.otp

    @classmethod
    def create_for_user(cls, user, fcm_id=None):
        token = cls.objects.create(
            token=generate_token(),
            otp=generate_otp(),
            fcm_id=fcm_id,
            user=user,
            otp_expired_at=timezone.now() + timedelta(minutes=settings.OTP_VALID_MINUTES),
        )
        return token
