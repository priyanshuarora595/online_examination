from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.urls import path,include
from django.contrib import admin
from exam import views
from django.contrib.auth.views import LogoutView,LoginView
from django.conf import settings
from django.conf.urls.static import static

class LogoutViewCustom(LogoutView):
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        request.COOKIES.clear()
        return super().dispatch(request, *args, **kwargs)
    pass

urlpatterns = [
   
    path('admin/', admin.site.urls),
    path('teacher/',include('teacher.urls')),
    path('student/',include('student.urls')),
    path('organization/',include('organization.urls')),
    


    path('',views.home_view,name=''),
    path('logout', LogoutViewCustom.as_view(template_name='exam/logout.html'),name='logout'),
    path('contactus', views.contactus_view),
    path('afterlogin', views.afterlogin_view,name='afterlogin'),



    path('adminclick', views.adminclick_view),
    path('adminlogin', LoginView.as_view(template_name='exam/adminlogin.html'),name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view,name='admin-dashboard'),
    path('invalid-user', views.invalid_user,name='invalid-user'),


    path('admin-teacher', views.admin_teacher_view,name='admin-teacher'),
    path('admin-view-teacher', views.admin_view_teacher_view,name='admin-view-teacher'),
    path('update-teacher/<int:pk>', views.update_teacher_view,name='update-teacher'),
    path('delete-teacher/<int:pk>', views.delete_teacher_view,name='delete-teacher'),
    path('admin-view-pending-teacher', views.admin_view_pending_teacher_view,name='admin-view-pending-teacher'),
    path('admin-view-teacher-salary', views.admin_view_teacher_salary_view,name='admin-view-teacher-salary'),
    path('approve-teacher/<int:pk>', views.approve_teacher_view,name='approve-teacher'),
    path('reject-teacher/<int:pk>', views.reject_teacher_view,name='reject-teacher'),


    path('admin-organization', views.admin_organization_view,name='admin-organization'),
    path('admin-view-organization', views.admin_view_organization_view,name='admin-view-organization'),
    path('update-organization/<int:pk>', views.update_organization_view,name='update-organization'),
    path('delete-organization/<int:pk>', views.delete_organization_view,name='delete-organization'),
    path('admin-view-pending-organization', views.admin_view_pending_organization_view,name='admin-view-pending-organization'),
    path('admin-view-organization-fees', views.admin_view_organization_fees_view,name='admin-view-organization-fees'),
    path('approve-organization/<int:pk>', views.approve_organization_view,name='approve-organization'),
    path('reject-organization/<int:pk>', views.reject_organization_view,name='reject-organization'),

    path('admin-student', views.admin_student_view,name='admin-student'),
    path('admin-view-student', views.admin_view_student_view,name='admin-view-student'),
    path('admin-view-student-marks', views.admin_view_student_marks_view,name='admin-view-student-marks'),
    path('admin-view-marks/<int:pk>', views.admin_view_marks_view,name='admin-view-marks'),
    path('admin-check-marks/<int:pk>', views.admin_check_marks_view,name='admin-check-marks'),
    path('update-student/<int:pk>', views.update_student_view,name='update-student'),
    path('delete-student/<int:pk>', views.delete_student_view,name='delete-student'),

    path('admin-course', views.admin_course_view,name='admin-course'),
    path('admin-add-course', views.admin_add_course_view,name='admin-add-course'),
    path('admin-view-course', views.admin_view_course_view,name='admin-view-course'),
    path('delete-course/<int:pk>', views.delete_course_view,name='delete-course'),
    path('update-course/<int:pk>', views.update_course_view,name='update-course'),

    path('admin-question', views.admin_question_view,name='admin-question'),
    path('admin-add-question', views.admin_add_question_view,name='admin-add-question'),
    path('admin-view-question', views.admin_view_question_view,name='admin-view-question'),
    path('view-question/<int:pk>', views.view_question_view,name='view-question'),
    path('delete-question/<int:pk>', views.delete_question_view,name='delete-question'),


]

urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)