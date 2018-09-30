from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('index', views.index, name='index'),
    path('login', views.login_user, name='login'),
    path('registration', views.registration_user, name='registration'),
]
