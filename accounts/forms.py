from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import EhpadProfile


class AccountLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input input-md w-full"


class EhpadRegistrationForm(UserCreationForm):
    email = forms.EmailField(label="Email professionnel")
    establishment_name = forms.CharField(label="Nom de l'établissement", max_length=200)
    establishment_address = forms.CharField(label="Adresse de l'établissement", max_length=255)
    contact_name = forms.CharField(label="Nom du contact", max_length=200)
    modules = forms.MultipleChoiceField(
        label="Dispositifs souhaités",
        choices=(
            ("spaces", "Espace Ouvert"),
            ("coworking", "Coworking"),
        ),
        widget=forms.CheckboxSelectMultiple,
        error_messages={"required": "Sélectionnez au moins un dispositif."},
    )

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != "modules":
                field.widget.attrs.setdefault("class", "input input-md w-full")
        self.fields["username"].label = "Identifiant"
        self.fields["username"].help_text = "Utilisé uniquement pour vous connecter."
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmer le mot de passe"

    def clean_modules(self):
        modules = self.cleaned_data["modules"]
        if not modules:
            raise forms.ValidationError("Sélectionnez au moins un dispositif.")
        return modules

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False
        if commit:
            user.save()
            EhpadProfile.objects.create(
                user=user,
                establishment_name=self.cleaned_data["establishment_name"],
                establishment_address=self.cleaned_data["establishment_address"],
                contact_name=self.cleaned_data["contact_name"],
                participates_in_spaces="spaces" in self.cleaned_data["modules"],
                participates_in_coworking="coworking" in self.cleaned_data["modules"],
            )
        return user
