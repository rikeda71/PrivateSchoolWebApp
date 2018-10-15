from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, AuthenticationForm, PasswordChangeForm
)
from .models import User, PDFFile


class RegistrationForm(UserCreationForm):
    """
    ユーザ登録フォーム
    """

    last_name = forms.CharField(max_length=10, required=True,
                                widget=forms.TextInput(
                                    attrs={'placeholder': '名字'}
                                ))
    first_name = forms.CharField(max_length=10, required=True,
                                 widget=forms.TextInput(
                                     attrs={'placeholder': '名前'}
                                 ))
    email = forms.EmailField(max_length=50, required=True,
                             widget=forms.EmailInput(
                                 attrs={'placeholder': 'メールアドレス'}
                             ))
    password1 = forms.CharField(max_length=30, required=True,
                                widget=forms.PasswordInput(
                                    attrs={'placeholder': 'パスワード'}
                                ))
    password2 = forms.CharField(max_length=30, required=True,
                                widget=forms.PasswordInput(
                                    attrs={'placeholder': 'パスワード(確認用)'}
                                ))

    class Meta:
        model = User
        fields = ('last_name', 'first_name', 'email')
        widgets = {
            'password': forms.PasswordInput()
        }

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            # field.widget.attrs['placeholder'] = field.label


class LoginForm(AuthenticationForm):
    """
    ログインフォーム
    """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class MyPasswordChangeForm(PasswordChangeForm):
    """
    パスワード変更フォーム
    """

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class UploadFileForm(forms.ModelForm):

    class Meta:
        model = PDFFile
        fields = ['attach', ]

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['accept'] = 'application/pdf'
            field.widget.attrs['placeholder'] = field.label
