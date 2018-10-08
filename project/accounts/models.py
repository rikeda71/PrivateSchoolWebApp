from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.core.validators import FileExtensionValidator
import os


class UserManager(BaseUserManager):

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('メールアドレスを入力してください')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', False)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_active') is not True:
            raise ValueError('Superuser must have is_active=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    user_id = models.AutoField(primary_key=True, unique=True)
    email = models.EmailField(_('メールアドレス'),
                              max_length=128, unique=True,
                              help_text=_('通知を受け取りたいメールアドレスを入力'),
                              )
    first_name = models.CharField(_('名前'), max_length=10)
    last_name = models.CharField(_('名字'), max_length=10)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Send an email to this user
        """

        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.last_name + ' ' + self.first_name


class PDFFile(models.Model):

    attach = models.FileField(
        verbose_name='shift',
        upload_to='uploads/%Y/%m/%d/',
        validators=[FileExtensionValidator(['pdf', ])],
    )

    def __str__(self):
        return self.pk

    def get_filename(self):
        return os.path.basename(self.attach.name)
