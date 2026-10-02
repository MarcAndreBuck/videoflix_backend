from datetime import datetime, timezone

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.middleware.csrf import CsrfViewMiddleware
from django.template.loader import render_to_string
from django.utils.encoding import (
    DjangoUnicodeDecodeError,
    force_bytes,
    force_str,
)
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from auth_app.models import RevokedAccessToken


def set_jwt_cookies(response, refresh):
    """Set access and refresh tokens as HTTP-only cookies."""
    set_access_token_cookie(response, refresh.access_token)
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )


def create_login_response(user):
    """Create the response for a successful login."""
    return Response(
        {
            "detail": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
            },
        },
        status=status.HTTP_200_OK,
    )


def delete_jwt_cookies(response):
    """Delete access and refresh token cookies."""
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')


def set_access_token_cookie(response, access_token):
    """Set the access token as an HTTP-only cookie."""

    response.set_cookie(
        key='access_token',
        value=str(access_token),
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )


def get_valid_refresh_token(refresh_token):
    """Return a valid refresh token or None."""
    try:
        return RefreshToken(refresh_token)
    except TokenError:
        return None


def create_refresh_error_response(
    detail, status_code=status.HTTP_401_UNAUTHORIZED
):
    """Create an error response for a refresh failure."""
    return Response(
        {'detail': detail},
        status=status_code,
    )


def create_refresh_response(refresh):
    """Create a response with a refreshed access token."""
    access_token = refresh.access_token
    response = Response(
        {
            'detail': 'Token refreshed',
            'access': str(access_token),
        },
        status=status.HTTP_200_OK,
    )
    set_access_token_cookie(response, access_token)
    return response


def revoke_access_token(token):
    """Record an access token as revoked until it expires."""
    RevokedAccessToken.objects.get_or_create(
        jti=token['jti'],
        defaults={
            'expires_at': datetime.fromtimestamp(token['exp'], tz=timezone.utc)
        },
    )


def create_logout_response():
    """Create the logout response and clear both JWT cookies."""
    response = Response(
        {
            'detail': (
                'Logout successful! All tokens will be deleted. '
                'Refresh token is now invalid.'
            )
        },
        status=status.HTTP_200_OK,
    )
    delete_jwt_cookies(response)
    return response


def send_password_reset_email(user, token):
    """Send an HTML password reset email to the user."""
    reset_link = create_password_reset_link(user, token)
    html_message = render_to_string(
        "auth_app/emails/password_reset_email.html",
        {"reset_link": reset_link, "logo_url": settings.LOGO_URL},
    )
    send_mail(
        subject="Reset your Password",
        message=f"Reset your password: {reset_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )


def send_activation_email(user, token):
    """Send an HTML activation email to the user."""
    activation_link = create_activation_link(user, token)
    html_message = render_to_string(
        "auth_app/emails/activation_email.html",
        {"activation_link": activation_link, "logo_url": settings.LOGO_URL},
    )
    send_mail(
        subject="Confirm your email",
        message=f"Activate your account: {activation_link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
    )


def create_activation_link(user, token):
    """Create an activation link for a user."""

    uid = urlsafe_base64_encode(force_bytes(user.pk))

    return (
        f"{settings.FRONTEND_URL.rstrip('/')}"
        f"/activate/{uid}/{token}/"
    )


def create_password_reset_link(user, token):
    """Create a password reset link for a user."""

    uid = urlsafe_base64_encode(force_bytes(user.pk))

    return (
        f"{settings.FRONTEND_URL.rstrip('/')}"
        f"/confirm-password/{uid}/{token}/"
    )


def get_user_from_uid(uidb64):
    """Return the user from an encoded ID or None."""

    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
    except (ValueError, DjangoUnicodeDecodeError):
        return None
    try:
        return get_user_model().objects.get(pk=user_id)
    except (get_user_model().DoesNotExist, ValueError, ValidationError):
        return None


def create_registration_response(user, token):
    """Create the response for a successful registration."""
    return Response(
        {
            "user": {"id": user.id, "email": user.email},
            "token": token,
        },
        status=status.HTTP_201_CREATED,
    )


def create_password_reset_response():
    """Create the response for a password reset request."""
    return Response(
        {'detail': 'An email has been sent to reset your password.'},
        status=status.HTTP_200_OK,
    )


def create_password_confirm_response():
    """Create the response for a successful password reset."""
    return Response(
        {'detail': 'Your Password has been successfully reset.'},
        status=status.HTTP_200_OK,
    )


def set_new_password(user, password):
    """Set and save a new password for a user."""
    user.set_password(password)
    user.save(update_fields=['password'])


def get_valid_user_from_token(uidb64, token):
    """Return the user if the token is valid, otherwise None."""
    user = get_user_from_uid(uidb64)
    if user is None:
        return None
    if not default_token_generator.check_token(user, token):
        return None
    return user


def create_invalid_reset_response():
    """Create the response for an invalid password reset link."""
    return Response(
        {'detail': 'Invalid or expired reset link.'},
        status=status.HTTP_400_BAD_REQUEST,
    )


def create_validation_error_response(errors):
    """Create a response for serializer validation errors."""
    return Response(
        errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


def create_activation_response():
    """Create the response for a successful account activation."""
    return Response(
        {"message": "Account successfully activated."},
        status=status.HTTP_200_OK,
    )


def create_invalid_activation_response():
    """Create the response for an invalid activation link."""
    return Response(
        {"detail": "Invalid activation link."},
        status=status.HTTP_400_BAD_REQUEST,
    )


def blacklist_refresh_token(refresh_token):
    """Blacklist a refresh token and return whether it succeeded."""
    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError:
        return False
    return True


def enforce_csrf(request):
    """Enforce CSRF validation when cookie security is enabled."""
    if not settings.JWT_COOKIE_SECURITY_ENABLED:
        return

    csrf_check = CsrfViewMiddleware(lambda req: None)
    csrf_check.process_request(request)
    failure = csrf_check.process_view(request, None, (), {})

    if failure:
        raise AuthenticationFailed('CSRF validation failed.')
