from rest_framework import serializers
from .models import Alert


class AlertCreateSerializer(serializers.ModelSerializer):
    """Used for incoming POST requests from Flutter."""
    front_photo = serializers.ImageField(write_only=True, required=False)
    rear_photo  = serializers.ImageField(write_only=True, required=False)

    class Meta:
        model  = Alert
        fields = (
            'trigger_type',
            'latitude',
            'longitude',
            'front_photo',
            'rear_photo',
            'is_test',
        )

    def validate_trigger_type(self, value):
        valid = ['volume_button', 'shake', 'manual']
        if value not in valid:
            raise serializers.ValidationError(
                f"trigger_type must be one of: {valid}"
            )
        return value


class AlertResponseSerializer(serializers.ModelSerializer):
    """Used for outgoing responses back to Flutter."""

    class Meta:
        model  = Alert
        fields = (
            'id',
            'trigger_type',
            'latitude',
            'longitude',
            'front_photo_url',
            'rear_photo_url',
            'status',
            'is_test',
            'created_at',
        )
        read_only_fields = fields