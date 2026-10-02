from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'confirmed_password')
        extra_kwargs = {
            "email": {"required": True},
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        """Validate that the email address is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Please check your input and try again.'
            )
        return value

    def validate_password(self, value):
        """Validate the password using Django's password validators."""
        validate_password(value)
        return value

    def validate(self, data):
        """Validate that both passwords match."""
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError(
                "Please check your input and try again."
            )
        return data

    def create(self, validated_data):
        """Create an inactive user with their email as username."""
        validated_data.pop("confirmed_password")
        email = validated_data["email"]

        return User.objects.create_user(
            username=email,
            email=email,
            password=validated_data["password"],
            is_active=False,
        )


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Validate the user credentials."""
        user = authenticate(
            username=data.get('email'),
            password=data.get('password')
        )
        if not user:
            raise AuthenticationFailed("Invalid email or password.")
        data['user'] = user
        return data


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming a password reset."""

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        """Validate the new password using Django's password validators."""
        validate_password(value)
        return value

    def validate(self, data):
        """Validate that both passwords match."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                "Passwords do not match."
            )
        return data


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset requests."""

    email = serializers.EmailField()
