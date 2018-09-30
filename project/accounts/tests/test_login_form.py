from django.test import TestCase
from accounts.forms import LoginForm
from accounts.models import User


class LoginFormTests(TestCase):

    def test_valid(self):
        params = dict(email='hoge@example.com', password='password')
        usermodel = User()
        form = LoginForm(params, instance=usermodel)
        self.assertTrue(form.is_valid())

    def test_invalid_with_email(self):
        params = dict(email='hoge', password='password')
        usermodel = User()
        form = LoginForm(params, instance=usermodel)
        self.assertFalse(form.is_valid())

    def test_invalid_with_password(self):
        params = dict(email='hoge@example.com', password='')
        usermodel = User()
        form = LoginForm(params, instance=usermodel)
        self.assertFalse(form.is_valid())
