from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.middleware.csrf import get_token

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import CookieJWTAuthentication
from .serializers import (
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
)
from .utils import (
    blacklist_refresh_token,
    create_activation_response,
    create_invalid_activation_response,
    create_invalid_reset_response,
    create_login_response,
    create_logout_response,
    create_password_confirm_response,
    create_password_reset_response,
    create_refresh_error_response,
    create_refresh_response,
    create_registration_response,
    create_validation_error_response,
    enforce_csrf,
    get_valid_refresh_token,
    get_valid_user_from_token,
    revoke_access_token,
    send_activation_email,
    send_password_reset_email,
    set_jwt_cookies,
    set_new_password,
)


class RegistrationView(APIView):
    """View for user registration."""
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new user."""
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = default_token_generator.make_token(user)
            send_activation_email(user, token)
            return create_registration_response(user, token)
        return create_validation_error_response(serializer.errors)


class LoginView(APIView):
    """View for user login."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Authenticate a user."""
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            response = create_login_response(user)
            set_jwt_cookies(response, refresh)
            get_token(request)
            return response

        return create_validation_error_response(serializer.errors)


class LogoutView(APIView):
    """View for user logout."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Log out the authenticated user."""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return create_refresh_error_response(
                'Refresh token not provided.',
                status.HTTP_400_BAD_REQUEST,
            )
        if not blacklist_refresh_token(refresh_token):
            return create_refresh_error_response(
                'Invalid or expired refresh token.'
            )
        revoke_access_token(request.auth)
        return create_logout_response()


class TokenRefreshView(APIView):
    """View for refreshing the access token."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Refresh the access token using the refresh token cookie."""
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return create_refresh_error_response(
                'Refresh token not provided.',
                status.HTTP_400_BAD_REQUEST,
            )
        enforce_csrf(request)
        refresh = get_valid_refresh_token(refresh_token)
        if refresh is None:
            return create_refresh_error_response(
                'Invalid or expired refresh token.'
            )
        return create_refresh_response(refresh)


class ActivationView(APIView):
    """Activate a user account using an email verification link."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Validate the activation link and activate the user."""
        user = get_valid_user_from_token(uidb64, token)
        if user is None:
            return create_invalid_activation_response()

        user.is_active = True
        user.save(update_fields=["is_active"])
        return create_activation_response()


class PasswordResetView(APIView):
    """Request a password reset email."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Handle a password reset request."""
        serializer = PasswordResetSerializer(data=request.data)
        if not serializer.is_valid():
            return create_validation_error_response(serializer.errors)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            token = default_token_generator.make_token(user)
            send_password_reset_email(user, token)

        return create_password_reset_response()


class PasswordResetConfirmView(APIView):
    """Confirm a password reset and set a new password."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Handle the new password."""
        user = get_valid_user_from_token(uidb64, token)
        if user is None:
            return create_invalid_reset_response()

        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return create_validation_error_response(serializer.errors)

        set_new_password(
            user,
            serializer.validated_data['new_password'],
        )
        return create_password_confirm_response()
