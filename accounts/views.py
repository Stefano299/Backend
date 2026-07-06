from .forms import CustomUserCreationForm
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views import generic

class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)

        # Aggiunge nuovo utente al gruppo corretto
        role = form.cleaned_data.get('role')
        if role == 'seller':
            group = Group.objects.get(name='Seller')
        else:
            group = Group.objects.get(name='Customer')
        self.object.groups.add(group)
        return response
