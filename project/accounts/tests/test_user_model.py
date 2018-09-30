from django.test import TestCase
from accounts.models import User

class UserModelTests(TestCase):
    def test_is_empty(self):
        saved_users = User.objects.all()
        self.assertEqual(saved_users.count(), 0)

    def test_is_not_empty(self):
        user = User()
        user.save()
        saved_users = User.objects.all()
        self.assertEqual(saved_users.count(), 1)

    def test_string_representation(self):
        user = User(email='hoge@example.com', password='hogehoge',
                    first_name='first', last_name='last')
        self.assertEqual(str(user), 'last first')

    def test_misses_email(self):
        missuser = User(email='hogehoge', password='hogehoge',
                        first_name='first', last_name='last')
        self.assertFalse(missuser.check())

    def test_misses_password(self):
        missuser = User(email='hoge@example.com', password='hoge',
                        first_name='first', last_name='last')
        self.assertFalse(missuser.check())
