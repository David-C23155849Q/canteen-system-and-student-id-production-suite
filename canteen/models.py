from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# 1. Stores student information
class Student(models.Model):
    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    qr_code_data = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name

# 2. Tracks every meal scanned
class MealLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    meal_type = models.CharField(max_length=20, default="Lunch")

    def __str__(self):
        return f"{self.student.student_id} - {self.timestamp}"

# 3. Acts as the "Whiteboard" between the Scanner script and Dashboard
class ScanStatus(models.Model):
    status = models.CharField(max_length=20, default="waiting")
    message = models.CharField(max_length=255, default="No scan detected")
    updated_at = models.DateTimeField(auto_now=True)

# 4. Tracks which Staff member is running which session
class CanteenSession(models.Model):
    MEAL_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Tea', 'Tea'),
        ('Lunch', 'Lunch'),
        ('Supper', 'Supper'),
    ]
    
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE) # Fixed the typo here
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.meal_type} started by {self.staff_member.username}"