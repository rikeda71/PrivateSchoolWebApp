from django.test import TestCase
from django.urls import reverse, resolve
from django.forms import widgets
from accounts.views import Login
from accounts.forms import LoginForm
from accounts.models import User


class LoginViewTest(TestCase):

    def setUp(self):
        super().setUp()
        url = reverse('accounts:login')
        self.response = self.client.get(url)

    def test_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_class(self):
        view = resolve('/accounts/login/')
        self.assertEqual(view.func.view_class, Login)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_value_of_contain_form_inputs(self):
        self.assertContains(self.response, '<input', 4)


class LoginFormTest(TestCase):

    def setUp(self):
        super().setUp()
        self.form = LoginForm()

    def test_field_widget_type(self):
        self.assertEqual(widgets.TextInput,
                         self.form.fields['username'].widget.__class__)
        self.assertEqual(widgets.PasswordInput,
                         self.form.fields['password'].widget.__class__)


class LoginTest(TestCase):

    def setUp(self):
        super().setUp()
        self.credentials = {'last_name': 'last', 'first_name': 'first',
                            'email': 'hoge@example.com', 'password': 'hogehoge'}
        user = User.objects.create_user(**self.credentials)
        user.is_active = True
        user.save()

    def test_login_is_valid(self):
        response = self.client.post(reverse('accounts:login'),
                                    {'username': 'hoge@example.com',
                                     'password': 'hogehoge'})
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, '/accounts/')

    def test_login_is_invalid_with_missing_value(self):
        response = self.client.post(reverse('accounts:login'),
                                    {'username': 'hoge@example.com',
                                     'password': 'hogehuga'})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '正しいメールアドレスとパスワードを入力してください', 1)

    def test_login_is_invalid_with_missing_field(self):
        response = self.client.post(reverse('accounts:login'),
                                    {'email': 'hoge@example.com',
                                     'password': 'hogehoge'})
        self.assertEqual(200, response.status_code)
