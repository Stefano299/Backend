from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


# Creo due mixin per evitare di ripetere sempre le stesse righe, sfruttando le CBV
class ManagerFormMixin(LoginRequiredMixin, PermissionRequiredMixin):
    #Mixin comune per le viste Create/Update del Manager.
    template_name = 'catalog/entity_form.html'
    success_url = reverse_lazy('orders:manager_dashboard')
    entity_title = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['entity_title'] = self.entity_title
        return context

class ManagerDeleteMixin(LoginRequiredMixin, PermissionRequiredMixin):
    #Mixin comune per le viste Delete del Manager.
    success_url = reverse_lazy('orders:manager_dashboard')
    http_method_names = ['post']
