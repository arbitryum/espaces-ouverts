from django.urls import path

from .views import (
    AccountLoginView,
    AccountLogoutView,
    EhpadRegistrationView,
    RegistrationPendingView,
)

app_name = "accounts"

urlpatterns = [
    path("inscription/", EhpadRegistrationView.as_view(), name="register"),
    path("inscription/en-attente/", RegistrationPendingView.as_view(), name="registration_pending"),
    path("connexion/", AccountLoginView.as_view(), name="login"),
    path("deconnexion/", AccountLogoutView.as_view(), name="logout"),
]
