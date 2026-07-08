from .forms import CustomUserCreationForm, UserProfileForm
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from .models import CustomUser

class SignUpView(SuccessMessageMixin, generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
    success_message = "Registrazione completata con successo! Ora puoi effettuare l'accesso."
    
    def form_valid(self, form):
        response = super().form_valid(form)
        group, _ = Group.objects.get_or_create(name='Customer')
        self.object.groups.add(group)
        return response

class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = CustomUser
    form_class = UserProfileForm
    template_name = 'registration/profile.html'
    success_url = reverse_lazy('profile')
    success_message = "Profilo aggiornato con successo."

    def get_object(self, queryset=None):
        return self.request.user
