from django import forms
from .models import Students

class StudentsForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = ["firstname", "lastname", "phone"]
        widgets = {
            "firstname": forms.TextInput(attrs={"class": "form-control"}),
            "lastname":  forms.TextInput(attrs={"class": "form-control"}),
            "phone":     forms.TextInput(attrs={"class": "form-control"}),
        }
