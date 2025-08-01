from django.utils.text import phone2numeric
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User, Group

# MODELS
from . import models


class ProductForm(forms.ModelForm):
    class Meta:
        model = models.Products
        labels = {
            "name": "",
            "price": "",
            "description": "",
        }
        field = ["name", "price", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Producto",
                    "class": "bg-gray-400 p-2 text-cyan-950 rounded-2xl",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "placeholder": "Precio",
                    "class": "bg-gray-400 p-2 text-cyan-950 rounded-2xl",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Descripción...",
                    "class": "bg-gray-400 p-2 rounded-2x1 text-cyan-950 rounded-2xl",
                }
            ),
        }

        exclude = ["idproduct"]


class DeleteProductForm(forms.ModelForm):
    class Meta:
        model = models.Products
        field = ["name"]
        labels = {"name": ""}
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Buscar producto",
                    "class": "bg-gray-400 text-cyan-950 p-2 rounded-2xl",
                }
            )
        }

        exclude = ["idproduct", "price", "description"]


class SearchProduct(forms.ModelForm):
    class Meta:
        model = models.Products
        fields = ["name"]
        labels = {"name": ""}
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "buscar",
                    "class": "bg-gray-400 text-cyan-950 border p-2 rounded-2xl",
                }
            )
        }

        exclude = ["idproduct", "price", "description"]


class SellForm(forms.ModelForm):
    class Meta:
        model = models.Sell
        fields = ["id_product", "totalsell"]
        labels = {
            "totalsell": "",
            "id_product": "",
        }
        widgets = {
            "totalsell": forms.NumberInput(
                attrs={
                    "placeholder": "cantidad",
                    "class": "bg-gray-400  p-2 m-5 w-40 text-cyan-950 rounded-2xl font-extrabold",
                }
            ),
            "id_product": forms.Select(
                attrs={
                    "placeholder": "Nombre",
                    "class": "bg-gray-400 p-2 italic text-cyan-950 rounded-2xl font-extrabold",
                }
            ),
        }


class StockForm(forms.ModelForm):
    class Meta:
        model = models.Stock
        fields = ["id_products", "quantitystock"]
        labels = {
            "id_products": "name",
            "quantitystock": "",
        }
        widgets = {
            "id_products": forms.Select(
                attrs={
                    "placeholder": "id_product",
                    "class": "bg-gray-400 text-cyan-950 border border-gray-400 p-2 m-5 rounded-2xl",
                }
            ),
            "quantitystock": forms.NumberInput(
                attrs={
                    "placeholder": "cantidad",
                    "class": "bg-gray-400 text-cyan-950  border border-gray-400 p-2 m-5 rounded-2xl",
                }
            ),
        }


class SentSellForm(forms.Form):
    action_type = forms.CharField(widget=forms.HiddenInput(), initial="sent_sell")
    pass


class AssginUserToGroupForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="seleccionar usuario",
        widget=forms.Select(attrs={"class": "border border-gray-400 text-xm p-2 m-4"}),
    )

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all().order_by("name"),
        label="",
        widget=forms.CheckboxSelectMultiple(attrs={"class": "p-2"}),
    )


class RegisterSellDetailForm(forms.ModelForm):
    OPTIONS_TYPE_PAY = [
        (
            "Efectivo",
            "Efectivo",
        ),
        ("trasnferencia", "trasnferencia"),
        ("tarjeta credito", "tarjeta crédito"),
        ("tarjeta debito", "tarjeta débito"),
    ]
    type_pay = forms.ChoiceField(
        choices=OPTIONS_TYPE_PAY,
        label="",
        initial="Efectivo",
        widget=forms.Select(
            attrs={"class": "bg-gray-400 p-2 text-cyan-950 rounded-2xl font-extrabold"}
        ),
    )
    OPTIONS_STATE_SELL = [
        (
            "Pagado",
            "Pagado",
        ),
        ("en espera", "en espera"),
    ]
    state_sell = forms.ChoiceField(
        choices=OPTIONS_STATE_SELL,
        label="",
        initial="Pagado",
        widget=forms.Select(
            attrs={"class": "bg-gray-400 p-2  text-cyan-950 rounded-2xl font-extrabold"}
        ),
    )

    class Meta:
        model = models.RegistersellDetail
        fields = ["type_pay", "state_sell", "notes"]
        labels = {
            "notes": "",
        }
        widgets = {
            "notes": forms.TextInput(
                attrs={
                    "placeholder": "coment.",
                    "class": "bg-gray-400 p-2 italic text-cyan-950 rounded-2xl font-extrabold",
                }
            ),
        }


class ClientsForm(forms.ModelForm):
    class Meta:
        model = models.Clients
        fields = "__all__"
        labels = {
            "name": "",
            "email": "",
            "direction": "",
            "telephone": "",
            "nit": "",
            "country": "",
            "departament": "",
            "city": "",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Nombre/Razón social",
                    "class": "border bg-gray-400 border-cyan-950  text-cyan-950 p-2 m-5",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "border bg-gray-400 border-cyan-950  text-cyan-950 p-2 m-5"
                }
            ),
            "direction": forms.TextInput(
                attrs={
                    "placeholder": "Dirección",
                    "class": "border bg-gray-400 border-cyan-950  text-cyan-950 p-2 m-5",
                }
            ),
            "telephone": forms.TextInput(
                attrs={
                    "placeholder": "Telefono",
                    "class": "border bg-gray-400 border-cyan-950  text-cyan-950 p-2 m-5",
                }
            ),
            "nit": forms.TextInput(
                attrs={
                    "placeholder": "nit",
                    "class": "border bg-gray-400 border-cyan-950  text-cyan-950 p-2 m-5",
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "placeholder": "País",
                    "class": "border bg-gray-400 border-cyan-950  text-cyan-950 p-2 m-5",
                }
            ),
            "departament": forms.TextInput(
                attrs={
                    "placeholder": "Departamento",
                    "class": "border bg-gray-400 border-cyan-950  text-cyan-950 p-2 m-5",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "placeholder": "Ciudad",
                    "class": "border bg-gray-400 border-cyan-950  text-cyan-950 p-2 m-5",
                }
            ),
        }


class SearchEmailForm(forms.Form):
    query = forms.CharField(
        label="Buscar",
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "bg-gray-400 text-cyan-950 font-extrabold rounded-2xl p-1"}
        ),
    )
