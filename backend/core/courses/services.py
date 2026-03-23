import requests
from django.conf import settings
from .models import Course, CourseAuditLog
from decimal import Decimal

class NumberingService:
    @staticmethod
    def generate_course_id():
        """Generate next course ID using numbering service"""
        # In production, this would call the numbering service API
        # For now, we'll implement simple logic
        try:
            from numbering.models import NumberingSequence
            sequence, created = NumberingSequence.objects.get_or_create(
                module_name='course',
                defaults={'prefix': 'CRS', 'current_number': 0, 'padding': 5}
            )
            sequence.current_number += 1
            sequence.save()
            return f"{sequence.prefix}{str(sequence.current_number).zfill(sequence.padding)}"
        except:
            # Fallback logic if numbering model doesn't exist
            last_course = Course.objects.all().order_by('-course_id').first()
            if last_course and last_course.course_id:
                try:
                    last_number = int(last_course.course_id[3:])
                    new_number = last_number + 1
                    return f"CRS{str(new_number).zfill(5)}"
                except:
                    return "CRS00001"
            return "CRS00001"

class AuditService:
    @staticmethod
    def log_action(course_id, action, user, old_value=None, new_value=None):
        """Log course actions for audit trail"""
        CourseAuditLog.objects.create(
            course_id=course_id,
            action=action,
            user=user or 'SYSTEM',
            old_value=old_value,
            new_value=new_value
        )

class CurrencyService:
    @staticmethod
    def convert_currency(amount, from_currency, to_currency):
        """Convert currency using exchange rates (simplified)"""
        # In production, integrate with real exchange rate API
        exchange_rates = {
            ('USD', 'INR'): 83.0,
            ('EUR', 'INR'): 90.0,
            ('GBP', 'INR'): 105.0,
            ('INR', 'USD'): 0.012,
            ('EUR', 'USD'): 1.08,
        }
        
        if from_currency == to_currency:
            return amount
        
        rate = exchange_rates.get((from_currency, to_currency))
        if rate:
            return amount * Decimal(str(rate))
        return amount