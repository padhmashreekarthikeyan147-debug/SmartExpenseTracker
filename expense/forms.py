from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Expense, Budget


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Enter Email"
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2"
        ]

        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Username"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter Password"
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm Password"
        })


class ExpenseForm(forms.ModelForm):

    class Meta:

        model = Expense

        fields = [
            "description",
            "amount",
            
            "date",
            "notes"
        ]

        widgets = {

            "description": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Expense Description"
            }),

            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Amount"
            }),

            "category": forms.TextInput(attrs={
                "class": "form-control",
                "readonly": "readonly"
            }),

            "date": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),

            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Additional Notes"
            }),
        }


class BudgetForm(forms.ModelForm):

    class Meta:
        model = Budget
        fields = ["amount"]

        widgets = {
            "amount": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Enter Monthly Budget"
            })
        }