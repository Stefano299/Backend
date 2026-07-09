from django import forms
from .models import Order, DiscountCode

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Quantità',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px; display: inline-block;'})
    )
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'indirizzo', 'citta', 'codice_postale', 'numero_di_telefono', 'payment_method']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Il tuo nome'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Il tuo cognome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'La tua email'}),
            'indirizzo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Via/Piazza, Numero Civico'}),
            'citta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Roma'}),
            'codice_postale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50123'}),
            'numero_di_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +39 333 1234567'}),
            'payment_method': forms.RadioSelect(attrs={'class': 'payment-radio'}),
        }
        labels = {
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'email': 'Email',
            'payment_method': 'Metodo di Pagamento',
        }

    field_order = ['first_name', 'last_name', 'email', 'indirizzo', 'citta', 'codice_postale', 'numero_di_telefono', 'payment_method']


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_status']
        widgets = {
            'shipping_status': forms.Select(attrs={'class': 'form-control'}),
        }

class DiscountApplyForm(forms.Form):
    code = forms.CharField(label="Codice Sconto", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Inserisci il codice...'}))

class DiscountCodeForm(forms.ModelForm):
    class Meta:
        model = DiscountCode
        fields = ['code', 'amount']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
