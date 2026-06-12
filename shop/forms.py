from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image_url', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome del Prodotto'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descrizione...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'URL dell\'immagine'}),
            'categories': forms.CheckboxSelectMultiple(attrs={'class': 'category-checkboxes'}),
        }

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
