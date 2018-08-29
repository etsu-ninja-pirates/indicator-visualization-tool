from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':"add-on",'class':"form-signin",'class':"span4"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-signin",'class':"span4"}))
