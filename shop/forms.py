from django import forms
from .models import Product, Category, Order, Review

class CustomClearableFileInput(forms.ClearableFileInput):
    template_name = 'shop/widgets/custom_clearable_file_input.html'

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'discount_price', 'stock', 'image', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome del Prodotto'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descrizione...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'placeholder': 'Lascia vuoto se non scontato'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'image': CustomClearableFileInput(attrs={'class': 'form-control'}),
            'categories': forms.CheckboxSelectMultiple(attrs={'class': 'category-checkboxes'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        discount_price = cleaned_data.get('discount_price')
        
        if price is not None and discount_price is not None:
            if discount_price >= price:
                self.add_error('discount_price', 'Il prezzo scontato deve essere inferiore al prezzo originale.')
        return cleaned_data

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome della Categoria'}),
        }

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Quantità',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': 'width: 80px; display: inline-block;'})
    )
    override = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class OrderCreateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=150,
        label='Nome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Il tuo nome'})
    )
    last_name = forms.CharField(
        max_length=150,
        label='Cognome',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Il tuo cognome'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'La tua email'})
    )

    PAYMENT_METHOD_CHOICES = [
        ('card', 'Carta di Credito'),
        ('paypal', 'PayPal'),
        ('transfer', 'Bonifico Bancario'),
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'payment-radio'}),
        initial='card',
        label='Metodo di Pagamento'
    )

    class Meta:
        model = Order
        fields = ['indirizzo', 'citta', 'codice_postale', 'numero_di_telefono', 'payment_method']
        widgets = {
            'indirizzo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Via/Piazza, Numero Civico'}),
            'citta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Roma'}),
            'codice_postale': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50123'}),
            'numero_di_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +39 333 1234567'}),
        }

    field_order = ['first_name', 'last_name', 'email', 'indirizzo', 'citta', 'codice_postale', 'numero_di_telefono', 'payment_method']


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_status']
        widgets = {
            'shipping_status': forms.Select(attrs={'class': 'form-control'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Scrivi la tua recensione...'}),
        }


