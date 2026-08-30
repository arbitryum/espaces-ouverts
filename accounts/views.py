from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import AccountLoginForm, EhpadRegistrationForm


class EhpadRegistrationView(CreateView):
    form_class = EhpadRegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:registration_pending")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            "Votre demande a été envoyée. Elle sera examinée par notre équipe.",
        )
        return response


class RegistrationPendingView(TemplateView):
    template_name = "accounts/registration_pending.html"


class AccountLoginView(LoginView):
    authentication_form = AccountLoginForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        profile = getattr(form.get_user(), "ehpad_profile", None)
        if profile is None or not profile.is_approved:
            form.add_error(None, "Votre compte est en attente de validation.")
            return self.form_invalid(form)
        return super().form_valid(form)


class AccountLogoutView(LogoutView):
    next_page = reverse_lazy("home:index")
