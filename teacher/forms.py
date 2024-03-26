from django import forms
from django.contrib.auth.models import User
from . import models
from organization import models as EMODEL


class TeacherUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password"]
        widgets = {"password": forms.PasswordInput()}



class TeacherForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "instance" in kwargs.keys():
            self.fields["organizationID"] = forms.ModelChoiceField(
                queryset=EMODEL.Organization.objects.all(),
                empty_label="Organization Name",
                to_field_name="id",
                initial=kwargs.get("instance").organization,
            )
            
    organizationID = forms.ModelChoiceField(
        queryset=EMODEL.Organization.objects.all(),
        empty_label="Organization Name",
        to_field_name="id",
        initial=None,
    )

    class Meta:
        model = models.Teacher
        fields = ["address", "mobile","salary"]
