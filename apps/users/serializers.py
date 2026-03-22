from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ('email', 'full_name', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    invite_link = serializers.ReadOnlyField()

    class Meta:
        model  = User
        fields = (
            'id',
            'email',
            'full_name',
            'telegram_id',
            'telegram_verified',
            'invite_link',
            'created_at',
        )
        read_only_fields = (
            'id',
            'email',
            'telegram_id',
            'telegram_verified',
            'invite_link',
            'created_at',
        )