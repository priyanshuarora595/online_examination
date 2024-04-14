from django import forms
from django.contrib.auth.models import User
from exam import models as EMODEL
from django.db import models as django_db_models

class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(
        max_length=500, widget=forms.Textarea(attrs={"rows": 3, "cols": 30})
    )


class TeacherSalaryForm(forms.Form):
    salary = forms.IntegerField()


class OrganizationFeesForm(forms.Form):
    fees = forms.IntegerField()

class DateTimeLocalInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class DateTimeLocalField(forms.DateTimeField):
    input_formats = [
        "%Y-%m-%dT%H:%M:%S", 
        "%Y-%m-%dT%H:%M:%S.%f", 
        "%Y-%m-%dT%H:%M",
    ]
    widget = DateTimeLocalInput(format = '%Y-%m-%dT%H:%M')

class CourseForm(forms.ModelForm):
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

    exam_date = DateTimeLocalField()
    class Meta:
        model = EMODEL.Course
        fields = ["course_name","duration","passing_percentage", "exam_date"]


class QuestionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "instance" in kwargs.keys():
            self.fields["courseID"] = forms.ModelChoiceField(
                queryset=EMODEL.Course.objects.filter(
                    organization=kwargs.get("instance").organization
                ),
                empty_label="Course Name",
                to_field_name="id",
                initial=EMODEL.Course.objects.get(id=kwargs.get("instance").course.id)
            )
        elif "initial" in kwargs.keys():
            self.fields["courseID"] = forms.ModelChoiceField(
                queryset=EMODEL.Course.objects.filter(
                    organization=kwargs.get("initial").get("organization")
                ),
                empty_label="Course Name",
                to_field_name="id",
                initial=None,
            )
        else:
            self.fields["courseID"] = forms.ModelChoiceField(
                queryset=EMODEL.Course.objects.all(),
                empty_label="Course Name",
                to_field_name="id",
                initial=None,
            )


    class Meta:
        model = EMODEL.Question
        fields = [
            "marks",
            "question",
            "question_image",
        ]
        widgets = {"question": forms.Textarea(attrs={"rows": 3, "cols": 50})}


class OptionForm(forms.ModelForm):
    class Meta:
        model = EMODEL.Option
        fields = ["option"]


# class AnswerForm(forms.ModelForm):
#     class Meta:
#         model = EMODEL.Answer
#         fields = ['answer']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", 'email']
