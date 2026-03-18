from rest_framework import serializers
from .models import EmergencyContact


class EmergencyContactSerializer(serializers.ModelSerializer):

    invite_link       = serializers.ReadOnlyField()
    telegram_verified = serializers.ReadOnlyField()

    class Meta:
        model  = EmergencyContact
        fields = (
            'id',
            'name',
            'phone_number',
            'relationship',
            'telegram_id',
            'telegram_verified',
            'invite_link',
            'created_at',
        )
        read_only_fields = ('id', 'telegram_id', 'telegram_verified', 'invite_link', 'created_at')

    def validate(self, attrs):
        request = self.context.get('request')
        user    = request.user

        if self.instance is None:
            existing_count = user.emergency_contacts.count()
            if existing_count >= 3:
                raise serializers.ValidationError(
                    "You can have a maximum of 3 emergency contacts."
                )
        return attrs