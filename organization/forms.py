from django import forms
from django.contrib.auth.models import User
from . import models


class OrganizationUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password"]
        widgets = {"password": forms.PasswordInput()}

    # def __init__(self, *args, **kwargs):
    #     super(OrganizationUserForm, self).__init__(*args, **kwargs)
    #     self.fields["password"].required = False

    # def save(self, commit=True):
    #     user = super(OrganizationUserForm, self).save(commit=False)
    #     print(f"{user.password = }")
    #     password = self.cleaned_data["password"]
    #     print(f"{password = }")
    #     if password!="":
    #         print("updating password")
    #         user.set_password(password)
    #         if commit:
    #             user.save()
    #     return user



class OrganizationForm(forms.ModelForm):
    class Meta:
        model = models.Organization
        fields = ["address", "mobile"]
