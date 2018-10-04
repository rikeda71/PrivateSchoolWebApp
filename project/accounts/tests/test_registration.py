from django.test import TestCase
from django.urls import reverse, resolve
from django.forms import widgets
from accounts.views import UserRegister
from accounts.views import UserRegisterComplete
from accounts.forms import RegistrationForm
from accounts.models import User


class RegistrationViewTest(TestCase):
    def setUp(self):
        super().setUp()
        url = reverse('accounts:user_register')
        self.response = self.client.get(url)

    def test_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_class(self):
        view = resolve('/accounts/registration/')
        self.assertEqual(view.func.view_class, UserRegister)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_value_of_contain_form_inputs(self):
        self.assertContains(self.response, '<input', 7)


class RegistrationFormTest(TestCase):
    def setUp(self):
        self.form = RegistrationForm()

    def test_field_widget_type(self):
        self.assertEqual(widgets.TextInput,
                         self.form.fields['last_name'].widget.__class__)
        self.assertEqual(widgets.TextInput,
                         self.form.fields['first_name'].widget.__class__)
        self.assertEqual(widgets.EmailInput,
                         self.form.fields['email'].widget.__class__)
        self.assertEqual(widgets.PasswordInput,
                         self.form.fields['password1'].widget.__class__)
        self.assertEqual(widgets.PasswordInput,
                         self.form.fields['password2'].widget.__class__)


class RegistrationTest(TestCase):
    def setUp(self):
        self.credentials = {'last_name': 'last', 'first_name': 'first',
                            'email': 'setup@example.com',
                            'password': 'hogehoge'}
        User.objects.create_user(**self.credentials)
        user = User.objects.get(pk=1)
        user.is_active = True
        user.save()

    def test_registration_is_valid(self):
        response = self.client.post(reverse('accounts:user_register'),
                                    {'last_name': 'last', 'first_name': 'first',
                                     'email': 'hoge@example.com',
                                     'password1': 'hogehoge', 'password2': 'hogehoge'})
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, '/accounts/registration/done')
        self.assertFalse(User.objects.get(pk=2).is_active)

    def test_registration_is_invalid_with_missing_value(self):
        response = self.client.post(reverse('accounts:user_register'),
                                    {'last_name': 'last', 'first_name': 'first',
                                     'email': 'hoge@example.com',
                                     'password1': 'hogehoge', 'password2': 'hogehuga'})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '確認用パスワードが一致しません', 1)

    def test_registration_is_invalid_with_already_exists_email(self):
        response = self.client.post(reverse('accounts:user_register'),
                                    {'last_name': 'last', 'first_name': 'first',
                                     'email': 'setup@example.com',
                                     'password1': 'hogehoge', 'password2': 'hogehoge'})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, 'この メールアドレス を持った ユーザー が既に存在します', 1)
