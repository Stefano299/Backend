from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    indirizzo = models.CharField(max_length=255, blank=True, null=True)
    citta = models.CharField(max_length=100, blank=True, null=True)
    codice_postale = models.CharField(max_length=20, blank=True, null=True)
    numero_di_telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username

