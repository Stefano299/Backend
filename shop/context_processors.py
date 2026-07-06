# Rende la variabile cart disponibile in tutti i template per mostrare nell'UI 
# il numero di prodotti nel carrello

from .cart import Cart

def cart(request):
    return {'cart': Cart(request)}
