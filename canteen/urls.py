from django.urls import path
from . import views

urlpatterns = [
    # This creates the link: http://127.0.0.1:8000/verify/
    path('verify/', views.verify_meal, name='verify_meal'),
    path('dashboard/', views.monitor_dashboard, name='monitor_dashboard'),
    path('get-latest-scan/', views.get_latest_scan, name='get_latest_scan'),
    path('select-session/', views.select_session, name='select_session'),
    path('analytics/', views.analytics_view, name='analytics'),
]