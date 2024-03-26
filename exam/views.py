from django.shortcuts import render, redirect
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.mail import send_mail
from teacher import models as TMODEL
from student import models as SMODEL
from organization import models as OMODEL
from exam import models as EMODEL
from teacher import forms as TFORM
from student import forms as SFORM
from organization import forms as OFORM
from exam import forms as EFORM
from django.contrib.auth.models import User


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


def afterlogin_view(request):
    if is_student(request.user):
        return redirect("student/student-dashboard")

    elif is_teacher(request.user):
        accountapproval = TMODEL.Teacher.objects.all().filter(
            user_id=request.user.id, status=True
        )
        if accountapproval:
            return redirect("teacher/teacher-dashboard")
        else:
            return render(request, "teacher/teacher_wait_for_approval.html")

    elif is_organization(request.user):
        accountapproval = OMODEL.Organization.objects.all().filter(
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
        "salary": TMODEL.Teacher.objects.all()
        .filter(status=True)
        .aggregate(Sum("salary"))["salary__sum"],
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
    teacherSalary = EFORM.TeacherSalaryForm()
    if request.method == "POST":
        teacherSalary = EFORM.TeacherSalaryForm(request.POST)
        if teacherSalary.is_valid():
            teacher = TMODEL.Teacher.objects.get(id=pk)
            teacher.salary = teacherSalary.cleaned_data["salary"]
            teacher.status = True
            teacher.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect("/admin-view-pending-teacher")
    return render(request, "exam/salary_form.html", {"teacherSalary": teacherSalary})


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
def admin_view_teacher_salary_view(request):
    teachers = TMODEL.Teacher.objects.all().filter(status=True)
    return render(
        request, "exam/admin_view_teacher_salary.html", {"teachers": teachers}
    )


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
    OrganizationFees = EFORM.OrganizationFeesForm()
    if request.method == "POST":
        OrganizationFees = EFORM.OrganizationFeesForm(request.POST)
        if OrganizationFees.is_valid():
            organization = OMODEL.Organization.objects.get(id=pk)
            organization.fees = OrganizationFees.cleaned_data["fees"]
            organization.status = True
            organization.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect("/admin-view-pending-teacher")
    return render(
        request, "exam/fees_form.html", {"OrganizationFees": OrganizationFees}
    )


@login_required(login_url="adminlogin")
@user_passes_test(is_admin)
def reject_organization_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect("/admin-view-pending-teacher")


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
def admin_question_view(request):
    return render(request, "exam/admin_question.html")


@login_required(login_url="adminlogin")
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
        answer_pos = int(request.POST.get("answer").split(" ")[1]) - 1
        for option in options_list:
            option_obj = EMODEL.Option.objects.create(option=option, question=question)
            option_obj.save()
            if option == options_list[answer_pos]:
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
def admin_view_question_view(request):
    courses = EMODEL.Course.objects.all()
    return render(request, "exam/admin_view_question.html", {"courses": courses})


@login_required(login_url="adminlogin")
def view_question_view(request, pk):
    questions = EMODEL.Question.objects.all().filter(course_id=pk)
    return render(request, "exam/view_question.html", {"questions": questions})


@login_required(login_url="adminlogin")
def delete_question_view(request, pk):
    question = EMODEL.Question.objects.get(id=pk)
    question.delete()
    course = EMODEL.Course.objects.all().filter(course_name=question.course)[0]
    course.question_number -= 1
    course.total_marks -= question.marks
    course.save()
    return HttpResponseRedirect("/admin-view-question")


@login_required(login_url="adminlogin")
def admin_view_student_marks_view(request):
    students = SMODEL.Student.objects.all()
    return render(request, "exam/admin_view_student_marks.html", {"students": students})


@login_required(login_url="adminlogin")
def admin_view_marks_view(request, pk):
    courses = EMODEL.Course.objects.all()
    response = render(request, "exam/admin_view_marks.html", {"courses": courses})
    response.set_cookie("student_id", str(pk))
    return response


@login_required(login_url="adminlogin")
def admin_check_marks_view(request, pk):
    course = EMODEL.Course.objects.get(id=pk)
    student_id = request.COOKIES.get("student_id")
    student = SMODEL.Student.objects.get(user_id=student_id)
    results = EMODEL.Result.objects.all().filter(exam=course).filter(student=student)

    return render(request, "exam/admin_check_marks.html", {"results": results})


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
            send_mail(
                str(name) + " || " + str(email),
                message,
                settings.EMAIL_HOST_USER,
                settings.EMAIL_RECEIVING_USER,
                fail_silently=False,
            )
            return render(request, "exam/contactussuccess.html")
    return render(request, "exam/contactus.html", {"form": sub})
