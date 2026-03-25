import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.contrib import messages
from reportlab.pdfgen import canvas
from django.core.files import File

from .models import Student, MealLog, ScanStatus, CanteenSession, CheatAttempt
from .utils import generate_single_id
from django.utils.timezone import localtime
from django.db.models import Count


# Helper Functions


def get_current_meal():
    active_session = CanteenSession.objects.filter(is_active=True).last()
    return active_session.meal_type if active_session else None


def is_admin(user):
    return user.is_superuser or user.is_staff


# Staff Views


@login_required
def select_session(request):
    if request.method == "POST":
        meal = request.POST.get("meal_type")
        CanteenSession.objects.filter(is_active=True).update(is_active=False)
        CanteenSession.objects.create(
            staff_member=request.user,
            meal_type=meal,
            is_active=True
        )
        return redirect('monitor_dashboard')
    return render(request, 'canteen/select_session.html')


@login_required
def monitor_dashboard(request):
    recent_scans = MealLog.objects.select_related('student').order_by('-timestamp')[:5]
    return render(request, 'canteen/dashboard.html', {'recent_scans': recent_scans})


# QR Scanner API


def verify_meal(request):
    qr_data = request.GET.get('qr_code')
    current_meal = get_current_meal()
    
    status_result = 'error'
    message_result = 'Invalid Request'
    student_photo = None

    if not current_meal:
        status_result = 'denied'
        message_result = 'No active session!'
    else:
        try:
            student = Student.objects.get(qr_code_data=qr_data)
            student_photo = student.photo.url if student.photo else None
            today = timezone.now().date()

            already_eaten = MealLog.objects.filter(
                student=student,
                timestamp__date=today,
                meal_type=current_meal
            ).exists()

            if already_eaten:
                status_result = 'denied'
                message_result = f'Already had {current_meal}!'
                
                # LOG THE CHEAT ATTEMPT
                CheatAttempt.objects.create(
                    student=student,
                    meal_type=current_meal,
                    reason="Already Eaten"
                )
            else:
                MealLog.objects.create(student=student, meal_type=current_meal)
                status_result = 'approved'
                message_result = f'Enjoy your {current_meal}, {student.full_name}!'

        except Student.DoesNotExist:
            status_result = 'error'
            message_result = 'Invalid Card!'
            
            # LOG INVALID CARD SCANS
            CheatAttempt.objects.create(
                invalid_qr=qr_data,
                meal_type=current_meal if current_meal else "Unknown",
                reason="Invalid ID Scanned"
            )

    # Sync with Monitor Dashboard
    obj, _ = ScanStatus.objects.get_or_create(id=1)
    obj.status = status_result
    obj.message = message_result
    obj.photo_url = student_photo
    obj.save()

    return JsonResponse({'status': status_result, 'message': message_result})

def get_latest_scan(request):
    obj, _ = ScanStatus.objects.get_or_create(id=1)
    
    # Don't return "waiting" data to the UI to avoid flickering
    if obj.status == 'waiting':
        return JsonResponse({'status': 'waiting'})

    data = {
        'status': obj.status, 
        'message': obj.message,
        'photo_url': obj.photo_url
    }

    # Reset so the dashboard knows we've handled this scan
    obj.status = 'waiting'
    obj.photo_url = None # Clear photo so it doesn't show for the next 'error'
    obj.save()
    return JsonResponse(data)



def get_latest_scan(request):
    obj, _ = ScanStatus.objects.get_or_create(id=1)
    data = {'status': obj.status, 
            'message': obj.message,
            'photo_url': obj.photo_url
            }

    obj.status = 'waiting'
    obj.save()
    return JsonResponse(data)
    
    return JsonResponse({'status': 'waiting'})


# Admin Views


@login_required
@user_passes_test(is_admin)
def student_dashboard(request):
    query = request.GET.get('q', '')

    if query:
        results = Student.objects.filter(
            Q(full_name__icontains=query) | Q(student_id__icontains=query),
            is_active=True
        )
    else:
        results = Student.objects.filter(is_active=True).order_by('-id')[:20]

    return render(request, 'adminstration/dashboard.html', {
        'results': results,
        'query': query,
        'total_count': results.count()
    })



