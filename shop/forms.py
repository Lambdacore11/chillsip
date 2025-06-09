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

class UsersProductsForm(forms.ModelForm):
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