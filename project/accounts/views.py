from django.shortcuts import render
from django.shortcuts import redirect
from .models import User
from accounts.forms import LoginForm
from accounts.forms import RegistrationForm
from django.contrib.auth import authenticate
from django.contrib.auth import login


def index(request):
    return render(request, 'accounts/index.html')


def login_user(request):
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        email = login_form['email'].value()
        password = login_form['password'].value()
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('accounts:index')
        else:
            login_form.add_error(None, 'メールアドレスかパスワードが間違っています')
            return render(request, 'accounts/login.html', {'login_form': login_form})
    else:
        login_form = LoginForm()
    return render(request, 'accounts/login.html', {'login_form': login_form})

def registration_user(request):
    if request.method == 'POST':
        registration_form = RegistrationForm(request.POST)
        last_name = registration_form['last_name'].value()
        first_name = registration_form['first_name'].value()
        email = registration_form['email'].value()
        password = registration_form['password'].value()
        if len(password) < 8:
            registration_form.add_error('password', 'パスワードは8文字以内で設定してください')
        if len(first_name) == 0:
            registration_form.add_error('first_name', '名前を入力してください')
        if len(last_name) == 0:
            registration_form.add_error('last_name', '名前を入力してください')

        if registration_form.has_error('password') or\
                registration_form.has_error('email') or\
                registration_form.has_error('first_name') or\
                registration_form.has_error('last_name'):
            return render(request, 'accounts/registration.html', {'registration_form': registration_form})

        user = User.objects.create_user(email=email,
                                        password=password,
                                        first_name=first_name,
                                        last_name=last_name,)
        return redirect('accounts:index')
    else:
        registration_form = RegistrationForm()
    return render(request, 'accounts/registration.html', {'registration_form': registration_form})
