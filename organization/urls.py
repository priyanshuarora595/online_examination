from django.urls import path
from organization import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path("organizationclick", views.organizationclick_view),
    path(
        "organizationlogin",
        LoginView.as_view(template_name="organization/organizationlogin.html"),
        name="organizationlogin",
    ),
    path(
        "organizationsignup", views.organization_signup_view, name="organizationsignup"
    ),
    path(
        "organization-dashboard",
        views.organization_dashboard_view,
        name="organization-dashboard",
    ),


    path('organization-teacher', views.organization_teacher_view,name='organization-teacher'),
    path('organization-view-teacher', views.organization_view_teacher_view,name='organization-view-teacher'),
    path('organization-view-pending-teacher', views.organization_view_pending_teacher_view,name='organization-view-pending-teacher'),
    path('organization-view-teacher-salary', views.organization_view_teacher_salary_view,name='organization-view-teacher-salary'),
    path('update-teacher/<int:pk>', views.update_teacher_view,name='organization-update-teacher'),
    path('delete-teacher/<int:pk>', views.delete_teacher_view,name='organization-delete-teacher'),
    path('approve-teacher/<int:pk>', views.approve_teacher_view,name='organization-approve-teacher'),
    path('reject-teacher/<int:pk>', views.reject_teacher_view,name='organization-reject-teacher'),
    
    
    
    
    path(
        "organization-exam",
        views.organization_exams_view,
        name="organization-exam",
    ),
    path(
        "organization-exams", views.organization_exams_view, name="organization-exams"
    ),

    path(
        "organization-student",
        views.organization_students_view,
        name="organization-student",
    ),
    path(
        "organization-view-student",
        views.organization_view_student_view,
        name="organization-view-student",
    ),

    path('organization-view-student-marks', views.organization_view_student_marks_view,name='organization-view-student-marks'),
    path('organization-view-marks/<int:pk>', views.organization_view_marks_view,name='organization-view-marks'),
    path('organization-check-marks/<int:pk>', views.organization_check_marks_view,name='organization-check-marks'),
    path('update-student/<int:pk>', views.update_student_view,name='update-student'),
    path('delete-student/<int:pk>', views.delete_student_view,name='delete-student'),


    path('organization-exam', views.organization_exam_view,name='organization-exam'),
    path('organization-add-exam', views.organization_add_exam_view,name='organization-add-exam'),
    path('organization-view-exam', views.organization_view_exam_view,name='organization-view-exam'),
    path('delete-exam/<int:pk>', views.delete_exam_view,name='delete-exam'),


    path('organization-question', views.organization_question_view,name='organization-question'),
    path('organization-add-question', views.organization_add_question_view,name='organization-add-question'),
    path('organization-view-question', views.organization_view_question_view,name='organization-view-question'),
    # path('see-question/<int:pk>', views.see_question_view,name='see-question'),
    # path('remove-question/<int:pk>', views.remove_question_view,name='remove-question'),
]