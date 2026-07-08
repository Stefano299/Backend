from django.urls import path
from .views import homePageView, contactPageView

urlpatterns = [
    path("", homePageView, name="home"),
    path("contattaci/", contactPageView, name="contact"),
]

