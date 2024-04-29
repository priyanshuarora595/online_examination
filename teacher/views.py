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
from django.contrib import messages
import hashlib
from datetime import datetime

import uuid

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
        request.POST._mutable = True
        # request.POST["salary"] = 0
        request.POST._mutable = False
        userForm = forms.TeacherUserForm(request.POST)
        teacherForm = forms.TeacherForm(request.POST, request.FILES)
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
        else:
            if userForm.errors:
                for key, val in userForm.errors.as_data().items():
                    messages.error(request, val[0].message)
            if teacherForm.errors:
                for key, val in teacherForm.errors.as_data().items():
                    if(key == 'mobile'):
                        messages.error(request, 'Please enter a valid contact number')
                    else:
                        messages.error(request, val[0].message)
            mydict = {"userForm": userForm, "teacherForm": teacherForm}
    return render(request, "teacher/teachersignup.html", context=mydict)


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_profile_view(request):
    teacher = TeacherModel.Teacher.objects.get(user=request.user)
    user = TeacherModel.User.objects.get(id=teacher.user_id)
    user_form = ExamForms.UserUpdateForm(instance=user)
    teacherForm = TeacherForms.TeacherForm(instance=teacher)

    # making the username field read only
    user_form.fields["username"].widget.attrs["readonly"] = True
    # user_form.fields["email"].widget.attrs["readonly"] = True

    # teacherForm.fields["salary"].widget.attrs["readonly"] = True
    mydict = {"userForm": user_form, "teacherForm": teacherForm}

    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = teacher.organization_id
        # request.POST["salary"] = teacher.salary
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
        "total_course": ExamModel.Course.objects.filter(
            organization=organization
        ).count(),
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
    return render(
        request, "teacher/teacher_add_course.html", {"courseForm": courseForm}
    )


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
            messages.error(request, "Please check the details again!")
            return redirect(request.META.get("HTTP_REFERER"))
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
    if course.created_by == request.user:
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
        question_images = request.FILES
        for img in question_images:
            file_name = str(question_images[img].name)
            question_images[img].name = str(uuid.uuid4().hex) + "." + file_name.split('.')[-1]
            print(question_images[img].name)
            
        questionForm = ExamForms.QuestionForm(request.POST, request.FILES)
        
        if not questionForm.is_valid():
            return render(
                    request,
                    "teacher/teacher_add_question.html",
                    {
                        "questionForm": questionForm,
                        "optionForm": optionForm
                    },
                )
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
            option_obj = ExamModel.Option.objects.create(
                option=option, question=question
            )
            option_obj.save()
            if option == answer:
                answer_obj = ExamModel.Answer.objects.create(
                    question=question, answer=option_obj
                )
                answer_obj.save()
        return redirect("teacher-add-question")
    return render(
        request,
        "teacher/teacher_add_question.html",
        {"questionForm": questionForm, "optionForm": optionForm},
    )
