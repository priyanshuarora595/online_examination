from django.shortcuts import render, redirect
from . import forms
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from exam import models as EMODEL
from student import models as SMODEL
from organization import models as OMODEL
from teacher import models as TMODEL
from exam import forms as EFORM


# for showing signup/login button for teacher


def is_teacher(user):
    return user.groups.filter(name="TEACHER").exists()


def teacherclick_view(request):
    if request.user.is_authenticated and is_teacher(request.user):
        return HttpResponseRedirect("afterlogin")
    return render(request, "teacher/teacherclick.html")


def teacher_signup_view(request):
    userForm = forms.TeacherUserForm()
    teacherForm = forms.TeacherForm()
    mydict = {"userForm": userForm, "teacherForm": teacherForm}
    if request.method == "POST":
        userForm = forms.TeacherUserForm(request.POST)
        teacherForm = forms.TeacherForm(request.POST, request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            teacher = teacherForm.save(commit=False)
            teacher.user = user
            teacher.organization = OMODEL.Organization.objects.get(
                id=request.POST.get("organizationID")
            )
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name="TEACHER")
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect("teacherlogin")
    return render(request, "teacher/teachersignup.html", context=mydict)


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    organization = TMODEL.Teacher.objects.get(user=request.user.id).organization
    dict = {
        "total_course": EMODEL.Course.objects.filter(organization=organization).count(),
        "total_student": SMODEL.Student.objects.filter(
            organization=organization
        ).count(),
    }
    return render(request, "teacher/teacher_dashboard.html", context=dict)


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_course_view(request):
    return render(request, "teacher/teacher_course.html")


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_add_course_view(request):
    courseForm = EFORM.CourseForm()
    organization = TMODEL.Teacher.objects.get(user=request.user.id).organization
    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = organization.id
        request.POST._mutable = False
        courseForm = EFORM.CourseForm(request.POST)
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.created_by = request.user
            course.organization = organization
            course.save()
        else:
            print("form is invalid")
        return redirect("teacher-view-exam")
    return render(request, "teacher/teacher_add_course.html", {"courseForm": courseForm})


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_course_view(request):
    organization = TMODEL.Teacher.objects.get(user=request.user.id).organization
    courses = EMODEL.Course.objects.filter(organization=organization)
    return render(request, "teacher/teacher_view_course.html", {"courses": courses})


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_update_course_view(request, pk):
    course = EMODEL.Course.objects.get(id=pk)
    courseForm = EFORM.CourseForm(instance=course)
    organization = TMODEL.Teacher.objects.get(user=request.user.id).organization
    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = organization.id
        request.POST._mutable = False
        courseForm = EFORM.CourseForm(request.POST, instance=course)
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.organization = organization
            course.save()
        else:
            print("form is invalid")
        return redirect("teacher-view-course")
    return render(
        request,
        "teacher/update_course.html",
        {"courseForm": courseForm, "organization_id": organization.id},
    )

@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_delete_course_view(request, pk):
    course = EMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect("/teacher/teacher-view-exam")


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_question_view(request):
    return render(request, "teacher/teacher_question.html")


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    organization = TMODEL.Teacher.objects.get(user=request.user.id).organization
    og = {"organization": organization}
    questionForm = EFORM.QuestionForm(initial=og)
    optionForm = EFORM.OptionForm()
    if request.method == "POST":
        questionForm = EFORM.QuestionForm(request.POST, request.FILES)
        if questionForm.is_valid():
            question = questionForm.save(commit=False)
            course = EMODEL.Course.objects.get(id=request.POST.get("courseID"))
            question.course = course
            course.question_number += 1
            course.total_marks += int(request.POST.get("marks"))
            course.save()
            question.save()

            options_list = request.POST.getlist("option")
            answer_pos = int(request.POST.get("answer").split(" ")[1])-1
            for option in options_list:
                option_obj = EMODEL.Option.objects.create(option=option,question=question)
                option_obj.save()
                if option == options_list[answer_pos]:
                    answer_obj = EMODEL.Answer.objects.create(question=question,answer=option_obj)
                    answer_obj.save()
        else:
            print("form is invalid")
        return redirect("teacher-add-question")
    return render(
        request, "teacher/teacher_add_question.html", {"questionForm": questionForm,"optionForm":optionForm}
    )


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses = EMODEL.Course.objects.all()
    return render(request, "teacher/teacher_view_question.html", {"courses": courses})


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def see_question_view(request, pk):
    questions = EMODEL.Question.objects.all().filter(course_id=pk)
    return render(request, "teacher/see_question.html", {"questions": questions})


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def remove_question_view(request, pk):

    question = EMODEL.Question.objects.get(id=pk)
    question.delete()
    course = EMODEL.Course.objects.all().filter(course_name=question.course)[0]
    course.question_number -= 1
    course.total_marks -= question.marks
    course.save()
    return HttpResponseRedirect("/teacher/teacher-view-question")
