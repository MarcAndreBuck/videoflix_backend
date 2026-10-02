from django.urls import path

from .views import (
    ActivationView,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetView,
    RegistrationView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('activate/<uidb64>/<token>/', ActivationView.as_view(), name='activate'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path(
        'password_confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(),
        name='password_confirm',
    ),
]
