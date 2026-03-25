from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# 1. Stores student informationfrom django.db import models

class Student(models.Model):
    full_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=20, unique=True)
    student_intake = models.CharField(max_length=100)
    # Changed to blank=True so the admin form doesn't require manual input
    qr_code_data = models.CharField(max_length=255, unique=True, blank=True)
    
    photo = models.ImageField(upload_to='student_photos/', default='logo.png')
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Force the QR data to match the Student ID automatically
        self.qr_code_data = self.student_id
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id} - {self.full_name}"
# 2. Tracks every meal scanned
class MealLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    meal_type = models.CharField(max_length=20, default="Lunch")

    def __str__(self):
        return f"{self.student.student_id} - {self.timestamp}"

# 3. Acts as the "Whiteboard" between the Scanner script and Dashboard
class ScanStatus(models.Model):
    status = models.CharField(max_length=50)
    message = models.CharField(max_length=255)
    photo_url = models.CharField(max_length=500, null=True, blank=True) # Add this line
    updated_at = models.DateTimeField(auto_now=True)
# 4. Tracks which Staff member is running which session
class CanteenSession(models.Model):
    MEAL_CHOICES = [
        ('Breakfast', 'Breakfast'),
        ('Tea', 'Tea'),
        ('Lunch', 'Lunch'),
        ('Supper', 'Supper'),
    ]
    
    staff_member = models.ForeignKey(User, on_delete=models.CASCADE) 
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.meal_type} started by {self.staff_member.username}"
    
    
    
  
#students who tried to get cheat meals
class CheatAttempt(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    invalid_qr = models.CharField(max_length=255, null=True, blank=True) # For non-existent IDs
    meal_type = models.CharField(max_length=50)
    attempt_time = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=100) # e.g., "Already Eaten" or "Invalid ID"

    def __str__(self):
        name = self.student.full_name if self.student else f"Unknown ({self.invalid_qr})"
        return f"CHEAT: {name} - {self.reason}"