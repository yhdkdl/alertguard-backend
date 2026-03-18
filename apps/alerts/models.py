from django.db import models
from django.conf import settings


class Alert(models.Model):

    TRIGGER_CHOICES = [
        ('volume_button', 'Volume Button'),
        ('shake',         'Shake'),
        ('manual',        'Manual'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent',    'Sent'),
        ('failed',  'Failed'),
    ]

    user            = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    trigger_type    = models.CharField(max_length=20, choices=TRIGGER_CHOICES)
    latitude        = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude       = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    front_photo_url = models.URLField(blank=True, null=True)
    rear_photo_url  = models.URLField(blank=True, null=True)
    status          = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_test         = models.BooleanField(default=False)
    created_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert by {self.user.email} at {self.created_at}"