from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Course, Enrollment

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def enroll_course(request, course_id):
    try:
        course = Course.objects.get(id=course_id, is_published=True)
        
        # Check if user is already enrolled
        if Enrollment.objects.filter(user=request.user, course=course).exists():
            return JsonResponse({
                'success': True,
                'message': 'You are already enrolled in this course',
                'redirect_url': f'/courses/{course.id}/'
            })
        
        # Create enrollment
        enrollment = Enrollment.objects.create(
            user=request.user,
            course=course,
            is_active=True
        )
        
        # Update enrolled students count
        course.students_enrolled += 1
        course.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Successfully enrolled in the course',
            'redirect_url': f'/courses/{course.id}/'
        })
        
    except Course.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Course not found or not available for enrollment'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
