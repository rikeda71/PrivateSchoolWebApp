from django.test import TestCase
from django.urls import reverse, resolve
from django.forms import widgets
from accounts.views import PasswordChange
from accounts.views import PasswordChangeDone
from accounts.forms import PasswordChangeForm
from accounts.models import User


class PasswordChangeViewTest(TestCase):

    def setUp(self):
        super().setUp()
        self.credentials = {'last_name': 'last', 'first_name': 'first',
                            'email': 'hoge@example.com', 'password': 'hogehoge'}
        user = User.objects.create_user(**self.credentials)
        user.is_active = True
        user.save()
        url = reverse('accounts:password_change')
        self.client.login(**{'email': 'hoge@example.com', 'password': 'hogehoge'})
        self.response = self.client.get(url)

    def test_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_class(self):
        view = resolve('/accounts/password_change/')
        self.assertEqual(view.func.view_class, PasswordChange)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_value_of_contain_form_inputs(self):
        self.assertContains(self.response, '<input', 5)


class PasswordChangeDoneViewTest(TestCase):

    def setUp(self):
        super().setUp()
        self.credentials = {'last_name': 'last', 'first_name': 'first',
                            'email': 'hoge@example.com', 'password': 'hogehoge'}
        user = User.objects.create_user(**self.credentials)
        user.is_active = True
        user.save()
        url = reverse('accounts:password_change_done')
        self.client.login(**{'email': 'hoge@example.com', 'password': 'hogehoge'})
        self.response = self.client.get(url)

    def test_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_class(self):
        view = resolve('/accounts/password_change/done/')
        self.assertEqual(view.func.view_class, PasswordChangeDone)


class PasswordChangeFormTest(TestCase):

    def setUp(self):
        super().setUp()
        self.credentials = {'last_name': 'last', 'first_name': 'first',
                            'email': 'hoge@example.com', 'password': 'hogehoge'}
        user = User.objects.create_user(**self.credentials)
        user.is_active = True
        user.save()
        self.form = PasswordChangeForm(user)

    def test_field_widget_type(self):
        self.assertEqual(widgets.PasswordInput,
                         self.form.fields['old_password'].widget.__class__)
        self.assertEqual(widgets.PasswordInput,
                         self.form.fields['new_password1'].widget.__class__)
        self.assertEqual(widgets.PasswordInput,
                         self.form.fields['new_password2'].widget.__class__)


class PasswordChangeTest(TestCase):

    def setUp(self):
        super().setUp()
        self.credentials = {'last_name': 'last', 'first_name': 'first',
                            'email': 'hoge@example.com', 'password': 'hogehoge'}
        user = User.objects.create_user(**self.credentials)
        user.is_active = True
        user.save()
        self.user = user

    def test_password_change_is_valid(self):
        self.client.login(**{'email': 'hoge@example.com', 'password': 'hogehoge'})
        response = self.client.post(reverse('accounts:password_change'),
                                    {'old_password': 'hogehoge',
                                     'new_password1': 'hugahuga',
                                     'new_password2': 'hugahuga'})
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response, '/accounts/password_change/done/')
        self.assertTrue(self.user.password, 'hugahuga')

    def test_password_change_is_invalid_with_missing_value(self):
        self.client.login(**{'email': 'hoge@example.com', 'password': 'hogehoge'})
        response = self.client.post(reverse('accounts:password_change'),
                                    {'old_password': 'hogehoge',
                                     'new_password1': 'hugahuga',
                                     'new_password2': 'hugahuga'})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '元のパスワードが間違っています', 1)

    def test_password_change_is_invalid_with_missing_value(self):
        self.client.login(**{'email': 'hoge@example.com', 'password': 'hogehoge'})
        response = self.client.post(reverse('accounts:password_change'),
                                    {'old_password': 'hugahuga',
                                     'new_password1': 'hugahuga',
                                     'new_password2': 'hogehoge'})
        self.assertEqual(200, response.status_code)
        self.assertContains(response, '確認用パスワードが一致しません', 1)
