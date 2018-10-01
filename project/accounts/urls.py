from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login_user, name='login'),
    path('registration/', views.UserRegister.as_view(), name='user_register'),
    path('registration/done', views.UserRegisterDone.as_view(), name='user_register_done'),
    path('registration/complete/<token>', views.UserRegisterComplete.as_view(), name='user_register_complete'),
    path('password_change', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done', views.PasswordChangeDone.as_view(), name='password_change_done'),
]
