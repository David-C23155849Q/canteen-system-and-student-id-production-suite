from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # API
    path('verify/', views.verify_meal, name='verify_meal'),
    path('get-latest-scan/', views.get_latest_scan, name='get_latest_scan'),

    # Staff
    path('', views.monitor_dashboard, name='monitor_dashboard'),
    path('select-session/', views.select_session, name='select_session'),

    # Admin
    path('students/', views.student_dashboard, name='student_dashboard'),
    path('edit/<str:student_id>/', views.edit_student, name='edit_student'),
    path('print/<str:student_id>/', views.print_view, name='print_view'),

    # Analytics
    path('analytics/', views.analytics_view, name='analytics'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    path('login-redirect/', views.login_success_redirect, name='login_success_redirect'),
]