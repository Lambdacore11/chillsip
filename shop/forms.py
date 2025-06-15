from django import forms
from .models import Order,Feedback

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'street',
            'is_private',
            'building',
            'apartment'
        ]
    def clean(self):
        cleaned_data = super().clean()
        is_private = cleaned_data.get('is_private')
        apartment = cleaned_data.get('apartment')

        if is_private and apartment:
            raise forms.ValidationError('Вы указали квартиру при выборе пункта "частный дом"')
        elif not is_private and not apartment:
            raise forms.ValidationError('Необходимо указать квартиру если не выбран пункт "частный дом"')
        
        return cleaned_data


class FeedbackForm(forms.ModelForm):
    class Meta:
        CHOICES = (
            ('1',1),
            ('2',2),
            ('3',3),
            ('4',4),
            ('5',5),         
        )
        model = Feedback
        fields = [
            'rating',
            'review',
        ]
        widgets = {
            'rating': forms.RadioSelect(choices=CHOICES)
        }