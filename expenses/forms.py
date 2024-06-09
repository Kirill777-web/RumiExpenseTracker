from django import forms
from .models import AddMoneyInfo


class AddMoneyForm(forms.ModelForm):
    class Meta:
        model = AddMoneyInfo
        fields = ['add_money', 'quantity', 'description', 'Date', 'Category']
