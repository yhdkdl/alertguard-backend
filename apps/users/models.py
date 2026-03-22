import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email      = models.EmailField(unique=True)
    full_name  = models.CharField(max_length=150)
    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Telegram fields — set by webhook, never by client directly
    telegram_id       = models.CharField(max_length=100, blank=True, null=True)
    telegram_verified = models.BooleanField(default=False)
    invite_token      = models.UUIDField(default=uuid.uuid4, unique=True)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name

    @property
    def invite_link(self):
        from django.conf import settings
        return (
            f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}"
            f"?start=verify_user_{self.invite_token}"
        )