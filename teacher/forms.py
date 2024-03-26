from django import forms
from django.contrib.auth.models import User
from . import models
from organization import models as EMODEL


class TeacherUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password"]
        widgets = {"password": forms.PasswordInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(args)>0:
            query_dict = args[0]
            if "organizationID" in query_dict.keys():
                del self.fields['password']

        # if "organizationID" in args[0].keys():
        #     del self.fields['password']


class TeacherForm(forms.ModelForm):
    organizationID = forms.ModelChoiceField(
        queryset=EMODEL.Organization.objects.all(),
        empty_label="Organization Name",
        to_field_name="id",
        initial=None,
    )

    class Meta:
        model = models.Teacher
        fields = ["address", "mobile","salary"]
