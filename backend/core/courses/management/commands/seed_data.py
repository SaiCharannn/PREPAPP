from django.core.management.base import BaseCommand
from courses.models import Course
from courses.services import NumberingService
from numbering.models import NumberingSequence
import traceback

class Command(BaseCommand):
    help = 'Seed sample course data'
    
    def handle(self, *args, **options):
        try:
            # Check existing courses
            existing_count = Course.objects.count()
            if existing_count > 0:
                self.stdout.write(self.style.WARNING(f'Found {existing_count} existing courses'))
                self.stdout.write('Current courses:')
                for course in Course.objects.all():
                    self.stdout.write(f'  - {course.course_id}: {course.course_name}')
                
                response = input('\nDo you want to add more sample data? (y/n): ')
                if response.lower() != 'y':
                    self.stdout.write(self.style.SUCCESS('Skipping seed data'))
                    return
            
            # Sample courses to add
            sample_courses = [
                {
                    'course_name': 'Python Programming',
                    'course_short_name': 'PYTHON',
                    'course_category': 'Programming',
                    'course_duration': 3,
                    'duration_unit': 'MONTH',
                    'course_fee': 15000,
                    'currency_code': 'INR',
                    'course_status': 'ACTIVE',
                },
                {
                    'course_name': 'Data Science',
                    'course_short_name': 'DATA_SCI',
                    'course_category': 'Data Science',
                    'course_duration': 4,
                    'duration_unit': 'MONTH',
                    'course_fee': 500,
                    'currency_code': 'USD',
                    'course_status': 'ACTIVE',
                },
                {
                    'course_name': 'Web Development',
                    'course_short_name': 'WEB_DEV',
                    'course_category': 'Development',
                    'course_duration': 2,
                    'duration_unit': 'MONTH',
                    'course_fee': 12000,
                    'currency_code': 'INR',
                    'course_status': 'ACTIVE',
                },
                {
                    'course_name': 'Machine Learning',
                    'course_short_name': 'ML',
                    'course_category': 'AI/ML',
                    'course_duration': 6,
                    'duration_unit': 'MONTH',
                    'course_fee': 25000,
                    'currency_code': 'INR',
                    'course_status': 'ACTIVE',
                },
                {
                    'course_name': 'React Development',
                    'course_short_name': 'REACT',
                    'course_category': 'Frontend',
                    'course_duration': 2,
                    'duration_unit': 'MONTH',
                    'course_fee': 10000,
                    'currency_code': 'INR',
                    'course_status': 'ACTIVE',
                },
                {
                    'course_name': 'Django Backend',
                    'course_short_name': 'DJANGO',
                    'course_category': 'Backend',
                    'course_duration': 2,
                    'duration_unit': 'MONTH',
                    'course_fee': 12000,
                    'currency_code': 'INR',
                    'course_status': 'ACTIVE',
                },
                {
                    'course_name': 'Full Stack Development',
                    'course_short_name': 'FULLSTACK',
                    'course_category': 'Development',
                    'course_duration': 4,
                    'duration_unit': 'MONTH',
                    'course_fee': 20000,
                    'currency_code': 'INR',
                    'course_status': 'ACTIVE',
                },
                {
                    'course_name': 'Cloud Computing',
                    'course_short_name': 'CLOUD',
                    'course_category': 'Cloud',
                    'course_duration': 3,
                    'duration_unit': 'MONTH',
                    'course_fee': 18000,
                    'currency_code': 'INR',
                    'course_status': 'ACTIVE',
                },
            ]
            
            created_count = 0
            skipped_count = 0
            
            for course_data in sample_courses:
                # Check if course with same name already exists
                if Course.objects.filter(course_name=course_data['course_name']).exists():
                    self.stdout.write(self.style.WARNING(f"⚠ Skipping '{course_data['course_name']}' - already exists"))
                    skipped_count += 1
                    continue
                
                try:
                    # Generate new course ID
                    course_id = NumberingService.generate_course_id()
                    
                    # Create the course
                    course = Course.objects.create(course_id=course_id, **course_data)
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Created: {course_id} - {course.course_name}"))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"✗ Error creating {course_data['course_name']}: {str(e)}"))
            
            # Summary
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS(f'Seed Data Summary:'))
            self.stdout.write(f'  ✓ Created: {created_count} new courses')
            self.stdout.write(f'  ⚠ Skipped: {skipped_count} existing courses')
            self.stdout.write(f'  📊 Total courses now: {Course.objects.count()}')
            
            # Show numbering sequence info
            seq = NumberingSequence.objects.get(module_name='course')
            self.stdout.write(f'\n📝 Next Course ID will be: {seq.prefix}{str(seq.current_number + 1).zfill(seq.padding)}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding data: {str(e)}'))
            traceback.print_exc()