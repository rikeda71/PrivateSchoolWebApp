from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login
from django.contrib.auth import login
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.signing import dumps, loads
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views import generic
from .models import User
from .forms import (
    LoginForm, RegistrationForm, MyPasswordChangeForm
)


class Index(generic.TemplateView):
    template_name = 'accounts/index.html'


class Login(LoginView):
    """
    ログインビュー
    """

    form_class = LoginForm
    template_name = 'accounts/login.html'


class Logout(LoginRequiredMixin, LogoutView):
    """
    ログアウトページ
    """

    template_name = 'accounts/index.html'


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


class UserRegister(generic.CreateView):
    """
    ユーザ仮登録
    """

    template_name = 'accounts/registration.html'
    form_class = RegistrationForm

    def form_valid(self, form):
        """
        仮登録と本登録メールの発行
        """

        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # アクティベーションURLの送付
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'token': dumps(user.pk),
            'user': user
        }
        subject_template = get_template('accounts/mail_template/register/subject.txt')
        subject = subject_template.render(context)
        subject = subject.replace('\n', '')

        message_template = get_template('accounts/mail_template/register/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        return redirect('accounts:user_register_done')


class UserRegisterDone(generic.TemplateView):
    """
    ユーザ仮登録をした
    """
    template_name = 'accounts/registration_done.html'


class UserRegisterComplete(generic.TemplateView):
    """
    メール内URLアクセス後のユーザ本登録
    """

    template_name = 'accounts/registration_complete.html'
    timeout_seconds = getattr(settings, 'ACTIVATION_TIMEOUT_SECONDS', 60 * 60 * 24)

    def get(self, request, **kargs):
        """
        tokenが正しければ本登録
        """
        token = kargs.get('token')
        try:
            user_pk = loads(token, max_age=self.timeout_seconds)
        # timeout
        except SignatureExpired:
            return HttpResponseBadRequest()
        # token misses
        except BadSignature:
            return HttpResponseBadRequest

        else:
            try:
                user = User.objects.get(pk=user_pk)
            except User.DoenNotExist:
                return HttpResponseBadRequest()
            else:
                if not user.is_active:
                    # 本登録
                    user.is_active = True
                    user.save()
                    return super().get(request, **kargs)
        return HttpResponseBadRequest()


class PasswordChange(PasswordChangeView):
    """
    パスワード変更ビュー
    """

    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('accounts:password_change_done')
    template_name = 'accounts/password_change.html'


class PasswordChangeDone(PasswordChangeDoneView):
    """
    パスワード変更完了ビュー
    """

    template_name = 'accounts/password_change_done.html'
