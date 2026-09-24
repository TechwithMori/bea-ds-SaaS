"""Auth serializers."""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Create a merchant account. Password is write-only."""

    password = serializers.CharField(write_only=True, min_length=10)

    class Meta:
        model = User
        fields = ("id", "email", "password", "first_name", "last_name", "company_name")
        read_only_fields = ("id",)

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "company_name")
        read_only_fields = fields
