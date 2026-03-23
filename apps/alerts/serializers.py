from rest_framework import serializers
from .models import Alert


class AlertCreateSerializer(serializers.ModelSerializer):
    front_photo     = serializers.ImageField(write_only=True, required=False)
    rear_photo      = serializers.ImageField(write_only=True, required=False)
    idempotency_key = serializers.CharField(
                        max_length=100,
                        required=False,
                        write_only=True)

    class Meta:
        model  = Alert
        fields = (
            'trigger_type',
            'latitude',
            'longitude',
            'front_photo',
            'rear_photo',
            'is_test',
            'idempotency_key',
        )

    def validate_trigger_type(self, value):
        valid = ['volume_button', 'shake', 'manual']
        if value not in valid:
            raise serializers.ValidationError(
                f"trigger_type must be one of: {valid}"
            )
        return value


class AlertResponseSerializer(serializers.ModelSerializer):
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