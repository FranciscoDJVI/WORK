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
                    "class": "bg-gray-400 rounded-2xl",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "bg-gray-400 rounded-2xl",
                }
            ),
            "password_1": forms.PasswordInput(
                attrs={
                    "class": "bg-gray-400 rounded-2xl",
                }
            ),
            "Password_2": forms.PasswordInput(
                attrs={
                    "class": "bg-gray-400 rounded-2xl",
                }
            ),
        }
