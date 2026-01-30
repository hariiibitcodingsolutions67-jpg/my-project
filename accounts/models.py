# models.py

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with role-based authentication"""
    
    ROLE_CHOICES = (
        ('EMPLOYEE', 'Employee'),
        ('PM', 'Project Manager'),
        ('ADMIN', 'Admin'), 
    )

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='EMPLOYEE')
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    
    # ✅ FIX: CASCADE delete - Jab creator delete ho to ye bhi delete ho
    created_by = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE,  # ← Ye change kiya
        null=True, 
        blank=True, 
        related_name='created_users'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()

    def __str__(self):
        return self.email
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Project(models.Model):
    """Project model - Created by PM"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # ✅ FIX: CASCADE delete
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # ← Already correct
        limit_choices_to={'role': 'PM'}, 
        related_name='projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'projects'
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'


class Todo(models.Model):
    """Todo model - Managed by Employee"""
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    )
    
    # ✅ FIX: CASCADE delete
    employee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # ← Already correct
        limit_choices_to={'role': 'EMPLOYEE'}, 
        related_name='todos'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.employee.email}"
    
    class Meta:
        db_table = 'todos'
        ordering = ['-date', '-created_at']
        verbose_name = 'Todo'
        verbose_name_plural = 'Todos'


class DailyUpdate(models.Model):
    """Daily Update model - Created by Employee with working hours"""
    
    # ✅ FIX: CASCADE delete
    employee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # ← Already correct
        limit_choices_to={'role': 'EMPLOYEE'}, 
        related_name='daily_updates'
    )
    date = models.DateField(default=timezone.now)
    update_text = models.TextField()
    working_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Working hours for the day"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.email} - {self.date}"
    
    class Meta:
        db_table = 'daily_updates'
        ordering = ['-date', '-created_at']
        unique_together = ['employee', 'date']  
        verbose_name = 'Daily Update'
        verbose_name_plural = 'Daily Updates'

class Leave(models.Model):
    """Leave Management System"""
    
    LEAVE_TYPE_CHOICES = (
        ('SICK', 'Sick Leave'),
        ('CASUAL', 'Casual Leave'),
        ('EARNED', 'Earned Leave'),
        ('EMERGENCY', 'Emergency Leave'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )
    
    employee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # ✅ Employee delete → Leave delete
        limit_choices_to={'role': 'EMPLOYEE'}, 
        related_name='leaves'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    
    # ✅ FIX: SET_NULL add karo
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # ← YE ZAROORI HAI!
        null=True, 
        blank=True, 
        related_name='approved_leaves'
    )
    remarks = models.TextField(blank=True, help_text="PM/Admin remarks")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.email} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    @property
    def total_days(self):
        """Calculate total leave days"""
        return (self.end_date - self.start_date).days + 1
    
    class Meta:
        db_table = 'leaves'
        ordering = ['-created_at']
        verbose_name = 'Leave'
        verbose_name_plural = 'Leaves'

class WorkingHoursSummary(models.Model):
    """Working Hours Summary - Auto-updated via signals for PM dashboard"""
    
    # ✅ FIX: CASCADE delete
    employee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # ← Already correct
        related_name='hours_summary'
    )
    pm = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # ← Already correct
        related_name='team_hours'
    )
    total_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.email} - {self.total_hours}hrs (PM: {self.pm.email})"
    
    class Meta:
        db_table = 'working_hours_summary'
        unique_together = ['employee', 'pm']
        verbose_name = 'Working Hours Summary'
        verbose_name_plural = 'Working Hours Summaries'