from django.urls import path
from teacher import views
from django.contrib.auth.views import LoginView

urlpatterns = [
path('teacherclick', views.teacherclick_view),
path('teacherlogin', LoginView.as_view(template_name='teacher/teacherlogin.html'),name='teacherlogin'),
path('teachersignup', views.teacher_signup_view,name='teachersignup'),
path('teacher-dashboard', views.teacher_dashboard_view,name='teacher-dashboard'),
path('teacher-course', views.teacher_course_view,name='teacher-course'),
path('teacher-question', views.teacher_question_view,name='teacher-question'),

path('teacher-add-course', views.teacher_add_course_view,name='teacher-add-course'),
path('teacher-view-course', views.teacher_view_course_view,name='teacher-view-course'),
path('teacher-update-course/<int:pk>', views.teacher_update_course_view,name='teacher-update-course'),
path('teacher-delete-course/<int:pk>', views.teacher_delete_course_view,name='teacher-delete-course'),


path('teacher-add-question', views.teacher_add_question_view,name='teacher-add-question'),
path('teacher-view-question-course', views.teacher_view_question_course_view,name='teacher-view-question-course'),
path('teacher-view-question/<int:pk>', views.teacher_view_question_view,name='teacher-view-question'),
# path('see-question/<int:pk>', views.see_question_view,name='see-question'),
path('teacher-update-question/<int:pk>', views.teacher_update_question_view,name='teacher-update-question'),
path('teacher-remove-question/<int:pk>', views.teacher_remove_question_view,name='teacher-remove-question'),
]