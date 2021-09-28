from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class ProductMovingToFromCartForm(forms.Form):
    product_id = forms.IntegerField(min_value=1, widget=forms.HiddenInput())


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['username'].help_text = None
        self.fields['password'].label = 'Пароль'
        self.fields['password'].help_text = None


class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя'
        self.fields['username'].help_text = None
        self.fields['first_name'] = forms.CharField(label='Имя', max_length=30)
        self.fields['last_name'] = forms.CharField(label='Фамилия', max_length=30)
        self.fields['email'] = forms.EmailField(label='Адрес электронной почты')
        self.fields['password1'].label = 'Пароль'
        self.fields['password1'].help_text = None
        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['password2'].help_text = None

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
