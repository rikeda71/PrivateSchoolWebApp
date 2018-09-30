from django import forms
from .models import User


class RegistrationForm(forms.ModelForm):
    """
    last_name = forms.CharField()
    first_name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), min_length=8)
    """

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class LoginForm(forms.ModelForm):
    """
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput(), min_length=8)
    """

    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
