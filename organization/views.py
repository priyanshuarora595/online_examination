from django.shortcuts import render, redirect
from exam import forms
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from teacher import models as TMODEL
from student import models as SMODEL
from exam import models as EMODEL
from organization import models as OMODEL
from teacher import forms as TFORM
from student import forms as SFORM
from organization import forms as OFORM
from exam import forms as EFORM
from django.contrib.auth.models import User
from django.db.models import Sum


# Create your views here.


def is_organization(user):
    return user.groups.filter(name="ORGANIZATION").exists()


# for showing signup/login button for organization
def organizationclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return render(request, "organization/organizationclick.html")


def organization_signup_view(request):
    userForm = OFORM.OrganizationUserForm()
    organizationForm = OFORM.OrganizationForm()
    mydict = {"userForm": userForm, "organizationForm": organizationForm}
    if request.method == "POST":
        userForm = OFORM.OrganizationUserForm(request.POST)
        organizationForm = OFORM.OrganizationForm(request.POST, request.FILES)
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


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_dashboard_view(request):
    organization_id = OMODEL.Organization.objects.get(user=request.user).id
    dict = {
        "total_student": SMODEL.Student.objects.all()
        .filter(organization_id=organization_id)
        .count(),
        "total_teacher": TMODEL.Teacher.objects.all()
        .filter(organization_id=organization_id, status=True)
        .count(),
        "total_course": EMODEL.Course.objects.all()
        .filter(organization_id=organization_id)
        .count(),
    }
    return render(request, "organization/organization_dashboard.html", context=dict)


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_profile_view(request):
    # organization = OMODEL.Organization.objects.get(id=request.user.id)
    organization = OMODEL.Organization.objects.get(user=request.user)
    user = OMODEL.User.objects.get(id=request.user.id)
    userForm = forms.UserUpdateForm(instance=user)
    organizationForm = OFORM.OrganizationForm(instance=organization)
    mydict = {"userForm": userForm, "organizationForm": organizationForm}

    if request.method == "POST":
        userForm = forms.UserUpdateForm(request.POST, instance=user)
        organizationForm = OFORM.OrganizationForm(request.POST, instance=organization)
        if userForm.is_valid() and organizationForm.is_valid():
            user = userForm.save()
            user.save()
            organizationForm.save()
            return redirect("organization-profile")
        else:
            return render(request, "exam/unauthorized.html")
    return render(request, "organization/update_organization.html", context=mydict)


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_students_view(request):
    organization_id = OMODEL.Organization.objects.get(user=request.user).id
    response = {
        "total_student": SMODEL.Student.objects.all()
        .filter(organization_id=organization_id)
        .count()
    }
    return render(request, "organization/organization_student.html", context=response)


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_view_student_view(request):
    organization_id = OMODEL.Organization.objects.get(user=request.user).id
    students = SMODEL.Student.objects.all().filter(organization_id=organization_id)
    return render(
        request, "organization/organization_view_student.html", {"students": students}
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_view_teacher_view(request):
    organization_id = OMODEL.Organization.objects.get(user=request.user).id
    teachers = TMODEL.Teacher.objects.all().filter(
        status=True, organization_id=organization_id
    )
    return render(
        request, "organization/organization_view_teacher.html", {"teachers": teachers}
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_teacher_view(request):
    organization_id = OMODEL.Organization.objects.get(user=request.user).id
    response = {
        "approved_teacher": TMODEL.Teacher.objects.all()
        .filter(organization_id=organization_id, status=True)
        .count(),
        "pending_teacher": TMODEL.Teacher.objects.all()
        .filter(organization_id=organization_id, status=False)
        .count(),
        "salary": TMODEL.Teacher.objects.all()
        .filter(organization_id=organization_id, status=True)
        .aggregate(Sum("salary"))["salary__sum"],
    }
    return render(request, "organization/organization_teacher.html", context=response)


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_view_pending_teacher_view(request):
    organization_id = OMODEL.Organization.objects.get(user=request.user).id
    teachers = TMODEL.Teacher.objects.all().filter(
        organization_id=organization_id, status=False
    )
    return render(
        request,
        "organization/organization_view_pending_teacher.html",
        {"teachers": teachers},
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def approve_teacher_view(request, pk):
    teacherSalary = forms.TeacherSalaryForm()
    print(request.POST)
    if request.method == "POST":
        teacherSalary = forms.TeacherSalaryForm(request.POST)
        if teacherSalary.is_valid():
            teacher = TMODEL.Teacher.objects.get(id=pk)
            organization_id = OMODEL.Organization.objects.get(user=request.user).id
            if teacher.organization_id == organization_id:
                teacher.salary = teacherSalary.cleaned_data["salary"]
                teacher.status = True
                teacher.save()
            else:
                return render(request, "exam/unauthorized.html")
        else:
            print("form is invalid")
        return redirect("organization-view-pending-teacher")
    return render(
        request, "organization/salary_form.html", {"teacherSalary": teacherSalary}
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def reject_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    organization_id = OMODEL.Organization.objects.get(user=request.user).id
    if teacher.organization_id == organization_id:
        user = User.objects.get(id=teacher.user_id)
        user.delete()
        teacher.delete()
    else:
        return render(request, "exam/unauthorized.html")
    return redirect("organization-view-pending-teacher")


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def update_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = TMODEL.User.objects.get(id=teacher.user_id)
    userForm = TFORM.TeacherUserForm(instance=user)
    teacherForm = TFORM.TeacherForm(instance=teacher)
    mydict = {"userForm": userForm, "teacherForm": teacherForm}
    organization_id = OMODEL.Organization.objects.get(user=request.user).id

    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = organization_id
        request.POST._mutable = False
        userForm = TFORM.TeacherUserForm(request.POST, instance=user)
        teacherForm = TFORM.TeacherForm(request.POST, instance=teacher)
        if userForm.is_valid() and teacherForm.is_valid():
            if teacher.organization_id == organization_id:
                user = userForm.save()
                user.save()
                teacherForm.save()
                return redirect("organization-view-teacher")
            else:
                return render(request, "exam/unauthorized.html")
    return render(request, "organization/update_teacher.html", context=mydict)


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def delete_teacher_view(request, pk):
    organization_id = OMODEL.Organization.objects.get(user=request.user).id
    teacher = TMODEL.Teacher.objects.get(id=pk)
    if teacher.organization_id == organization_id:
        user = User.objects.get(id=teacher.user_id)
        user.delete()
        teacher.delete()
        return redirect("organization-view-teacher")
    else:
        return render(request, "exam/unauthorized.html")


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_view_teacher_salary_view(request):
    organization_id = OMODEL.Organization.objects.get(user=request.user).id
    teachers = TMODEL.Teacher.objects.all().filter(
        status=True, organization_id=organization_id
    )
    return render(
        request,
        "organization/organization_view_teacher_salary.html",
        {"teachers": teachers},
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_student_view(request):
    dict = {
        "total_student": SMODEL.Student.objects.all().count(),
    }
    return render(request, "organization/organization_student.html", context=dict)


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_view_student_view(request):
    students = SMODEL.Student.objects.all()
    return render(
        request, "organization/organization_view_student.html", {"students": students}
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def update_student_view(request, pk):
    student = SMODEL.Student.objects.get(id=pk)
    user = SMODEL.User.objects.get(id=student.user_id)
    userForm = SFORM.StudentUserForm(instance=user)
    studentForm = SFORM.StudentForm(instance=student)
    mydict = {"userForm": userForm, "studentForm": studentForm}
    if request.method == "POST":
        userForm = SFORM.StudentUserForm(request.POST, instance=user)
        studentForm = SFORM.StudentForm(request.POST, instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            studentForm.save()
            return redirect("organization-view-student")
    return render(request, "organization/update_student.html", context=mydict)


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def delete_student_view(request, pk):
    student = SMODEL.Student.objects.get(id=pk)
    user = User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect("/organization-view-student")


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_view_student_marks_view(request):
    students = SMODEL.Student.objects.all()
    return render(
        request,
        "organization/organization_view_student_marks.html",
        {"students": students},
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_view_marks_view(request, pk):
    courses = EMODEL.Course.objects.all()
    response = render(
        request, "organization/organization_view_marks.html", {"courses": courses}
    )
    response.set_cookie("student_id", str(pk))
    return response


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_check_marks_view(request, pk):
    course = EMODEL.Course.objects.get(id=pk)
    student_id = request.COOKIES.get("student_id")
    student = SMODEL.Student.objects.get(user_id=student_id)
    results = EMODEL.Result.objects.all().filter(exam=course).filter(student=student)

    return render(
        request, "organization/organization_check_marks.html", {"results": results}
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_course_view(request):
    return render(request, "organization/organization_course.html")


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_add_course_view(request):
    courseForm = forms.CourseForm()
    organization = OMODEL.Organization.objects.get(user=request.user)
    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = organization.id
        request.POST._mutable = False
        courseForm = forms.CourseForm(request.POST)
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.organization = organization
            course.save()
        else:
            print("form is invalid")
        return redirect("organization-view-exam")
    return render(
        request,
        "organization/organization_add_course.html",
        {"courseForm": courseForm, "organization_id": organization.id},
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_update_course_view(request, pk):
    course = EMODEL.Course.objects.get(id=pk)
    courseForm = forms.CourseForm(instance=course)
    organization = OMODEL.Organization.objects.get(user=request.user)
    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = organization.id
        request.POST._mutable = False
        courseForm = forms.CourseForm(request.POST, instance=course)
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.organization = organization
            course.save()
        else:
            print("form is invalid")
        return redirect("organization-view-course")
    return render(
        request,
        "organization/update_course.html",
        {"courseForm": courseForm, "organization_id": organization.id},
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_view_course_view(request):
    courses = EMODEL.Course.objects.all()
    return render(
        request, "organization/organization_view_course.html", {"courses": courses}
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def delete_course_view(request, pk):
    course = EMODEL.Course.objects.get(id=pk)
    course.delete()
    return redirect("organization-view-course")


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_question_view(request):
    return render(request, "organization/organization_question.html")


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_add_question_view(request):
    organization = OMODEL.Organization.objects.get(user=request.user)
    # questionForm = EFORM.QuestionForm(organization=organization)
    # questionForm = EFORM.QuestionForm(kwargs={"organization": organization})
    # print(questionForm.data)
    og = {"organization": organization}
    questionForm = EFORM.QuestionForm(initial=og)
    # print(questionForm)
    # questionForm.data.update(og)
    # print(questionForm.data)
    # questionForm = EFORM.QuestionForm(organization=organization)
    optionForm = EFORM.OptionForm()
    if request.method == "POST":
        print("post request=========")
        print(request.POST)
        questionForm = EFORM.QuestionForm(request.POST, request.FILES)
        print(questionForm)
        print(f"{questionForm.is_valid() = }")
        print(f"{questionForm.errors = }")
        question = questionForm.save(commit=False)
        course = EMODEL.Course.objects.get(id=request.POST.get("courseID"))
        question.course = course
        course.question_number += 1
        course.total_marks += int(request.POST.get("marks"))
        course.save()
        question.save()
        print(f"{question.id = }")
        options_list = request.POST.getlist("option")
        answer_pos = int(request.POST.get("answer").split(" ")[1])-1
        for option in options_list:
            option_obj = EMODEL.Option.objects.create(option=option,question=question)
            option_obj.save()
            if option == options_list[answer_pos]:
                answer_obj = EMODEL.Answer.objects.create(question=question,answer=option_obj)
                answer_obj.save()
        # answer = int(request.POST.get("answer").split(" ")[1])
        # answer_obj = EMODEL.Answer.objects.create(question=question,answer=options_list[answer])
        # opform = forms.OptionForm(data={'option': option}).save(commit=False)
        # opform.question = question
        # opform.save()

        # optionForm = EFORM.OptionForm(request.POST)
        # print(f"{optionForm.is_valid()}")
        return redirect("organization-add-question")
    return render(
        request,
        "organization/organization_add_question.html",
        {"questionForm": questionForm, "optionForm": optionForm},
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def organization_view_question_view(request):
    organization = OMODEL.Organization.objects.get(user=request.user)
    courses = EMODEL.Course.objects.filter(organization=organization.id)
    return render(
        request, "organization/organization_view_question.html", {"courses": courses}
    )


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def view_question_view(request, pk):
    questions = EMODEL.Question.objects.all().filter(course_id=pk)
    return render(request, "organization/view_question.html", {"questions": questions})


@login_required(login_url="organizationlogin")
@user_passes_test(is_organization)
def delete_question_view(request, pk):
    question = EMODEL.Question.objects.get(id=pk)
    question.delete()
    course = EMODEL.Course.objects.all().filter(course_name=question.course)[0]
    course.question_number -= 1
    course.total_marks -= question.marks
    course.save()
    return HttpResponseRedirect("/organization-view-question")
