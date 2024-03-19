from django.shortcuts import render
from . import forms, models
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect

# Create your views here.


# for showing signup/login button for organization
def organizationclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return render(request, "organization/organizationclick.html")


def organization_signup_view(request):
    userForm = forms.OrganizationUserForm()
    organizationForm = forms.OrganizationForm()
    mydict = {"userForm": userForm, "organizationForm": organizationForm}
    if request.method == "POST":
        userForm = forms.OrganizationUserForm(request.POST)
        organizationForm = forms.OrganizationForm(request.POST, request.FILES)
        if userForm.is_valid() and organizationForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            organization = organizationForm.save(commit=False)
            organization.user = user
            organization.save()
            my_organization_group = Group.objects.get_or_create(name="ORGANIZATION")
            my_organization_group[0].user_set.add(user)
        return HttpResponseRedirect("organizationlogin")
    return render(request, "organization/organizationsignup.html", context=mydict)
