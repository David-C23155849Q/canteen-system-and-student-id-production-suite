from django.contrib import admin
from django.contrib import admin
from .models import Student, MealLog

admin.site.register(Student)
admin.site.register(MealLog)


# canteen/admin.py
from .models import CheatAttempt

@admin.register(CheatAttempt)
class CheatAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'invalid_qr', 'meal_type', 'attempt_time', 'reason')
    list_filter = ('reason', 'meal_type', 'attempt_time')
    search_fields = ('student__full_name', 'student__student_id', 'invalid_qr')