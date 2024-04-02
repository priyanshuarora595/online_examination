from django.shortcuts import render, redirect
from . import forms
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from exam import models as ExamModel
from student import models as StudentModel
from organization import models as OrganizationModel
from teacher import models as TeacherModel
from exam import forms as ExamForms
from teacher import forms as TeacherForms


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
    mydict = {
        "userForm": userForm,
        "teacherForm": teacherForm
    }
    if request.method == "POST":
        request.POST._mutable = True
        request.POST["salary"] = 0
        request.POST._mutable = False
        userForm = forms.TeacherUserForm(request.POST)
        teacherForm = forms.TeacherForm(request.POST, request.FILES)
        print(userForm.errors)
        print(teacherForm.errors)
        if userForm.is_valid() and teacherForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            teacher = teacherForm.save(commit=False)
            teacher.user = user
            teacher.organization = OrganizationModel.Organization.objects.get(
                id=request.POST.get("organizationID")
            )
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name="TEACHER")
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect("teacherlogin")
    return render(request, "teacher/teachersignup.html", context=mydict)

@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_profile_view(request):
    teacher = TeacherModel.Teacher.objects.get(user=request.user)
    user = TeacherModel.User.objects.get(id=teacher.user_id)
    user_form = ExamForms.UserUpdateForm(instance=user)
    teacherForm = TeacherForms.TeacherForm(instance=teacher)


    user_form.fields['username'].widget.attrs['readonly'] = True
    user_form.fields['email'].widget.attrs['readonly'] = True


    teacherForm.fields['salary'].widget.attrs['readonly'] = True
    mydict = {
        "userForm": user_form, 
        "teacherForm": teacherForm
    }

    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = teacher.organization_id
        request.POST["salary"] = teacher.salary
        request.POST._mutable = False
        user_form = ExamForms.UserUpdateForm(request.POST, instance=user)
        teacherForm = TeacherForms.TeacherForm(request.POST, instance=teacher)

        if user_form.is_valid() and teacherForm.is_valid():
            pass
            user_form.save()
            teacherForm.save()
            return redirect("teacher-profile")
    return render(request, "teacher/teacher_update_profile.html", context=mydict)

@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    dict = {
        "total_course": ExamModel.Course.objects.filter(organization=organization).count(),
        "total_student": StudentModel.Student.objects.filter(
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
    courseForm = ExamForms.CourseForm()
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = organization.id
        request.POST._mutable = False
        courseForm = ExamForms.CourseForm(request.POST)
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.created_by = request.user
            course.organization = organization
            course.save()
        else:
            print("form is invalid")
        return redirect("teacher-view-course")
    return render(request, "teacher/teacher_add_course.html", {"courseForm": courseForm})


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_course_view(request):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    courses = ExamModel.Course.objects.filter(organization=organization)
    return render(request, "teacher/teacher_view_course.html", {"courses": courses})


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_update_course_view(request, pk):
    course = ExamModel.Course.objects.get(id=pk)
    courseForm = ExamForms.CourseForm(instance=course)
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = organization.id
        request.POST._mutable = False
        courseForm = ExamForms.CourseForm(request.POST, instance=course)
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.organization = organization
            course.save()
        else:
            print("form is invalid")
        return redirect("teacher-view-course")
    return render(
        request,
        "teacher/teacher_update_course.html",
        {"courseForm": courseForm, "organization_id": organization.id},
    )

@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_delete_course_view(request, pk):
    course = ExamModel.Course.objects.get(id=pk)
    if course.created_by==request.user:
        course.delete()
    else:
        return render(request, "exam/unauthorized.html")
    return redirect("teacher-view-course")


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_question_view(request):
    return render(request, "teacher/teacher_question.html")


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    og = {"organization": organization}
    questionForm = ExamForms.QuestionForm(initial=og)
    optionForm = ExamForms.OptionForm()
    if request.method == "POST":
        questionForm = ExamForms.QuestionForm(request.POST, request.FILES)
        question = questionForm.save(commit=False)
        course = ExamModel.Course.objects.get(id=request.POST.get("courseID"))
        question.course = course
        course.question_number += 1
        course.total_marks += int(request.POST.get("marks"))
        course.save()
        question.save()

        options_list = request.POST.getlist("option")
        answer = request.POST.get("answer")
        for option in options_list:
            option_obj = ExamModel.Option.objects.create(option=option, question=question)
            option_obj.save()
            if option == answer:
                answer_obj = ExamModel.Answer.objects.create(
                    question=question, answer=option_obj
                )
                answer_obj.save()
        return redirect("teacher-add-question")
    return render(
        request, "teacher/teacher_add_question.html", {"questionForm": questionForm,"optionForm":optionForm}
    )


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_question_course_view(request):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    courses = ExamModel.Course.objects.filter(organization=organization)
    return render(request, "teacher/teacher_view_question_course.html", {"courses": courses})

@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_question_view(request,pk):
    questions = ExamModel.Question.objects.filter(course_id=pk)
    return render(request, "teacher/teacher_view_question.html", {"questions": questions})


# @login_required(login_url="teacherlogin")
# @user_passes_test(is_teacher)
# def see_question_view(request, pk):
#     questions = ExamModel.Question.objects.all().filter(course_id=pk)
#     return render(request, "teacher/see_question.html", {"questions": questions})


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_update_question_view(request, pk):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    question = ExamModel.Question.objects.get(id=pk)
    question.organization = organization
    questionForm = ExamForms.QuestionForm(instance=question)
    options = ExamModel.Option.objects.filter(question=question)
    optionForms = []
    newOption=ExamForms.OptionForm()

    for option in options:
        optionForms.append(ExamForms.OptionForm(instance=option))

    answer = ExamModel.Answer.objects.get(question=question)

    if request.method == "POST":
        course = ExamModel.Course.objects.get(id=request.POST.get("courseID"))
        course.total_marks -= int(question.marks)
        questionForm = ExamForms.QuestionForm(request.POST, request.FILES,instance=question)
        question = questionForm.save(commit=False)
        question.course = course
        course.total_marks += int(request.POST.get("marks"))
        course.save()
        question.save()
        for option in options:
            option.delete()
        
        # answerForm.delete()

        options_list = request.POST.getlist("option")
        answer_resp = request.POST.get("answer")
        for option in options_list:
            option_obj = ExamModel.Option.objects.create(option=option,question=question)
            option_obj.save()
            if option == answer_resp:
                answer_obj = ExamModel.Answer.objects.create(question=question,answer=option_obj)
                answer_obj.save()

        return redirect("teacher-view-question-course")
    return render(
        request,
        "teacher/teacher_update_question.html",
        {"questionForm": questionForm, "optionForm": optionForms,"answerForm":answer.answer.option,"newOption":newOption},
    )

@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_remove_question_view(request, pk):
    question = ExamModel.Question.objects.get(id=pk)
    course = ExamModel.Course.objects.filter(course_name=question.course)[0]
    course.question_number -= 1
    course.total_marks -= question.marks
    question.delete()
    course.save()
    return redirect(request.META.get('HTTP_REFERER'))
