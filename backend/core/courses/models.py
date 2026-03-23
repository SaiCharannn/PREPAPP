import uuid
from django.db import models
from django.core.validators import MinValueValidator

class Course(models.Model):
    DURATION_UNITS = [
        ('DAY', 'Days'),
        ('WEEK', 'Weeks'),
        ('MONTH', 'Months'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    ]
    
    # Explicitly set the database table name
    class Meta:
        db_table = 'course_master'  # Match your existing table name
        indexes = [
            models.Index(fields=['course_name']),
            models.Index(fields=['course_category']),
            models.Index(fields=['course_status']),
        ]
        ordering = ['-created_at']
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_id = models.CharField(max_length=30, unique=True, db_index=True)
    course_name = models.CharField(max_length=200, db_index=True)
    course_short_name = models.CharField(max_length=50)
    course_category = models.CharField(max_length=100, db_index=True)
    course_duration = models.IntegerField(validators=[MinValueValidator(1)])
    duration_unit = models.CharField(max_length=20, choices=DURATION_UNITS)
    course_fee = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    currency_code = models.CharField(max_length=3)
    course_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"{self.course_id} - {self.course_name}"

class CourseAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('STATUS_CHANGE', 'Status Change'),
    ]
    
    class Meta:
        db_table = 'course_audit_log'  # Set table name
        ordering = ['-timestamp']
    
    course_id = models.CharField(max_length=30)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.CharField(max_length=50)
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course_id} - {self.action} - {self.timestamp}"