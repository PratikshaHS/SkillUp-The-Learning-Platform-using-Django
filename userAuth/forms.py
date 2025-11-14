# userAuth/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email":      forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
            "username":   forms.TextInput(attrs={"class": "form-control", "placeholder": "username"}),
        }
