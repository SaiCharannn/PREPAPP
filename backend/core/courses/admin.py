from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Course, CourseAuditLog

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_id', 'course_name', 'course_category', 'course_fee', 'currency_code', 'course_status']
    list_filter = ['course_category', 'course_status', 'currency_code']
    search_fields = ['course_id', 'course_name', 'course_short_name']
    readonly_fields = ['course_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('course_id', 'course_name', 'course_short_name', 'course_category')
        }),
        ('Duration', {
            'fields': ('course_duration', 'duration_unit')
        }),
        ('Financial', {
            'fields': ('course_fee', 'currency_code')
        }),
        ('Status', {
            'fields': ('course_status',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CourseAuditLog)
class CourseAuditLogAdmin(admin.ModelAdmin):
    list_display = ['course_id', 'action', 'user', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['course_id', 'user']
    readonly_fields = ['course_id', 'action', 'user', 'old_value', 'new_value', 'timestamp']