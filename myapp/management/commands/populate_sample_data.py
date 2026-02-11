from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from myapp.models import Students
from CoursePlatform.models import Course
import random

class Command(BaseCommand):
    help = 'Populate the database with sample students and courses'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Sample student data
        students_data = [
            {'firstname': 'Alex', 'lastname': 'Johnson', 'phone': 5551234567},
            {'firstname': 'Sarah', 'lastname': 'Williams', 'phone': 5552345678},
            {'firstname': 'Michael', 'lastname': 'Brown', 'phone': 5553456789},
            {'firstname': 'Emily', 'lastname': 'Davis', 'phone': 5554567890},
            {'firstname': 'David', 'lastname': 'Miller', 'phone': 5555678901},
            {'firstname': 'Jessica', 'lastname': 'Wilson', 'phone': 5556789012},
            {'firstname': 'Daniel', 'lastname': 'Moore', 'phone': 5557890123},
            {'firstname': 'Ashley', 'lastname': 'Taylor', 'phone': 5558901234},
            {'firstname': 'Christopher', 'lastname': 'Anderson', 'phone': 5559012345},
            {'firstname': 'Amanda', 'lastname': 'Thomas', 'phone': 5550123456},
            {'firstname': 'Matthew', 'lastname': 'Jackson', 'phone': 5551357924},
            {'firstname': 'Jennifer', 'lastname': 'White', 'phone': 5552468135},
            {'firstname': 'Joshua', 'lastname': 'Harris', 'phone': 5553579246},
            {'firstname': 'Michelle', 'lastname': 'Martin', 'phone': 5554680357},
            {'firstname': 'Andrew', 'lastname': 'Thompson', 'phone': 5555791468},
        ]
        
        # Create students
        for student_data in students_data:
            student, created = Students.objects.get_or_create(
                firstname=student_data['firstname'],
                lastname=student_data['lastname'],
                defaults={'phone': student_data['phone']}
            )
            if created:
                self.stdout.write(f'Created student: {student.firstname} {student.lastname}')
        
        # Sample coding courses
        coding_courses = [
            {
                'title': 'Python Programming Fundamentals',
                'description': 'Learn Python from scratch with hands-on projects. Cover variables, functions, loops, and object-oriented programming.',
                'instructor': 'Dr. James Rodriguez',
                'level': 'beginner',
                'category': 'Programming',
                'price': 199.99,
                'is_published': True,
            },
            {
                'title': 'JavaScript & Web Development',
                'description': 'Master JavaScript, DOM manipulation, and modern web development frameworks like React.',
                'instructor': 'Sarah Chen',
                'level': 'intermediate',
                'category': 'Web Development',
                'price': 249.99,
                'is_published': True,
            },
            {
                'title': 'Data Structures & Algorithms',
                'description': 'Essential computer science concepts for coding interviews and efficient programming.',
                'instructor': 'Prof. Michael Kumar',
                'level': 'advanced',
                'category': 'Computer Science',
                'price': 299.99,
                'is_published': True,
            },
            {
                'title': 'Full Stack Django Development',
                'description': 'Build complete web applications using Django framework, from backend to frontend.',
                'instructor': 'Lisa Thompson',
                'level': 'intermediate',
                'category': 'Web Development',
                'price': 279.99,
                'is_published': True,
            },
            {
                'title': 'Machine Learning with Python',
                'description': 'Introduction to ML algorithms, data preprocessing, and model building using scikit-learn.',
                'instructor': 'Dr. Alex Patel',
                'level': 'advanced',
                'category': 'Data Science',
                'price': 349.99,
                'is_published': True,
            },
            {
                'title': 'Mobile App Development with React Native',
                'description': 'Create cross-platform mobile apps for iOS and Android using React Native.',
                'instructor': 'Kevin Zhang',
                'level': 'intermediate',
                'category': 'Mobile Development',
                'price': 259.99,
                'is_published': False,
            },
        ]
        
        # Sample marketing courses
        marketing_courses = [
            {
                'title': 'Digital Marketing Masterclass',
                'description': 'Comprehensive guide to online marketing including SEO, social media, and paid advertising.',
                'instructor': 'Maria Garcia',
                'level': 'beginner',
                'category': 'Digital Marketing',
                'price': 179.99,
                'is_published': True,
            },
            {
                'title': 'Search Engine Optimization (SEO)',
                'description': 'Learn to rank websites higher on Google with proven SEO strategies and techniques.',
                'instructor': 'John Smith',
                'level': 'intermediate',
                'category': 'SEO',
                'price': 199.99,
                'is_published': True,
            },
            {
                'title': 'Social Media Marketing Strategy',
                'description': 'Build engaging social media campaigns across Facebook, Instagram, Twitter, and LinkedIn.',
                'instructor': 'Emma Wilson',
                'level': 'beginner',
                'category': 'Social Media',
                'price': 149.99,
                'is_published': True,
            },
            {
                'title': 'Google Ads & PPC Advertising',
                'description': 'Master paid advertising campaigns and maximize ROI with Google Ads and Facebook Ads.',
                'instructor': 'Robert Johnson',
                'level': 'intermediate',
                'category': 'Paid Advertising',
                'price': 229.99,
                'is_published': True,
            },
            {
                'title': 'Content Marketing & Copywriting',
                'description': 'Create compelling content that converts visitors into customers through effective copywriting.',
                'instructor': 'Rachel Green',
                'level': 'intermediate',
                'category': 'Content Marketing',
                'price': 189.99,
                'is_published': True,
            },
            {
                'title': 'Email Marketing Automation',
                'description': 'Build automated email sequences that nurture leads and increase sales.',
                'instructor': 'David Lee',
                'level': 'beginner',
                'category': 'Email Marketing',
                'price': 159.99,
                'is_published': False,
            },
            {
                'title': 'Brand Strategy & Development',
                'description': 'Learn to build powerful brands that resonate with your target audience.',
                'instructor': 'Sophie Anderson',
                'level': 'advanced',
                'category': 'Branding',
                'price': 269.99,
                'is_published': True,
            },
        ]
        
        # Combine all courses
        all_courses = coding_courses + marketing_courses
        
        # Create courses with random start dates
        for course_data in all_courses:
            # Generate random start date (1-60 days from now)
            start_date = date.today() + timedelta(days=random.randint(1, 60))
            # End date 30-90 days after start date
            end_date = start_date + timedelta(days=random.randint(30, 90))
            
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    'description': course_data['description'],
                    'instructor': course_data['instructor'],
                    'level': course_data['level'],
                    'category': course_data['category'],
                    'price': course_data['price'],
                    'is_published': course_data['is_published'],
                    'start_date': start_date,
                    'end_date': end_date,
                }
            )
            if created:
                self.stdout.write(f'Created course: {course.title}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(students_data)} students and {len(all_courses)} courses!'
            )
        )
