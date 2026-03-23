import uuid
from django.db import models
from django.conf import settings


class EmergencyContact(models.Model):

    RELATIONSHIP_CHOICES = [
        ('family',    'Family'),
        ('friend',    'Friend'),
        ('colleague', 'Colleague'),
        ('other',     'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )
    name         = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default='other'
    )

    # Telegram verification fields
    telegram_id       = models.CharField(max_length=100, blank=True, null=True)
    telegram_verified = models.BooleanField(default=False)
    invite_token      = models.UUIDField(default=uuid.uuid4, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.name} ({self.user.email})"

    @property
    def invite_link(self):
        bot_username = settings.TELEGRAM_BOT_USERNAME
        return f"https://t.me/{bot_username}?start=verify_{self.invite_token}"