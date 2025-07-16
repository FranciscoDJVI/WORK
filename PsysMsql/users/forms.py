from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )
        labels = {
            "Username": "",
            "Email": "",
        }
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "border border-blue-950 p-2",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "border border-blue-950 p-2",
                }
            ),
            "password_1": forms.PasswordInput(
                attrs={"class": "border border-blue-950"}
            ),
            "Password_2": forms.PasswordInput(
                attrs={"class": "border border-blue-950"}
            ),
        }
