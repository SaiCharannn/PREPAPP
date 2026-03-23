from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Course, CourseAuditLog
from .serializers import CourseSerializer, CourseCreateSerializer, CourseAuditLogSerializer
from .services import NumberingService, AuditService
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['course_category', 'course_status', 'currency_code']
    search_fields = ['course_name', 'course_short_name', 'course_id']
    ordering_fields = ['course_name', 'course_fee', 'created_at']
    
    def get_permissions(self):
        """
        Allow anyone to view courses, but require authentication for modifications
        """
        if self.action in ['list', 'retrieve', 'get_categories']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        """List all courses with filters"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            # Handle pagination
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @swagger_auto_schema(
        request_body=CourseCreateSerializer,
        responses={201: CourseSerializer()}
    )
    def create(self, request, *args, **kwargs):
        """Create a new course with auto-generated ID"""
        try:
            print(f"Create request data: {request.data}")  # Debug log
            print(f"User: {request.user}")  # Debug log
            
            serializer = CourseCreateSerializer(data=request.data)
            if not serializer.is_valid():
                print(f"Serializer errors: {serializer.errors}")  # Debug log
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate course ID
            course_id = NumberingService.generate_course_id()
            print(f"Generated course ID: {course_id}")  # Debug log
            
            # Create course
            course = Course.objects.create(
                course_id=course_id,
                created_by=request.user.username if request.user.is_authenticated else 'SYSTEM',
                **serializer.validated_data
            )
            
            # Log audit
            AuditService.log_action(
                course_id=course_id,
                action='CREATE',
                user=request.user.username if request.user.is_authenticated else 'SYSTEM',
                new_value=CourseSerializer(course).data
            )
            
            return Response(
                {
                    'course_id': course_id,
                    'message': 'Course created successfully',
                    'data': CourseSerializer(course).data
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            print(f"Create error: {str(e)}")  # Debug log
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Update course with audit logging"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            
            print(f"Update request data: {request.data}")  # Debug log
            
            # Get old values before update
            old_data = CourseSerializer(instance).data
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if not serializer.is_valid():
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_update(serializer)
            
            # Log audit
            AuditService.log_action(
                course_id=instance.course_id,
                action='UPDATE',
                user=request.user.username,
                old_value=old_data,
                new_value=serializer.data
            )
            
            return Response({
                'message': 'Course updated successfully',
                'data': serializer.data
            })
        except Exception as e:
            print(f"Update error: {str(e)}")  # Debug log
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete a course (soft delete by deactivating)"""
        try:
            instance = self.get_object()
            
            # Instead of hard delete, we'll deactivate
            old_status = instance.course_status
            instance.course_status = 'INACTIVE'
            instance.save()
            
            # Log audit
            AuditService.log_action(
                course_id=instance.course_id,
                action='DELETE',
                user=request.user.username,
                old_value={'course_status': old_status},
                new_value={'course_status': 'INACTIVE'}
            )
            
            return Response({
                'message': 'Course deactivated successfully',
                'course_id': instance.course_id
            })
        except Exception as e:
            print(f"Delete error: {str(e)}")  # Debug log
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        """Change course status"""
        try:
            course = self.get_object()
            new_status = request.data.get('course_status')
            
            if new_status not in ['ACTIVE', 'INACTIVE']:
                return Response(
                    {'error': 'Invalid status. Must be ACTIVE or INACTIVE'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            old_status = course.course_status
            course.course_status = new_status
            course.save()
            
            # Log status change
            AuditService.log_action(
                course_id=course.course_id,
                action='STATUS_CHANGE',
                user=request.user.username,
                old_value={'course_status': old_status},
                new_value={'course_status': new_status}
            )
            
            return Response({
                'message': f'Course status changed to {new_status}',
                'course_id': course.course_id,
                'status': new_status
            })
        except Exception as e:
            print(f"Status change error: {str(e)}")  # Debug log
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='categories')
    def get_categories(self, request):
        """Get distinct course categories"""
        try:
            categories = Course.objects.values_list('course_category', flat=True).distinct()
            return Response(list(categories))
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='audit-log')
    def get_audit_log(self, request, pk=None):
        """Get audit log for a course"""
        try:
            course = self.get_object()
            logs = CourseAuditLog.objects.filter(course_id=course.course_id)
            serializer = CourseAuditLogSerializer(logs, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='export')
    def export_courses(self, request):
        """Export courses as CSV"""
        try:
            import csv
            from django.http import HttpResponse
            
            queryset = self.filter_queryset(self.get_queryset())
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="courses.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Course ID', 'Course Name', 'Short Name', 'Category', 
                            'Duration', 'Duration Unit', 'Fee', 'Currency', 'Status'])
            
            for course in queryset:
                writer.writerow([
                    course.course_id,
                    course.course_name,
                    course.course_short_name,
                    course.course_category,
                    course.course_duration,
                    course.duration_unit,
                    course.course_fee,
                    course.currency_code,
                    course.course_status
                ])
            
            return response
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )