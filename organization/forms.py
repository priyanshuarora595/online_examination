from django import forms
from django.contrib.auth.models import User
from . import models


class OrganizationUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password", "email"]
        widgets = {"password": forms.PasswordInput()}



class OrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = ["address", "mobile"]
