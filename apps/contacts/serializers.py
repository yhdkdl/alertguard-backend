from rest_framework import serializers
from .models import EmergencyContact


class EmergencyContactSerializer(serializers.ModelSerializer):

    class Meta:
        model  = EmergencyContact
        fields = (
            'id',
            'name',
            'phone_number',
            'telegram_id',
            'relationship',
            'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def validate(self, attrs):
        request = self.context.get('request')
        user    = request.user

        # On create (no instance yet), check the 3-contact limit
        if self.instance is None:
            existing_count = user.emergency_contacts.count()
            if existing_count >= 3:
                raise serializers.ValidationError(
                    "You can have a maximum of 3 emergency contacts."
                )

        return attrs