@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_upload_questions_file(request):
    if request.method=="POST":
        import pandas as pd
        import openpyxl
        import uuid
        from openpyxl_image_loader import SheetImageLoader
        from exam.models import Course,Question,Option,Answer
        from django.core.files.base import ContentFile
        from io import BytesIO
        file_obj = request.FILES.get("uploadFile")
        if file_obj.content_type!='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            messages.error(request, "Only xlsx files allowed")
            return redirect(request.META.get("HTTP_REFERER"))

        df = pd.read_excel(file_obj,header=None,engine='openpyxl')
        df_list = df.values.tolist()
        # Load the Excel workbook and sheet
        pxl_doc = openpyxl.load_workbook(file_obj)
        sheet = pxl_doc['Sheet1']
        image_loader = SheetImageLoader(sheet)
        last_row = sheet.max_row
        course_name = df_list[0][0]
        # return redirect(request.META.get("HTTP_REFERER"))
        # return None
        course_obj = Course.objects.filter(course_name=course_name).first()
        if not course_obj:
            messages.error(request, "No course with the provided name")
            return redirect(request.META.get("HTTP_REFERER"))
        
        self_organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
        if self_organization!=course_obj.organization:
            messages.error(request, f"No course found by the name {course_name} in your organization {self_organization}")
            return redirect(request.META.get("HTTP_REFERER"))
        
        for row_number in range(1, last_row + 1):
            question = Question()
            row = df_list[row_number - 1]
            question.question = row[1]
            question.marks = row[2]
            question.course = course_obj
            try:
                image = image_loader.get("D"+str(row_number))
            except Exception as e:
                image = None
            if image:
                image_rgb = image.convert('RGB')
                output = BytesIO()
                image_rgb.save(output, format='JPEG')
                image_data = output.getvalue()
                question.question_image.save(f'{uuid.uuid4().hex}.jpg', ContentFile(image_data))
            question.save()
            course_obj.question_number+=1
            course_obj.total_marks+=question.marks
            course_obj.save()
            answer = row[-1]
            for option in row[4:-1]:
                op =  Option.objects.create(option=option, question=question)
                op.save()
                if answer == option:
                    ans = Answer.objects.create(answer=op,question=question)
                    ans.save()
        messages.success(request, f"questions added in course {course_name}")
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        return render(request,"teacher/teacher_upload_question_file.html")

@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_question_course_view(request):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    courses = ExamModel.Course.objects.filter(organization=organization)
    return render(
        request, "teacher/teacher_view_question_course.html", {"courses": courses}
    )


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_question_view(request, pk):
    questions = ExamModel.Question.objects.filter(course_id=pk)
    return render(
        request, "teacher/teacher_view_question.html", {"questions": questions}
    )


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
    question_image = question.question_image.name
    if question_image=="":
        question_image=False
    question.organization = organization
    questionForm = ExamForms.QuestionForm(instance=question)
    options = ExamModel.Option.objects.filter(question=question)
    optionForms = []
    newOption = ExamForms.OptionForm()

    for option in options:
        optionForms.append(ExamForms.OptionForm(instance=option))

    answer = ExamModel.Answer.objects.get(question=question)

    if request.method == "POST":
        course = ExamModel.Course.objects.get(id=request.POST.get("courseID"))
        course.total_marks -= int(question.marks)
        questionForm = ExamForms.QuestionForm(
            request.POST, request.FILES, instance=question
        )
        if not questionForm.is_valid():
            return render(
                request,
                "teacher/teacher_update_question.html",
                {
                    "questionForm": questionForm,
                    "optionForm": optionForms,
                    "answerForm": answer.answer.option,
                    "newOption": newOption,
                    "question_image": question_image
                },
            )
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
            option_obj = ExamModel.Option.objects.create(
                option=option, question=question
            )
            option_obj.save()
            if option == answer_resp:
                answer_obj = ExamModel.Answer.objects.create(
                    question=question, answer=option_obj
                )
                answer_obj.save()

        return redirect(request.META.get("HTTP_REFERER"))
    return render(
        request,
        "teacher/teacher_update_question.html",
        {
            "questionForm": questionForm,
            "optionForm": optionForms,
            "answerForm": answer.answer.option,
            "newOption": newOption,
            "question_image": question_image
        },
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
    return redirect(request.META.get("HTTP_REFERER"))

@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_results_courses(request):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    courses = ExamModel.Course.objects.filter(organization=organization,created_by=request.user)
    response = render(
        request, "teacher/teacher_view_result_courses.html", {"courses": courses}
    )
    return response

@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_marks(request,pk):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    # courses = ExamModel.Course.objects.filter(organization=organization,created_by=request.user)
    # students = StudentModel.Student.objects.filter(organization=organization,)
    results = ExamModel.Result.objects.filter(exam__id=pk)
    response = render(
        request, "teacher/teacher_check_marks.html", {"results": results}
    )
    print(results)
    # response.set_cookie("student_id", str(pk))
    return response