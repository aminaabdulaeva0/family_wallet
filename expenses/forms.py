from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'comment']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Например: Продукты'}),
            'amount': forms.NumberInput(attrs={'placeholder': '0.00'}),
            'comment': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Необязательно'}),
        }
