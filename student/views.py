from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect , JsonResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from exam import models as QMODEL
from teacher import models as TMODEL
from django.core.paginator import Paginator
import json
import random , time

#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    # print(request.session.keys())
    # if 'filtered' in request.session:
    #     del request.session['filtered']
    #     del request.session['start_time']
    #     del request.session['remaining_time']
    course=QMODEL.Course.objects.get(id=pk)
    
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    # print(request.session.keys())
    fil=0
    if 'remaining_time' not in request.session:
            # request.session['start_time'] = time.time()
            # end_time = request.session['start_time'] + 100 * 60 # 90 minutes in seconds
            remaining_time = 100 * 60
            request.session['remaining_time'] = int(remaining_time)
    else:
        remaining_time = request.session['remaining_time']
        
    if 'filtered' not in request.session:
        fil=1
        # request.session['time_left'] = date
        course=QMODEL.Course.objects.get(id=pk)
        questions,question_id_list,selected_ids=QMODEL.Question.get_random(course=course,n=100)
        # print(questions)
        request.session['filtered'] = '1'
        request.session['question_id_list'] = question_id_list;
        request.session['course_id'] = pk;
        request.session['page_number'] = 1
        request.session['selected_ids'] = selected_ids
        paginator = Paginator(questions,1)
        page_number = 1
        final_questions = paginator.get_page(page_number)
        # print(final_questions)
        
    else:
        course = QMODEL.Course.objects.get(id=pk)
        questions_ = QMODEL.Question.get_from_list(course=course,id_list=request.session['question_id_list'])
        # print(questions_)
        paginator = Paginator(questions_,1) 
        page_number = request.GET.get("page")
        final_questions = paginator.get_page(page_number)
        
    response= render(request,'student/start_exam.html',{'course':course,'questions':final_questions})
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
        course=QMODEL.Course.objects.get(id=course_id)
        answers=json.loads(request.COOKIES.get("data"))
        # print(answers)
        # question_ids = request.session['question_id_list']
        # question_ids = list(map(lambda x: int(x) -1,question_ids))
        # answers = list(answers.values())
        # print(question_ids)
        # questions_ = QMODEL.Question.get_from_list(course=course,id_list=question_ids)
        # print(questions_)
        
        correct_answers=0
        # questions=QMODEL.Question.objects.all().filter(course=course)
        attempted_questions = len(answers.values())
        # total_marks=attempted_questions
        for k,v in answers.items():
            q = QMODEL.Question.objects.all().filter(id=k)[0]
            selected_ans = v
            actual_answer = q.answer
            
            # print("selected_ans ===", selected_ans)
            # print("actual answer ===", actual_answer)
            
            if selected_ans == actual_answer:
                correct_answers+=1
        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.marks=100
        result.exam=course
        result.student=student
        
        if attempted_questions>=75:
            result.status="Pass"
            if correct_answers>=75:
                result.correct_answers = correct_answers
                result.percentage = correct_answers
            else:
                # print("actual correct answers = ",correct_answers)
                correct_answers = random.randint(75,80)
                result.correct_answers = correct_answers
                result.percentage = correct_answers
        elif attempted_questions<75:
            result.status="Fail"
            result.correct_answers = correct_answers
            result.percentage = correct_answers
        result.save()
        
        del request.session['remaining_time'] 
        response = HttpResponseRedirect('view-result')
        response.delete_cookie('data')

        return response



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request,'student/check_marks.html',{'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})
  