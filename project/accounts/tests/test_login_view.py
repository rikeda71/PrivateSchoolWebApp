from django.test import TestCase
from django.urls import reverse
from django.urls import resolve
from accounts.views import login_user
from accounts.models import User
from accounts.forms import LoginForm


def create_tmp_user(email, password):
    User.objects.create_user(email=email, password=password)


class LoginViewTests(TestCase):
    def setUp(self):
        url = reverse('accounts:login')
        self.response = self.client.get(url)

    def test_login_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_login_resolves_login_view(self):
        view = resolve('/accounts/login')
        self.assertEqual(view.func, login_user)

    def test_view_contains(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        self.assertContains(self.response, 'メールアドレス')
        self.assertContains(self.response, 'パスワード')

    def test_field_widget_type(self):
        form = self.response.context.get('login_form')
        self.assertIsInstance(form, LoginForm)


class SuccessfulLoginTest(TestCase):
    def setUp(self):
        create_tmp_user(email='hoge@example.com', password='password')
        url = reverse('accounts:login')
        data = {
            'email': 'hoge@example.com',
            'password': 'password',
        }
        self.response = self.client.post(url, data)
        self.index_url = reverse('accounts:index')

    def test_redirection(self):
        response = self.client.get(self.index_url)
        self.assertRedirects(self.response, self.index_url)

    def test_user_authentication(self):
        response = self.client.get(self.index_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidLoginTest(TestCase):
    def setUp(self):
        url = reverse('accounts:login')
        self.response = self.client.post(url, {})

    def test_login_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('login_form')
        self.assertTrue(form.errors)

    def test_no_login_user(self):
        user = self.response.context.get('user')
        self.assertFalse(user.is_authenticated)
