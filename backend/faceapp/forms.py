# faceapp/forms.py
from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ("username", "email", "password")

class LoginForm(forms.Form):
    username = forms.CharField(required=False)
    # For face login we don't require username; optional for fallback
