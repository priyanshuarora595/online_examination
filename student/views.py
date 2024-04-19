from django.shortcuts import render,redirect
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect 
from django.contrib.auth.decorators import login_required,user_passes_test

from exam import models as QuestionModel
from exam import forms as ExamForms

from student import forms as StudentForms
from student import models as StudentModel

from organization import models as OrganizationModel

from django.core.paginator import Paginator
import json
import datetime

from django.contrib import messages

#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=StudentForms.StudentUserForm()
    studentForm=StudentForms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=StudentForms.StudentUserForm(request.POST)
        studentForm=StudentForms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.organization = OrganizationModel.Organization.objects.get(
                id=request.POST.get("organizationID")
            )
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
            return HttpResponseRedirect('studentlogin')
        else:
            if userForm.errors:
                for key,val in userForm.errors.as_data().items():
                    messages.error(request,val[0].message)
            if studentForm.errors:
                for key,val in studentForm.errors.as_data().items():
                    messages.error(request,val[0].message)
            mydict = {"userForm": userForm, "studentForm": studentForm}
    return render(request,'student/studentsignup.html',context=mydict)


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_profile_view(request):
    student = StudentModel.Student.objects.get(user=request.user)
    user = StudentModel.User.objects.get(id=request.user.id)
    user_form = ExamForms.UserUpdateForm(instance=user)
    student_form = StudentForms.StudentForm(instance = student)

    # making the username field read only    
    user_form.fields['username'].widget.attrs['readonly'] = True
    # user_form.fields['email'].widget.attrs['readonly'] = True

    page_context  = {
        "userForm": user_form,
        "studentForm": student_form
    }

    if request.method == "POST":
        request.POST._mutable = True
        request.POST["organizationID"] =student.organization.id
        request.POST._mutable = False
        
        user_form = ExamForms.UserUpdateForm(request.POST, instance=user)
        student_form = StudentForms.StudentForm(request.POST, instance=student)
        
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save()
            user.save()
            student_form.save()
            return redirect("student-profile")
        else:
            return render(request, "exam/unauthorized.html")
    return render(request, "student/update_student.html", context=page_context)


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    student = StudentModel.Student.objects.get(user=request.user.id)
    dict={
    'total_course':QuestionModel.Course.objects.filter(organization=student.organization).count()
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    student = StudentModel.Student.objects.get(user=request.user.id)
    courses=QuestionModel.Course.objects.filter(organization=student.organization)
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    # print(request.session.keys())
    # if 'filtered' in request.session:
    #     del request.session['filtered']
    #     del request.session['start_time']
    #     del request.session['remaining_time']
    course=QuestionModel.Course.objects.get(id=pk)
    student = StudentModel.Student.objects.get(user=request.user.id)
    
    if course.organization.id!=student.organization.id:
        return render(request,"exam/unauthorized.html")
    return render(request,'student/take_exam.html',{'course':course})


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def verify_exam_view(request,pk,access_code):
    course=QuestionModel.Course.objects.get(id=pk)
    student = StudentModel.Student.objects.get(user=request.user.id)
    if course.organization.id!=student.organization.id:
        messages.error(request, f"You are unauthorized. This course does not beloing to your organization")
        return redirect(request.META.get('HTTP_REFERER'))

    if course:
        if access_code!=str(course.access_code):
            messages.error(request, "Invalid Access Code")
            response = redirect(request.META.get('HTTP_REFERER'))
            return response
        
        if QuestionModel.Result.objects.filter(student=student,exam=course).exists():
            messages.error(request, "You have already taken this exam.")
            return redirect(request.META.get('HTTP_REFERER'))

        if datetime.datetime.now()<course.exam_date:
            messages.error(request, f"Exam Has not started yet")
            return redirect(request.META.get('HTTP_REFERER'))
        
        entry_before = course.exam_date+datetime.timedelta(minutes=course.entry_time)
        if entry_before < datetime.datetime.now():
            messages.error(request, f"Entry Time up. You can not enter the exam now.")
            return redirect(request.META.get('HTTP_REFERER'))
        
        response = redirect("start-exam",pk=pk)
        response.set_cookie("allow","True")
        return response
        

    else:
        messages.error(request, "Invalid Course!!")
        response = redirect(request.META.HTTP_REFERER)
    return response

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    if request.COOKIES.get('allow')!="True":
        messages.error(request, f"Not Allowed")
        return redirect('take-exam',pk=pk)
    
    fil=0
    course=QuestionModel.Course.objects.get(id=pk)
        
    if 'remaining_time' not in request.session:
            remaining_time = int(course.duration) * 60
            request.session['remaining_time'] = int(remaining_time)
    else:
        remaining_time = request.session['remaining_time']
            
    if 'filtered' not in request.session:
        fil=1
        questions,question_id_list,selected_ids=QuestionModel.Question.get_random(course=course,n=course.question_number)

        if len(questions)<1:
            messages.error(request, f"No questions Available")
            return redirect('take-exam',pk=pk)
        
        request.session['filtered'] = '1'
        request.session['question_id_list'] = question_id_list
        request.session['course_id'] = pk
        request.session['page_number'] = 1
        request.session['selected_ids'] = selected_ids
        paginator = Paginator(questions,1)
        page_number = 1
        final_questions = paginator.get_page(page_number)
        options = QuestionModel.Option.objects.filter(question=final_questions.object_list[0])
        
    else:
        questions_ = QuestionModel.Question.get_from_list(course=course,id_list=request.session['question_id_list'])
        if len(questions_)<1:
            messages.error(request, f"No questions Available")
            return redirect('take-exam',pk=pk)
        paginator = Paginator(questions_,1) 
        page_number = request.GET.get("page")
        final_questions = paginator.get_page(page_number)
        options = QuestionModel.Option.objects.filter(question=final_questions.object_list[0])


    response = render(request,'student/start_exam.html',{'course':course,'questions':final_questions,'options':options})
    response.set_cookie("course_id",pk)
    if(fil==1):
        response.set_cookie("remaining_time",remaining_time)

    return response
        

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    # print(request.COOKIES.get('course_id'))
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course=QuestionModel.Course.objects.get(id=course_id)
        answers=json.loads(request.COOKIES.get("data"))
        # print(answers)
        # question_ids = request.session['question_id_list']
        # question_ids = list(map(lambda x: int(x) -1,question_ids))
        # answers = list(answers.values())
        # print(question_ids)
        # questions_ = QuestionModel.Question.get_from_list(course=course,id_list=question_ids)
        # print(questions_)
        
        correct_answers=0
        scored_marks=0
        # questions=QuestionModel.Question.objects.all().filter(course=course)
        # attempted_questions = len(answers.values())
        # total_marks=attempted_questions
        for k,v in answers.items():
            q = QuestionModel.Question.objects.all().filter(id=k)[0]
            selected_ans = v
            actual_answer = QuestionModel.Answer.objects.filter(question=q)[0].answer.option
            
            if selected_ans == actual_answer:
                correct_answers+=1
                scored_marks +=q.marks

        student = StudentModel.Student.objects.get(user_id=request.user.id)
        result = QuestionModel.Result()
        result.marks = course.total_marks
        result.exam=course
        result.student=student
        
        # if attempted_questions>=75:
        #     result.status="Pass"
        #     if correct_answers>=75:
        #         result.correct_answers = correct_answers
        #         result.percentage = correct_answers
        #     else:
        #         # print("actual correct answers = ",correct_answers)
        #         correct_answers = random.randint(75,80)
        #         result.correct_answers = correct_answers
        #         result.percentage = correct_answers
        # elif attempted_questions<75:
        #     result.status="Fail"
        #     result.correct_answers = correct_answers
        #     result.percentage = correct_answers

        correct_answers_percentage = (scored_marks/course.total_marks)*100
        if correct_answers_percentage>=course.passing_percentage:
            result.status="Pass"
        else:
            result.status="Fail"
        result.correct_answers = int(correct_answers)
        result.percentage = round(correct_answers_percentage,2)


        result.save()
        
        del request.session['remaining_time'] 
        response = redirect('view-result')
        response.delete_cookie('data')
        return response



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    student = StudentModel.Student.objects.get(user=request.user.id)
    courses=QuestionModel.Course.objects.filter(organization=student.organization)
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QuestionModel.Course.objects.get(id=pk)
    student = StudentModel.Student.objects.get(user_id=request.user.id)
    results= QuestionModel.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    student = StudentModel.Student.objects.get(user=request.user.id)
    courses=QuestionModel.Course.objects.filter(organization=student.organization)
    return render(request,'student/student_marks.html',{'courses':courses})
  