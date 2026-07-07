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
        group, _ = Group.objects.get_or_create(name='Customer')
        self.object.groups.add(group)
        return response
