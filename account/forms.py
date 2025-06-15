from decimal import Decimal
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']
    
    def  clean_username(self):
        username = super().clean_username()

        if len(username) < 5:
            raise forms.ValidationError('Имя пользователя должно быть не менее 5 символов')

        return username


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
        
    
