import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models.functions import TruncDate

# Import all your models
from .models import Student, MealLog, ScanStatus, CanteenSession

def get_current_meal():
    """Look for the session the staff member manually started"""
    active_session = CanteenSession.objects.filter(is_active=True).last()
    if active_session:
        return active_session.meal_type
    return None 

@login_required
def select_session(request):
    """View to ask staff which meal is starting"""
    if request.method == "POST":
        meal = request.POST.get("meal_type")
        # Deactivate previous sessions
        CanteenSession.objects.filter(is_active=True).update(is_active=False)
        # Create new session linked to current user
        CanteenSession.objects.create(
            staff_member=request.user,
            meal_type=meal,
            is_active=True
        )
        return redirect('monitor_dashboard')
    return render(request, 'canteen/select_session.html')

def verify_meal(request):
    """Called by the external Python QR script"""
    qr_data = request.GET.get('qr_code')
    current_meal = get_current_meal()
    
    status_result = 'error'
    message_result = 'Invalid Request'

    if not current_meal:
        status_result = 'denied'
        message_result = 'No active session! Staff must start a session.'
    else:
        try:
            student = Student.objects.get(qr_code_data=qr_data)
            today = timezone.now().date()
            
            already_eaten = MealLog.objects.filter(
                student=student, 
                timestamp__date=today, 
                meal_type=current_meal
            ).exists()
            
            if already_eaten:
                status_result = 'denied'
                message_result = f'Already had {current_meal} today!'
            else:
                MealLog.objects.create(student=student, meal_type=current_meal)
                status_result = 'approved'
                message_result = f'Enjoy your {current_meal}, {student.full_name}!'
                
        except Student.DoesNotExist:
            status_result = 'error'
            message_result = 'Invalid Card!'

    # Update the "Whiteboard" bridge for the Dashboard
    obj, created = ScanStatus.objects.get_or_create(id=1)
    obj.status = status_result
    obj.message = message_result
    obj.save()
    
    return JsonResponse({'status': status_result, 'message': message_result})

def get_latest_scan(request):
    """Dashboard calls this every second via AJAX"""
    obj, created = ScanStatus.objects.get_or_create(id=1)
    data = {
        'status': obj.status,
        'message': obj.message,
    }
    
    if obj.status != 'waiting':
        obj.status = 'waiting'
        obj.save()
        
    return JsonResponse(data)

@login_required 
def monitor_dashboard(request):
    """The main visual monitor for the canteen"""
    recent_scans = MealLog.objects.select_related('student').order_by('-timestamp')[:5]
    return render(request, 'canteen/dashboard.html', {'recent_scans': recent_scans})

@login_required
def analytics_view(request):
    """Staff analytics page with charts and counters"""
    # 1. Get total scans grouped by date for the Chart
    daily_data = MealLog.objects.annotate(date=TruncDate('timestamp')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')

    labels = [item['date'].strftime("%d %b") for item in daily_data]
    counts = [item['count'] for item in daily_data]

    # 2. Staff performance table
    staff_data = CanteenSession.objects.values('staff_member__username') \
        .annotate(session_count=Count('id')) \
        .order_by('-session_count')
    
    # 3. Quick Stats (Hero Numbers)
    total_meals_today = MealLog.objects.filter(timestamp__date=timezone.now().date()).count()
    total_all_time = MealLog.objects.count()

    context = {
        'labels': json.dumps(labels),
        'counts': json.dumps(counts),
        'staff_data': staff_data,
        'total_today': total_meals_today,
        'total_all_time': total_all_time,
    }
    return render(request, 'canteen/analytics.html', context)