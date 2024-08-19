from django import forms # type: ignore
from .models import Users

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Users
        fields = ['name', 'email', 'password']