from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "confirmed_password")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Please check your input and try again."
            )
        return value

    def validate(self, data):
        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError(
                "Please check your input and try again."
            )
        return data

    def create(self, validated_data):
        validated_data.pop("confirmed_password")
        email = validated_data["email"]
        password = validated_data["password"]
        return User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=False,
        )