@login_required
@user_passes_test(is_admin)
def edit_student(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)

    if request.method == "POST":
        try:
            student.full_name = request.POST.get('full_name')
            student.student_id = request.POST.get('student_id')
            student.student_intake = request.POST.get('student_intake')

            if 'photo' in request.FILES:
                student.photo = request.FILES['photo']
            
            student.save()

            if 'save_regenerate' in request.POST:
                generate_single_id(student)

                new_id_path = os.path.join(
                    settings.MEDIA_ROOT, 
                    'student_ids_purple_final', 
                    f"{student.student_id}_FRONT.png"
                )
                
                if os.path.exists(new_id_path):
                    with open(new_id_path, 'rb') as f:
                        # This replaces the student's face with the finished card PNG
                        student.photo.save(f"{student.student_id}_ID_CARD.png", File(f), save=True)
                    messages.success(request, f"ID Card generated for {student.student_id}")
                else:
                    messages.error(request, "ID PNG was not created. Check your utils.py pathing.")

            return redirect('student_dashboard')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return redirect('student_dashboard')

    return render(request, 'adminstration/edit_student.html', {'student': student})

@login_required
@user_passes_test(is_admin)
def print_view(request, student_id):
    student = get_object_or_404(Student, student_id=student_id)
    return render(request, 'adminstration/print_view.html', {'student': student})


# Analytics


@login_required
def analytics_view(request):
    date_filter = request.GET.get('date')
    session_filter = request.GET.get('session')

    logs = MealLog.objects.all()
    sessions = CanteenSession.objects.all().order_by('-start_time')

    if date_filter:
        logs = logs.filter(timestamp__date=date_filter)
        sessions = sessions.filter(start_time__date=date_filter)

    if session_filter:
        logs = logs.filter(meal_type=session_filter)
        sessions = sessions.filter(meal_type=session_filter)

    for s in sessions:
        s.total_scans = MealLog.objects.filter(
            meal_type=s.meal_type,
            timestamp__date=s.start_time.date()
        ).count()

    daily_data = logs.annotate(date=TruncDate('timestamp')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')
        
    # NEW: Get the most frequent "cheaters" for the report
    top_cheaters = CheatAttempt.objects.values(
    'student__full_name', 
    'student__student_id', 
    'student__photo', 
    'invalid_qr'  # <--- MUST INCLUDE THIS HERE
    ).annotate(
    attempts=Count('id')
    ).order_by('-attempts')[:10]

    # NEW: Get recent flagged attempts
    recent_cheats = CheatAttempt.objects.select_related('student').order_by('-attempt_time')[:10]

    staff_stats = CanteenSession.objects.values('staff_member__username') \
        .annotate(session_count=Count('id')) \
        .order_by('-session_count')

    context = {
        'labels': json.dumps([d['date'].strftime("%d %b") for d in daily_data]),
        'counts': json.dumps([d['count'] for d in daily_data]),
        # CHANGE 'sessions' to 'session_history' HERE:
        'session_history': sessions, 
        'staff_data': staff_stats,
        'total_today': MealLog.objects.filter(timestamp__date=timezone.now().date()).count(),
        'total_all_time': MealLog.objects.count(),
        'top_cheaters': top_cheaters,
        'recent_cheats': recent_cheats,
        'total_cheats_today': CheatAttempt.objects.filter(attempt_time__date=timezone.now().date()).count(),
        'meal_choices': ['Breakfast', 'Tea', 'Lunch', 'Supper'],
    }

    return render(request, 'canteen/analytics.html', context)


# PDF Export


@login_required
def export_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="canteen_report.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Canteen Report")

    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M')}")

    y = 750
    p.drawString(100, y, "Staff | Meal | Date | Count")
    p.line(100, y-5, 500, y-5)

    sessions = CanteenSession.objects.all().order_by('-start_time')[:25]

    for s in sessions:
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

        count = MealLog.objects.filter(
            meal_type=s.meal_type,
            timestamp__date=s.start_time.date()
        ).count()

        p.drawString(100, y, f"{s.staff_member.username} | {s.meal_type} | {s.start_time.strftime('%d-%m')} | {count}")

    p.showPage()
    p.save()

    return response



# error handling tmplate page
def custom_403(request, exception):
    return render(request, '403.html', status=403)



from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def login_success_redirect(request):
    """
    Redirects users to the correct dashboard based on their permissions.
    """
    if request.user.is_superuser or request.user.is_staff:
        # Admins go to the Student ID Management dashboard
        return redirect('student_dashboard')
    else:
        # Regular Canteen Staff go to the Scanner monitor
        return redirect('select_session')