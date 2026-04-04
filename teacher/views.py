import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render

from exam import forms as ExamForms
from exam import models as ExamModel
from organization import models as OrganizationModel
from student import models as StudentModel
from teacher import forms as TeacherForms
from teacher import models as TeacherModel

from . import forms

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
                    if key == "mobile":
                        messages.error(request, "Please enter a valid contact number")
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
    mydict = {"userForm": user_form, "teacherForm": teacherForm}

    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] = teacher.organization_id
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
def teacher_view_student_view(request):
    students = StudentModel.Student.objects.all()
    return render(request, "teacher/teacher_view_student.html", {"students": students})

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
            question_images[img].name = (
                str(uuid.uuid4().hex) + "." + file_name.split(".")[-1]
            )
            print(question_images[img].name)

        questionForm = ExamForms.QuestionForm(request.POST, request.FILES)

        if not questionForm.is_valid():
            return render(
                request,
                "teacher/teacher_add_question.html",
                {"questionForm": questionForm, "optionForm": optionForm},
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
    if request.method == "POST":
        import uuid
        from io import BytesIO

        import openpyxl
        import pandas as pd
        from django.core.files.base import ContentFile
        from openpyxl_image_loader import SheetImageLoader

        from exam.models import Answer, Course, Option, Question

        file_obj = request.FILES.get("uploadFile")

        if not file_obj:
            messages.error(request, "No file uploaded")
            return redirect(request.META.get("HTTP_REFERER"))

        if (
            file_obj.content_type
            != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            messages.error(request, "Only xlsx files allowed")
            return redirect(request.META.get("HTTP_REFERER"))

        # IMPORTANT: reset file pointer before reading multiple times
        file_obj.seek(0)
        df = pd.read_excel(file_obj, header=None, engine="openpyxl")
        df_list = df.values.tolist()

        if not df_list:
            messages.error(request, "Excel file is empty")
            return redirect(request.META.get("HTTP_REFERER"))

        # Reset again for openpyxl
        file_obj.seek(0)
        pxl_doc = openpyxl.load_workbook(file_obj)
        sheet = pxl_doc.active
        image_loader = SheetImageLoader(sheet)

        print("------------- df_list -------------", df_list)

        course_name = df_list[0][0]

        course_obj = Course.objects.filter(course_name=course_name).first()
        if not course_obj:
            messages.error(request, "No course with the provided name")
            return redirect(request.META.get("HTTP_REFERER"))

        self_organization = TeacherModel.Teacher.objects.get(
            user=request.user.id
        ).organization
        if self_organization != course_obj.organization:
            messages.error(
                request,
                f"No course found by the name {course_name} in your organization {self_organization}",
            )
            return redirect(request.META.get("HTTP_REFERER"))

        # ✅ FIXED LOOP
        for row_number, row in enumerate(df_list, start=1):

            # skip header / invalid rows
            if len(row) < 5 or not row[1]:
                continue

            question = Question(question=row[1], marks=row[2], course=course_obj)

            # Handle image
            try:
                image = image_loader.get("D" + str(row_number))
            except Exception:
                image = None

            if image:
                image_rgb = image.convert("RGB")
                output = BytesIO()
                image_rgb.save(output, format="JPEG")
                image_data = output.getvalue()

                question.question_image.save(
                    f"{uuid.uuid4().hex}.jpg", ContentFile(image_data), save=False
                )

            question.save()

            # Update course stats
            course_obj.question_number += 1
            course_obj.total_marks += question.marks

            answer = row[-1]

            for option in row[4:-1]:
                if not option:
                    continue

                op = Option.objects.create(option=option, question=question)

                if str(answer).strip() == str(option).strip():
                    Answer.objects.create(answer=op, question=question)

        course_obj.save()  # ✅ save once at end

        messages.success(request, f"Questions added in course {course_name}")
        return redirect(request.META.get("HTTP_REFERER"))

    else:
        return render(request, "teacher/teacher_upload_question_file.html")


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


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_update_question_view(request, pk):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    question = ExamModel.Question.objects.get(id=pk)
    question_image = question.question_image.name
    if question_image == "":
        question_image = False
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
                    "question_image": question_image,
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
            "question_image": question_image,
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
    courses = ExamModel.Course.objects.filter(
        organization=organization, created_by=request.user
    )
    response = render(
        request, "teacher/teacher_view_result_courses.html", {"courses": courses}
    )
    return response


@login_required(login_url="teacherlogin")
@user_passes_test(is_teacher)
def teacher_view_marks(request, pk):
    organization = TeacherModel.Teacher.objects.get(user=request.user.id).organization
    results = ExamModel.Result.objects.filter(
        exam__id=pk, exam__organization=organization
    )
    response = render(request, "teacher/teacher_check_marks.html", {"results": results})
    return response
