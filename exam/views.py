from django.shortcuts import render, redirect
from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from teacher import models as TMODEL
from student import models as SMODEL
from organization import models as OMODEL
from exam import models as EMODEL
from teacher import forms as TFORM
from student import forms as SFORM
from organization import forms as OFORM
from exam import forms as EFORM
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import messages
from onlinexam.settings import STATIC_DIR


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return render(request, "exam/index.html")


def is_teacher(user):
    return user.groups.filter(name="TEACHER").exists()


def is_student(user):
    return user.groups.filter(name="STUDENT").exists()


def is_organization(user):
    return user.groups.filter(name="ORGANIZATION").exists()


def is_admin(user):
    return user.is_superuser

def is_admin_is_teacher_is_organization(user):
    return user.groups.filter(name="TEACHER").exists() or user.groups.filter(name="ORGANIZATION").exists() or user.is_superuser

def afterlogin_view(request):
    if is_student(request.user):
        response = redirect("student/student-dashboard")
        org = SMODEL.Student.objects.filter(user=request.user).first().organization
        response.set_cookie("organization", org)
        return response

    elif is_teacher(request.user):
        accountapproval = TMODEL.Teacher.objects.filter(
            user_id=request.user.id, status=True
        )
        if accountapproval:
            response = redirect("teacher/teacher-dashboard")
            response.set_cookie("organization", accountapproval.first().organization)
            return response
        else:
            return render(request, "teacher/teacher_wait_for_approval.html")

    elif is_organization(request.user):
        accountapproval = OMODEL.Organization.objects.filter(
            user_id=request.user.id, status=True
        )
        if accountapproval:
            return redirect("organization/organization-dashboard")
        else:
            return render(request, "organization/organization_wait_for_approval.html")

    elif is_admin(request.user):
        return redirect("admin-dashboard")
    else:
        return redirect("invalid-user")


def invalid_user(request):
    return render(request, "exam/invalid_user.html")


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return HttpResponseRedirect("adminlogin")


def delete_account(request):
    """
    delete a user account
    """
    username = request.user.username
    user_obj = User.objects.filter(Q(username=username)).first()

    if is_organization(request.user):
        org = OMODEL.Organization.objects.filter(user_id=request.user.id).first()
        # org.delete()
        teachers = TMODEL.Teacher.objects.filter(organization=org)
        students = SMODEL.Student.objects.filter(organization=org)

        # Delete related teacher profiles and user entries
        for teacher in teachers:
            teacher.user.delete()
            # teacher.delete()

        # Delete related student profiles and user entries
        for student in students:
            student.user.delete()
            # student.delete()
    user_obj.delete()

@login_required(login_url="afterlogin")
def delete_account_view(request):
    """
    view for confirming the user's account deletion 
    """
    context = {}
    if is_student(request.user):
        context['base_template'] = 'student/studentbase.html'
    elif is_teacher(request.user):
        context['base_template'] = 'teacher/teacherbase.html'
    elif is_organization(request.user):
        context['base_template'] = 'organization/organization.html'
    elif is_admin(request.user):
        context['base_template'] = 'exam/adminbase.html'

    if request.method == "POST":
        # delete the user's account, after confirmation
        delete_account(request)
        return redirect('')
    return render(request, 'common/delete_account_view.html', context=context)



