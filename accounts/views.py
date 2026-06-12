from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views import generic

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)

        # Aggiunge nuovo utente al gruppo costumer
        customer_group = Group.objects.get(name='Customer')
        self.object.groups.add(customer_group)
