from django.test import TestCase
from accounts.forms import RegistrationForm
from accounts.models import User


class RegistrationFormTests(TestCase):
    def setUp(self):
        self.usermodel = User()

    def test_valid(self):
        params = dict(email='hoge@example.com',
                      first_name='first', last_name='last',
                      password1='hogehoge', password2='hogehoge')
        form = RegistrationForm(params, instance=self.usermodel)
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        params = dict(email='hogeexample.com',
                      first_name='first', last_name='last',
                      password1='hogehoge', password2='hogehoge')
        form = RegistrationForm(params, instance=self.usermodel)
        self.assertFalse(form.is_valid())

    def test_missmatch_password(self):
        params = dict(email='hoge@example.com',
                      first_name='first', last_name='last',
                      password1='hogehuga', password2='hogehoge')
        usermodel = User()
        form = RegistrationForm(params, instance=self.usermodel)
        self.assertFalse(form.is_valid())

    def test_invalid_password_length(self):
        params = dict(email='hoge@example.com',
                      first_name='first', last_name='last',
                      password1='hoge', password2='hoge')
        usermodel = User()
        form = RegistrationForm(params, instance=self.usermodel)
        self.assertFalse(form.is_valid())

    def test_invalid_with_firstname(self):
        params = dict(email='hoge@example.com',
                      first_name='', last_name='last',
                      password1='hogehoge', password2='hogehoge')
        usermodel = User()
        form = RegistrationForm(params, instance=self.usermodel)
        self.assertFalse(form.is_valid())

    def test_invalid_with_lastname(self):
        params = dict(email='hoge@example.com',
                      first_name='first', last_name='',
                      password1='hogehoge', password2='hogehoge')
        usermodel = User()
        form = RegistrationForm(params, instance=self.usermodel)
        self.assertFalse(form.is_valid())
