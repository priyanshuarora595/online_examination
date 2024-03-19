from django.urls import path
from organization import views
from django.contrib.auth.views import LoginView

urlpatterns = [
path('organizationclick', views.organizationclick_view),
path('organizationlogin', LoginView.as_view(template_name='organization/organizationlogin.html'),name='organizationlogin'),
path('organizationsignup', views.organization_signup_view,name='organizationsignup'),
# path('organization-dashboard', views.organization_dashboard_view,name='organization-dashboard'),
# path('organization-exam', views.organization_exam_view,name='organization-exam'),
# path('organization-add-exam', views.organization_add_exam_view,name='organization-add-exam'),
# path('organization-view-exam', views.organization_view_exam_view,name='organization-view-exam'),
# path('delete-exam/<int:pk>', views.delete_exam_view,name='delete-exam'),


# path('organization-question', views.organization_question_view,name='organization-question'),
# path('organization-add-question', views.organization_add_question_view,name='organization-add-question'),
# path('organization-view-question', views.organization_view_question_view,name='organization-view-question'),
# path('see-question/<int:pk>', views.see_question_view,name='see-question'),
# path('remove-question/<int:pk>', views.remove_question_view,name='remove-question'),
]