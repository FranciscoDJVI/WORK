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
                    "placeholder": "Name product",
                    "class": "bg-white italic border border-gray-400 p-2 text-blue-950",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "placeholder": "Enter price",
                    "class": "bg-white italic border  border-gray-400  p-2 text-blue-950",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Description...",
                    "class": "bg-white italic border border-gray-400  p-2 rounded-2x1 h-50  w-100  text-blue-950",
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
                    "placeholder": "Search product ",
                    "class": "bg-white text-blue-950 italic border border-blue-950 p-2",
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
                    "placeholder": "Search product ",
                    "class": "bg-white text-blue-950 border border-gray-400 p-2 italic",
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
                    "placeholder": "Quantiity",
                    "class": "bg-white border border-gray-400 p-2 italic m-5 w-20 text-black",
                }
            ),
            "id_product": forms.Select(
                attrs={
                    "placeholder": "Name",
                    "class": "bg-white  border border-gray-400 p-2 italic text-black",
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
                    "class": "bg-white text-blue-950 border border-gray-400 p-2 italic m-5 w-30",
                }
            ),
            "quantitystock": forms.NumberInput(
                attrs={
                    "placeholder": "quantity",
                    "class": "bg-white text-blue-950  border border-gray-400 p-2 italic m-5 text-blue-950",
                }
            ),
        }


class SentSellForm(forms.Form):
    action_type = forms.CharField(widget=forms.HiddenInput(), initial="sent_sell")
    pass


class AssginUserToGroupForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("username"),
        label="select user",
        empty_label="---seleccionar---",
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
            "efectivo",
            "efectivo",
        ),
        ("trasnferencia", "trasnferencia"),
        ("tarjeta_credito", "tarjeta crédito"),
        ("tarjeta_debito", "tarjeta débito"),
    ]
    type_pay = forms.ChoiceField(
        choices=OPTIONS_TYPE_PAY,
        label="",
        initial="efectivo",
        widget=forms.Select(
            attrs={"class": "bg-white border border-gray-400 p-2 italic text-black"}
        ),
    )
    OPTIONS_STATE_SELL = [
        (
            "pagado",
            "pagado",
        ),
        ("en espera", "en espera"),
    ]
    state_sell = forms.ChoiceField(
        choices=OPTIONS_STATE_SELL,
        label="",
        initial="pagado",
        widget=forms.Select(
            attrs={"class": "bg-white border border-gray-400 p-2 italic text-black"}
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
                    "class": "bg-white border border-gray-400 p-2 italic text-black",
                }
            ),
        }

class ClientsForm(forms.ModelForm):
    
    class Meta:
        model = models.Clients
        fields = "__all__"
        labels = {
            "name":"",
            "email":"",
            "direction":"",
            "telephone":"",
            "nit":"",
            "country":"",
            "departament":"",
            "city":"",
            
        }
        widgets = {
            "name": forms.TextInput(
                attrs = {
                    "placeholder":"name/enterprise",
                    "class":"border border-blue-950 p-2 m-5"
                }
            ),
            "email": forms.EmailInput(
                attrs = {
                    "class":"border border-blue-950 p-2 m-5"
                }
            ),
            "direction": forms.TextInput(
                attrs = {
                    "placeholder":"direction",
                    "class":"border border-blue-950 p-2 m-5"
                }
            ),
            "telephone": forms.TextInput(
                attrs = {
                    "placeholder":"telephone",
                    "class":"border border-blue-950 p-2 m-5"
                }
            ),
            "nit": forms.TextInput(
                attrs = {
                    "placeholder":"nit",
                    "class":"border border-blue-950 p-2 m-5"
                }
            ),
            "country": forms.TextInput(
                attrs = {
                    "placeholder":"country",
                    "class":"border border-blue-950 p-2 m-5"
                }
            ),
            "departament": forms.TextInput(
                attrs = {
                    "placeholder":"departament",
                    "class":"border border-blue-950 p-2 m-5"
                }
            ),
            "city": forms.TextInput(
                attrs = {
                    "placeholder":"city",
                    "class":"border border-blue-950 p-2 m-5"
                }
            ),
            
        }
        

class SearchEmailForm(forms.Form):
    query = forms.CharField(
        label="Buscar",max_length=100,
        widget=forms.TextInput(attrs={"class":"bg-white italic text-black font-extrabold rounded-2xl p-1"})
        )
    