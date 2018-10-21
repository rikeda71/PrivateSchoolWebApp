from django.urls import path
from django.contrib.auth.decorators import (
    login_required, permission_required
)
from . import views

app_name = 'accounts'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', login_required(views.LogoutView.as_view()), name='logout'),
    path('registration/', views.UserRegister.as_view(), name='user_register'),
    path('registration/done', views.UserRegisterDone.as_view(), name='user_register_done'),
    path('registration/complete/<token>', views.UserRegisterComplete.as_view(), name='user_register_complete'),
    path('password_change/', login_required(views.PasswordChange.as_view()), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),
    path('upload/', views.upload_file, name='upload'),
    path('month/<int:year>/<int:month>/', login_required(views.MonthCalendar.as_view()), name='month'),
    path('shift/<int:year>/<int:month>/<int:day>/', login_required(views.ShiftView.as_view()), name='shift'),
]
