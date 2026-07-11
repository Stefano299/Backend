from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'indirizzo', 'citta', 'codice_postale', 'numero_di_telefono', 'is_staff']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informazioni Aggiuntive', {'fields': ('indirizzo', 'citta', 'codice_postale', 'numero_di_telefono')}),
    )
    
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'username',
                    'password1',
                    'password2',
                    'first_name',
                    'last_name',
                    'email',
                    'indirizzo',
                    'citta',
                    'codice_postale',
                    'numero_di_telefono',
                ),
            },
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
