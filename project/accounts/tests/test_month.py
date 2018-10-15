from django.test import TestCase
from django.urls import reverse, resolve
from accounts.models import User
from accounts.views import MonthCalendar


class MonthCalendarViewTest(TestCase):

    def setUp(self):
        super().setUp()
        self.credentials = {'last_name': 'last', 'first_name': 'first',
                            'email': 'hoge@example.com', 'password': 'hogehoge'}
        user = User.objects.create_user(**self.credentials)
        user.is_active = True
        user.save()
        url = reverse('accounts:month', kwargs={'year': 2018, 'month': 10})
        self.client.login(**{'email': 'hoge@example.com', 'password': 'hogehoge'})
        self.response = self.client.get(url)

    def test_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_class(self):
        view = resolve('/accounts/month/2018/10/')
        self.assertEqual(view.func.view_class, MonthCalendar)

    def test_value_of_contain_nextmonth_path(self):
        self.assertContains(self.response, '/accounts/month/2018/11/')

    def test_value_of_contain_previousmonth_path(self):
        self.assertContains(self.response, '/accounts/month/2018/9/')
