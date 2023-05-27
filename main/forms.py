from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class RegistrForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Log In'
    }))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Reenter Password'
    }))
    email = forms.EmailField(max_length=254, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'E-mail'
    }))
    nickname = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Nickname'
    }))

    class Meta:
        model = User
        fields = ('nickname', 'username', 'email', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords are not same!")
        return password2


class LogForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-input',
        'placeholder': 'Login'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-input',
        'placeholder': 'Password'
    }))


class PostForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'text-of-new-post',
        'placeholder': 'Your text'
    }))
    photo = forms.ImageField(widget=forms.ClearableFileInput(), required=False)

class EditPostForm(forms.Form):
    is_del = forms.CharField(widget=forms.TextInput(attrs={
        'id': 'is_del',
        'value': '0',
        'style': 'display: none;'
    }), required=False)
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'text-of-new-post',
        'placeholder': 'Your text'
    }))
    photo = forms.ImageField(widget=forms.ClearableFileInput(), required=False)


class CommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'message_area',
        'placeholder': 'New comment'
    }))


class FrindSearchRequestForm(forms.Form):
    querry = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'search-id-input',
        'placeholder': 'Search(ID/Name)'
    }))
