import calendar
from collections import deque
import datetime
from django.conf import settings
from django.contrib import messages
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
from .models import User, PDFFile, Shift
from .forms import (
    LoginForm, RegistrationForm, MyPasswordChangeForm, UploadFileForm
)
from accounts.tasks import shiftregistrations
from project.settings import MEDIA_ROOT


class Index(generic.TemplateView):
    template_name = 'accounts/index.html'


class Login(LoginView):
    """
    ログインビュー
    """

    form_class = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        result = super().form_valid(form)
        messages.success(
            self.request, 'ログインしました'
        )
        return result


class Logout(LoginRequiredMixin, LogoutView):
    """
    ログアウトページ
    """

    template_name = 'accounts/index.html'


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


def upload_file(request):
    """
    シフトアップロードビュー
    """

    if not request.user.is_superuser:
        return redirect('accounts:index')
    if request.method == 'POST':
        form = UploadFileForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # ファイル処理
            pdf = form.save()
            shiftregistrations.delay(pdf.pk, MEDIA_ROOT + '/' + str(pdf.attach))
            messages.success(
                request, 'シフトを登録しました．反映にしばらく時間がかかります'
            )
            return redirect('accounts:index')
    else:
        form = UploadFileForm()
    return render(request, 'accounts/upload_pdf.html', {'form': form})


class BaseCalendarMixin:
    """
    Calendar Mixin super class
    """

    first_weekday = 6
    week_names = ['月', '火', '水', '木', '金', '土', '日']

    def setup(self):
        self._calendar = calendar.Calendar(self.first_weekday)

    def get_week_names(self):
        week_names = deque(self.week_names)
        week_names.rotate(-self.first_weekday)
        return week_names


class MonthCalendarMixin(BaseCalendarMixin):
    """
    Month Calendar Mixin
    """

    @staticmethod
    def get_previous_month(date):
        """
        return previous month
        """

        if date.month == 1:
            return date.replace(year=date.year - 1, month=12, day=1)
        return date.replace(month=date.month - 1, day=1)

    @staticmethod
    def get_next_month(date):
        """
        return next month
        """

        if date.month == 12:
            return date.replace(year=date.year + 1, month=1, day=1)
        return date.replace(month=date.month + 1, day=1)

    def get_current_month(self):
        """
        return current month
        """

        month = self.kwargs.get('month')
        year = self.kwargs.get('year')
        if month and year:
            month = datetime.date(year=int(year), month=int(month), day=1)
        else:
            month = datetime.date.today().replace(day=1)
        return month

    def get_month_days(self, date):
        return self._calendar.monthdatescalendar(date.year, date.month)

    def get_month_shifts(self, days, user):
        """
        return shifts in days
        """

        day_with_shifts = []
        for week in days:
            week_shifts = []
            for day in week:
                lookup = {'day': day, 'user_id': user}
                queryset = Shift.objects.filter(**lookup)
                segments = list(sorted(set([q.segment for q in queryset])))
                # シフト順の調整
                for s in ['Z', 'Y', 'X']:
                    if s in segments:
                        segments.remove(s)
                        segments.insert(0, s)
                week_shifts.append((day, "".join(segments)))
            day_with_shifts.append(week_shifts)
        return day_with_shifts

    def get_month_calendar(self, user):
        """
        return month calendar information
        """

        self.setup()
        current_month = self.get_current_month()
        calendar_data = {
            'now': datetime.date.today(),
            'days': self.get_month_days(current_month),
            'current': current_month,
            'previous': self.get_previous_month(current_month),
            'next': self.get_next_month(current_month),
            'week_names': self.get_week_names(),
        }
        calendar_data['days'] = self.get_month_shifts(calendar_data['days'], user)
        return calendar_data


class MonthCalendar(MonthCalendarMixin, generic.TemplateView):
    """
    Month Calendar View
    """

    template_name = 'accounts/month.html'

    def get_context_data(self, user, **kwargs):
        context = super().get_context_data(**kwargs)
        context['month'] = self.get_month_calendar(user)
        return context

    def get(self, request, **kwargs):
        context = self.get_context_data(user=request.user)
        return self.render_to_response(context)


class ShiftView(generic.TemplateView):
    """
    Shift View in a day
    """

    template_name = 'accounts/shift.html'

    def get_context_data(self, user, **kwargs):
        context = super().get_context_data(**kwargs)
        year = kwargs.get('year')
        month = kwargs.get('month')
        day = kwargs.get('day')
        segment = ('X', 'Y', 'Z', 'A', 'B', 'C', 'D')
        context['shift'] = {}
        for s in segment:
            shifts = Shift.objects.filter(user_id=user, day=datetime.date(year=year, month=month, day=day), segment=s)
            if len(shifts) > 0:
                context['shift'][s] = shifts
        return context

    def get(self, request, **kwargs):
        context = self.get_context_data(user=request.user, **kwargs)
        print(context)
        return self.render_to_response(context)
