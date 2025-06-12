from decimal import Decimal
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm,PasswordChangeForm
import re


class UserRegisterForm(forms.ModelForm):
    
    password = forms.CharField(label='Пароль',widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль',widget=forms.PasswordInput)

    class Meta:

        model = get_user_model()
        fields = ['username','email']
    
    def clean_username(self):

        username = self.cleaned_data['username']

        if len(username) < 5:
            raise forms.ValidationError('Имя пользователя должно быть не менее 5 символов')
        
        return username

    def clean_password2(self):

        password = self.cleaned_data['password']
        password2 = self.cleaned_data['password2']

        if len(password) < 8 :
            raise forms.ValidationError('Пароль должен содержать не менее 8 символов')
        
        elif re.search(r'^[0-9]+$',password):
            raise forms.ValidationError('Введённый пароль состоит только из цифр.')
        
        elif password != password2:
            raise forms.ValidationError('Пароли не совпадают')
        
        return password2


class UserPasswordChangeForm(PasswordChangeForm):

    def clean_new_password1(self):

        password = self.cleaned_data['new_password1']

        if len(password) < 8 :
            raise forms.ValidationError('Пароль должен содержать не менее 8 символов')
        
        elif re.search(r'^[0-9]+$',password):
            raise forms.ValidationError('Введённый пароль состоит только из цифр.')
        
        return password


class UserLoginForm(AuthenticationForm):
   def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Имя пользователя или эл.почта'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'age',
            'gender',
            'foto'
        ]


class MoneyUpdateForm(forms.ModelForm):

    MONEY_CHOICES = (
            (100,'100₽'),
            (500,'500₽'),
            (1000,'1000₽'),
            (5000,'5000₽'),
            (10000,'10 000₽')
        )
    
    account = forms.ChoiceField(choices=MONEY_CHOICES, label='Внести')

    class Meta:
        model = get_user_model()
        fields = ['account']
    
    def clean_account(self):
        value = self.cleaned_data['account']
        return Decimal(value)
        
    