@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    dict = {
        "total_student": SMODEL.Student.objects.all().count(),
        "total_teacher": TMODEL.Teacher.objects.all().filter(status=True).count(),
        "total_course": EMODEL.Course.objects.all().count(),
        "total_question": EMODEL.Question.objects.all().count(),
        "total_organizations": OMODEL.Organization.objects.all()
        .filter(status=True)
        .count(),
    }
    return render(request, "exam/admin_dashboard.html", context=dict)


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_teacher_view(request):
    dict = {
        "total_teacher": TMODEL.Teacher.objects.all().filter(status=True).count(),
        "pending_teacher": TMODEL.Teacher.objects.all().filter(status=False).count(),
    }
    return render(request, "exam/admin_teacher.html", context=dict)


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_teacher_view(request):
    teachers = TMODEL.Teacher.objects.all().filter(status=True)
    return render(request, "exam/admin_view_teacher.html", {"teachers": teachers})


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_organization_view(request):
    dict = {
        "total_organization": OMODEL.Organization.objects.all()
        .filter(status=True)
        .count(),
        "pending_organization": OMODEL.Organization.objects.all()
        .filter(status=False)
        .count(),
        "fees": OMODEL.Organization.objects.all()
        .filter(status=True)
        .aggregate(Sum("fees"))["fees__sum"],
    }
    return render(request, "exam/admin_organization.html", context=dict)


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_organization_view(request):
    organizations = OMODEL.Organization.objects.all().filter(status=True)
    return render(
        request, "exam/admin_view_organization.html", {"organizations": organizations}
    )


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def update_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = TMODEL.User.objects.get(id=teacher.user_id)
    userForm = EFORM.UserUpdateForm(instance=user)
    teacherForm = TFORM.TeacherForm(instance=teacher)
    mydict = {"userForm": userForm, "teacherForm": teacherForm}
    if request.method == "POST":
        userForm = EFORM.UserUpdateForm(request.POST, instance=user)
        teacherForm = TFORM.TeacherForm(request.POST, instance=teacher)

        if userForm.is_valid() and teacherForm.is_valid():
            user = userForm.save()
            user.save()
            teacher = teacherForm.save(commit=False)
            teacher.organization = OMODEL.Organization.objects.get(
                id=request.POST.get("organizationID")
            )
            teacher.save()
            return redirect("admin-view-teacher")
    return render(request, "exam/update_teacher.html", context=mydict)


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def delete_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect("/admin-view-teacher")


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def update_organization_view(request, pk):
    organization = OMODEL.Organization.objects.get(id=pk)
    user = OMODEL.User.objects.get(id=organization.user_id)
    userForm = OFORM.OrganizationUserForm(instance=user)
    organizationForm = OFORM.OrganizationForm(instance=organization)
    mydict = {"userForm": userForm, "organizationForm": organizationForm}

    if request.method == "POST":
        userForm = EFORM.UserUpdateForm(request.POST, instance=user)
        organizationForm = OFORM.OrganizationForm(request.POST, instance=organization)
        if userForm.is_valid() and organizationForm.is_valid():
            user = userForm.save()
            user.save()
            organizationForm.save()
            return redirect("admin-view-organization")
    return render(request, "exam/update_organization.html", context=mydict)


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def delete_organization_view(request, pk):
    organization = OMODEL.Organization.objects.get(id=pk)
    user = User.objects.get(id=organization.user_id)
    user.delete()
    organization.delete()
    return HttpResponseRedirect("/admin-view-organization")


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_pending_teacher_view(request):
    teachers = TMODEL.Teacher.objects.all().filter(status=False)
    return render(
        request, "exam/admin_view_pending_teacher.html", {"teachers": teachers}
    )


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_pending_organization_view(request):
    organizations = OMODEL.Organization.objects.all().filter(status=False)
    return render(
        request,
        "exam/admin_view_pending_organization.html",
        {"organizations": organizations},
    )


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def approve_teacher_view(request, pk):
    if request.method == "POST":
        teacher = TMODEL.Teacher.objects.get(id=pk)
        teacher.status = True
        teacher.save()
    else:
        print("Not a valid request type")
        return HttpResponseRedirect("/admin-view-pending-teacher")
    return redirect('approve-teacher', pk = pk)


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def reject_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect("/admin-view-pending-teacher")


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_organization_fees_view(request):
    organizations = OMODEL.Organization.objects.all().filter(status=True)
    return render(
        request,
        "exam/admin_view_organization_fees.html",
        {"organizations": organizations},
    )


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def approve_organization_view(request, pk):
    try:
        organization = OMODEL.Organization.objects.get(id=pk)
        organization.status = True
        organization.save()
    except Exception as e:
        print("Error on approving organization from admin {e}")
    return redirect('admin-view-pending-organization')


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def reject_organization_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect("/admin-view-pending-organization")


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_student_view(request):
    dict = {
        "total_student": SMODEL.Student.objects.all().count(),
    }
    return render(request, "exam/admin_student.html", context=dict)


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_student_view(request):
    students = SMODEL.Student.objects.all()
    return render(request, "exam/admin_view_student.html", {"students": students})


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def update_student_view(request, pk):
    student = SMODEL.Student.objects.get(id=pk)
    user = SMODEL.User.objects.get(id=student.user_id)
    userForm = EFORM.UserUpdateForm(instance=user)
    studentForm = SFORM.StudentForm(instance=student)
    mydict = {"userForm": userForm, "studentForm": studentForm}
    if request.method == "POST":
        userForm = EFORM.UserUpdateForm(request.POST, instance=user)
        studentForm = SFORM.StudentForm(request.POST, instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.save()
            student = studentForm.save(commit=False)
            student.organization = OMODEL.Organization.objects.get(
                id=request.POST.get("organizationID")
            )
            student.save()
            return redirect("admin-view-student")
    return render(request, "exam/update_student.html", context=mydict)


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def delete_student_view(request, pk):
    student = SMODEL.Student.objects.get(id=pk)
    user = User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect("/admin-view-student")


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_course_view(request):
    return render(request, "exam/admin_course.html")


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_add_course_view(request):
    courseForm = EFORM.CourseForm()
    if request.method == "POST":
        organization = OMODEL.Organization.objects.get(
            id=request.POST.get("organizationID")
        )
        courseForm = EFORM.CourseForm(request.POST)
        print(f"{courseForm.errors = }")
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.organization = organization
            course.created_by = request.user
            courseForm.save()
        else:
            print("form is invalid")
            print(f"{courseForm.errors = }")
            messages.error(request, courseForm.errors)
            return render(request, "exam/admin_add_course.html", {"courseForm": courseForm})
        return HttpResponseRedirect("/admin-view-course")
    return render(request, "exam/admin_add_course.html", {"courseForm": courseForm})


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_course_view(request):
    courses = EMODEL.Course.objects.all()
    return render(request, "exam/admin_view_course.html", {"courses": courses})


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def delete_course_view(request, pk):
    course = EMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect("/admin-view-course")


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def update_course_view(request, pk):
    course = EMODEL.Course.objects.get(id=pk)
    courseForm = EFORM.CourseForm(instance=course)
    if request.method == "POST":
        organization = OMODEL.Organization.objects.get(
            id=request.POST["organizationID"]
        )
        courseForm = EFORM.CourseForm(request.POST, instance=course)
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.organization = organization
            course.save()
        else:
            print("form is invalid")
        return redirect("admin-view-course")
    return render(
        request,
        "exam/update_course.html",
        {"courseForm": courseForm},
    )


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_question_view(request):
    return render(request, "exam/admin_question.html")


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_add_question_view(request):
    questionForm = EFORM.QuestionForm()
    optionForm = EFORM.OptionForm()
    if request.method == "POST":
        questionForm = EFORM.QuestionForm(request.POST, request.FILES)
        question = questionForm.save(commit=False)
        course = EMODEL.Course.objects.get(id=request.POST.get("courseID"))
        question.course = course
        course.question_number += 1
        course.total_marks += int(request.POST.get("marks"))
        course.save()
        question.save()

        options_list = request.POST.getlist("option")
        answer = request.POST.get("answer")
        for option in options_list:
            option_obj = EMODEL.Option.objects.create(option=option, question=question)
            option_obj.save()
            if option == answer:
                answer_obj = EMODEL.Answer.objects.create(
                    question=question, answer=option_obj
                )
                answer_obj.save()
        return redirect("admin-add-question")
    return render(
        request,
        "exam/admin_add_question.html",
        {"questionForm": questionForm, "optionForm": optionForm},
    )


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_upload_questions_file(request):
    if request.method == "POST":
        import pandas as pd
        import openpyxl
        import uuid
        from openpyxl_image_loader import SheetImageLoader
        from exam.models import Course, Question, Option, Answer
        from django.core.files.base import ContentFile
        from io import BytesIO

        file_obj = request.FILES.get("uploadFile")
        if (
            file_obj.content_type
            != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            messages.error(request, "Only xlsx files allowed")
            return redirect(request.META.get("HTTP_REFERER"))

        df = pd.read_excel(file_obj, header=None, engine="openpyxl")
        df_list = df.values.tolist()
        # Load the Excel workbook and sheet
        pxl_doc = openpyxl.load_workbook(file_obj)
        sheet = pxl_doc["Sheet1"]
        image_loader = SheetImageLoader(sheet)
        last_row = sheet.max_row

        for row_number in range(1, last_row + 1):
            course_name = df_list[row_number-1][0]
            course_obj = Course.objects.filter(course_name=course_name).first()
            if not course_obj:
                continue
            question = Question()
            row = df_list[row_number - 1]
            question.question = row[1]
            question.marks = row[2]
            question.course = course_obj
            try:
                image = image_loader.get("D" + str(row_number))
            except Exception as e:
                image = None
            if image:
                image_rgb = image.convert("RGB")
                output = BytesIO()
                image_rgb.save(output, format="JPEG")
                image_data = output.getvalue()
                question.question_image.save(
                    f"{uuid.uuid4().hex}.jpg", ContentFile(image_data)
                )
            question.save()
            course_obj.question_number += 1
            course_obj.total_marks += question.marks
            course_obj.save()
            answer = row[-1]
            for option in row[4:-1]:
                op = Option.objects.create(option=option, question=question)
                op.save()
                if answer == option:
                    ans = Answer.objects.create(answer=op, question=question)
                    ans.save()
        messages.success(request, f"questions added in course {course_name}")
        return redirect(request.META.get("HTTP_REFERER"))
    else:
        return render(request, "exam/admin_upload_question_file.html")


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_update_question_view(request, pk):
    question = EMODEL.Question.objects.get(id=pk)
    question.organization = question.course.organization
    question_image = question.question_image.name
    if question_image=="":
        question_image=False
    questionForm = EFORM.QuestionForm(instance=question)
    options = EMODEL.Option.objects.filter(question=question)
    optionForms = []
    newOption = EFORM.OptionForm()

    for option in options:
        optionForms.append(EFORM.OptionForm(instance=option))

    answer = EMODEL.Answer.objects.get(question=question)

    if request.method == "POST":
        course = EMODEL.Course.objects.get(id=request.POST.get("courseID"))
        course.total_marks -= int(question.marks)
        questionForm = EFORM.QuestionForm(
            request.POST, request.FILES, instance=question
        )
        
        if not questionForm.is_valid():
            return render(
                request,
                "exam/admin_update_question.html",
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
            option_obj = EMODEL.Option.objects.create(option=option, question=question)
            option_obj.save()
            if option == answer_resp:
                answer_obj = EMODEL.Answer.objects.create(
                    question=question, answer=option_obj
                )
                answer_obj.save()

        return redirect(request.META.get("HTTP_REFERER"))
    return render(
        request,
        "exam/admin_update_question.html",
        {
            "questionForm": questionForm,
            "optionForm": optionForms,
            "answerForm": answer.answer.option,
            "newOption": newOption,
            "question_image": question_image
        },
    )


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_question_view(request):
    courses = EMODEL.Course.objects.all()
    return render(request, "exam/admin_view_question.html", {"courses": courses})


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def view_question_view(request, pk):
    questions = EMODEL.Question.objects.all().filter(course_id=pk)
    return render(request, "exam/view_question.html", {"questions": questions})


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def delete_question_view(request, pk):
    question = EMODEL.Question.objects.get(id=pk)
    course = EMODEL.Course.objects.all().filter(course_name=question.course)[0]
    course.question_number -= 1
    course.total_marks -= question.marks
    question.delete()
    course.save()
    return redirect(request.META.get("HTTP_REFERER"))


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_student_marks_view(request):
    students = SMODEL.Student.objects.all()
    return render(request, "exam/admin_view_student_marks.html", {"students": students})


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_view_marks_view(request, pk):
    student = SMODEL.Student.objects.get(user=pk)
    courses = EMODEL.Course.objects.filter(organization=student.organization)
    response = render(request, "exam/admin_view_marks.html", {"courses": courses})
    response.set_cookie("student_id", str(pk))
    return response


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def admin_check_marks_view(request, pk):
    course = EMODEL.Course.objects.get(id=pk)
    student_id = request.COOKIES.get("student_id")
    student = SMODEL.Student.objects.get(user_id=student_id)
    results = EMODEL.Result.objects.all().filter(exam=course).filter(student=student)

    return render(request, "exam/admin_check_marks.html", {"results": results})

@login_required(login_url="afterlogin")
@user_passes_test(is_admin_is_teacher_is_organization)
def delete_result(request,pk):
    result_obj = EMODEL.Result.objects.get(id=pk)
    result_obj.delete()
    return redirect(request.META.get("HTTP_REFERER"))



def aboutus_view(request):
    return render(request, "exam/aboutus.html")


def contactus_view(request):
    sub = EFORM.ContactusForm()
    if request.method == "POST":
        sub = EFORM.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data["Email"]
            name = sub.cleaned_data["Name"]
            message = sub.cleaned_data["Message"]

            mail = EmailMultiAlternatives(
                subject =  f"{name} || {email} sent a message from Online Examination Portal",
                body= f"Message : {message}",
                from_email=settings.EMAIL_HOST_USER,
                bcc=[email],
                to=list(settings.EMAIL_RECEIVING_USER)
            )
            mail.send(fail_silently=False)
            return render(request, "exam/contactussuccess.html")
    return render(request, "exam/contactus.html", {"form": sub})


def download_question_file_format(request):
    file = STATIC_DIR + "/samples/question_format.xlsx"
    with open(str(file), "rb") as f:
        file_data = f.read()
        response = HttpResponse(file_data)
        response["Content-Type"] = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment;filename=question_format.xlsx"
        return response


def download_sample_question_file(request):
    file = STATIC_DIR + "/samples/sample_question_file.xlsx"
    with open(str(file), "rb") as f:
        file_data = f.read()
        response = HttpResponse(file_data)
        response["Content-Type"] = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment;filename=sample_question_file.xlsx"
        return response