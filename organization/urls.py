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
    path(
        "organization-profile",
        views.organization_profile_view,
        name="organization-profile",
    ),


    path('organization-teacher', views.organization_teacher_view,name='organization-teacher'),
    path('organization-view-teacher', views.organization_view_teacher_view,name='organization-view-teacher'),
    path('organization-view-pending-teacher', views.organization_view_pending_teacher_view,name='organization-view-pending-teacher'),
    # path('organization-view-teacher-salary', views.organization_view_teacher_salary_view,name='organization-view-teacher-salary'),
    path('organization-update-teacher/<int:pk>', views.update_teacher_view,name='organization-update-teacher'),
    path('organization-delete-teacher/<int:pk>', views.delete_teacher_view,name='organization-delete-teacher'),
    path('organization-approve-teacher/<int:pk>', views.approve_teacher_view,name='organization-approve-teacher'),
    path('organization-reject-teacher/<int:pk>', views.reject_teacher_view,name='organization-reject-teacher'),

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
    path('organization-update-student/<int:pk>', views.update_student_view,name='organization-update-student'),
    path('organization-delete-student/<int:pk>', views.delete_student_view,name='organization-delete-student'),


    # path('organization-course', views.organization_course_view,name='organization-course'),
    path('organization-add-course', views.organization_add_course_view,name='organization-add-course'),
    path('organization-view-course', views.organization_view_course_view,name='organization-view-course'),
    path('organization-update-course/<int:pk>', views.organization_update_course_view,name='organization-update-course'),
    path('organization-delete-course/<int:pk>', views.delete_course_view,name='organization-delete-course'),


    path('organization-question', views.organization_question_view,name='organization-question'),
    path('organization-add-question', views.organization_add_question_view,name='organization-add-question'),
    path('organization-upload-question', views.organization_upload_questions_file,name='organization-upload-question'),
    path('organization-view-question-course', views.organization_view_question_course_view,name='organization-view-question-course'),
    path('organization-view-question/<int:pk>', views.organization_view_question_view,name='organization-view-question'),
    path('organization-update-question/<int:pk>', views.organization_update_question_view,name='organization-update-question'),
    path('organization-delete-question/<int:pk>', views.delete_question_view,name='organization-delete-question'),
]
