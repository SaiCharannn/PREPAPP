from rest_framework import serializers
from .models import Course, CourseAuditLog

class CourseSerializer(serializers.ModelSerializer):
    formatted_fee = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_id', 'course_name', 'course_short_name',
            'course_category', 'course_duration', 'duration_unit',
            'course_fee', 'currency_code', 'course_status',
            'created_at', 'updated_at', 'formatted_fee'
        ]
        read_only_fields = ['id', 'course_id', 'created_at', 'updated_at']
    
    def get_formatted_fee(self, obj):
        return f"{obj.currency_code} {obj.course_fee}"
    
    def validate_course_name(self, value):
        if Course.objects.filter(course_name=value).exists():
            raise serializers.ValidationError("Course name already exists")
        return value
    
    def validate_course_fee(self, value):
        if value < 0:
            raise serializers.ValidationError("Course fee cannot be negative")
        return value
    
    def validate_course_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than 0")
        return value

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'course_name', 'course_short_name', 'course_category',
            'course_duration', 'duration_unit', 'course_fee',
            'currency_code', 'course_status'
        ]
    
    def validate(self, data):
        # Custom validation for currency code
        valid_currencies = ['INR', 'USD', 'EUR', 'GBP']
        if data.get('currency_code') not in valid_currencies:
            raise serializers.ValidationError({
                'currency_code': f"Currency must be one of {valid_currencies}"
            })
        return data

class CourseAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseAuditLog
        fields = '__all__'