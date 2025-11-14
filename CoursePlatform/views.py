from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.forms import modelform_factory
from .models import Course, CourseVideo, Enrollment
from .forms import CourseForm, CourseVideoFormSet
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


def course_list(request):
    search = request.GET.get("search", "").strip()
    level = request.GET.get("level", "").strip()
    published = request.GET.get("published", "")

    qs = Course.objects.all()
    if search:
        qs = qs.filter(
            Q(title__icontains=search) |
            Q(instructor__icontains=search) |
            Q(category__icontains=search) |
            Q(description__icontains=search)
        )
    if level:
        qs = qs.filter(level=level)
    if published in ("true", "false"):
        qs = qs.filter(is_published=(published == "true"))

    levels = Course._meta.get_field("level").choices

    return render(
        request,
        "CoursePlatform/course_list.html",
        {"courses": qs, "search": search, "level": level, "levels": levels, "published": published},
    )


def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        formset = CourseVideoFormSet(request.POST, prefix='videos')
        
        if form.is_valid() and formset.is_valid():
            course = form.save(commit=False)
            if 'thumbnail' in request.FILES:
                course.thumbnail = request.FILES['thumbnail']
            course.save()
            
            # Save the formset with the course instance
            videos = formset.save(commit=False)
            for video in videos:
                video.course = course
                video.save()
            
            return redirect("courseplatform:course_list")
    else:
        form = CourseForm()
        formset = CourseVideoFormSet(prefix='videos')
    
    return render(request, "CoursePlatform/course_form.html", {
        "form": form, 
        "formset": formset,
        "title": "Add Course"
    })


def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        formset = CourseVideoFormSet(request.POST, prefix='videos', instance=course)
        
        if form.is_valid() and formset.is_valid():
            if 'thumbnail' in request.FILES:
                course.thumbnail = request.FILES['thumbnail']
            form.save()
            
            # Save the formset
            videos = formset.save(commit=False)
            for video in videos:
                video.course = course
                video.save()
                
            # Delete any videos marked for deletion
            for video in formset.deleted_objects:
                video.delete()
                
            return redirect("courseplatform:course_list")
    else:
        form = CourseForm(instance=course)
        formset = CourseVideoFormSet(prefix='videos', instance=course)
        
    return render(
        request,
        "CoursePlatform/course_form.html",
        {
            "form": form, 
            "formset": formset,
            "title": "Edit Course", 
            "course": course
        },
    )


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    # Check if user is enrolled
    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            course=course, 
            student=request.user,
            status='active'
        ).exists()
    
    # Get similar courses
    similar_courses = Course.objects.filter(
        category=course.category,
        is_published=True
    ).exclude(id=course.id)[:4]
    
    # Get enrollment stats
    enrollment_stats = {
        'total': course.enrollments.count(),
        'completed': course.enrollments.filter(status='completed').count(),
        'active': course.enrollments.filter(status='active').count(),
        'dropped': course.enrollments.filter(status='dropped').count(),
    }
    
    return render(
        request,
        "CoursePlatform/course_detail.html",
        {
            "course": course,
            "is_enrolled": is_enrolled,
            "similar_courses": similar_courses,
            "enrollment_stats": enrollment_stats,
        },
    )


def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == "POST":
        course.delete()
        return redirect("courseplatform:course_list")
    return render(
        request,
        "CoursePlatform/course_confirm_delete.html",
        {"course": course},
    )

def test_template_tags(request):
    """
    A view to test custom template tags
    """
    return render(request, 'test_template_tags.html')


import stripe
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Enrollment

@login_required
def enroll_course(request, course_id):
    """
    Enroll the current user in a course using Stripe Checkout for paid courses
    """
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course, status='active').exists():
        messages.info(request, f'You are already enrolled in {course.title}')
        return redirect('courseplatform:course_detail', pk=course_id)
    
    # If course is free, enroll directly
    if course.price == 0:
        try:
            Enrollment.objects.create(
                student=request.user,
                course=course,
                status='active'
            )
            messages.success(request, f'Successfully enrolled in {course.title}!')
            return redirect('courseplatform:course_detail', pk=course_id)
        except Exception as e:
            messages.error(request, 'Error enrolling in the course. Please try again.')
            return redirect('courseplatform:course_detail', pk=course_id)
    
    # For paid courses, create Stripe Checkout session
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        success_url = request.build_absolute_uri(
            f'/courses/{course.id}/?payment=success&session_id={{CHECKOUT_SESSION_ID}}'
        )
        cancel_url = request.build_absolute_uri(f'/courses/{course.id}/')
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': course.title,
                        'description': course.description[:200] if course.description else 'Course Enrollment',
                    },
                    'unit_amount': int(course.price * 100),  # Convert to paise
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=f'course_{course_id}_user_{request.user.id}',
            metadata={
                'course_id': str(course.id),
                'user_id': str(request.user.id)
            }
        )
        
        # Redirect to Stripe Checkout
        return redirect(checkout_session.url)
        
    except Exception as e:
        print(f"Error creating Stripe session: {str(e)}")
        messages.error(request, 'Error processing payment. Please try again.')
        return redirect('courseplatform:course_detail', pk=course_id)


@login_required
def payment_page(request):
    """
    View for the payment page that handles both free and paid courses
    """
    from .models import Course, Enrollment
    
    # Get course ID from URL parameters
    course_id = request.GET.get('course_id')
    if not course_id:
        messages.error(request, 'No course selected for payment')
        return redirect('courseplatform:course_list')
    
    try:
        course = Course.objects.get(id=course_id, is_published=True)
    except (Course.DoesNotExist, ValueError):
        messages.error(request, 'Invalid course selected')
        return redirect('courseplatform:course_list')
    
    # If course is free, enroll directly
    if course.price == 0:
        # Check if already enrolled
        if not Enrollment.objects.filter(student=request.user, course=course, status='active').exists():
            Enrollment.objects.create(
                student=request.user,
                course=course,
                status='active'
            )
            messages.success(request, f'Successfully enrolled in {course.title}!')
        else:
            messages.info(request, f'You are already enrolled in {course.title}')
        return redirect('courseplatform:course_detail', pk=course_id)
    
    # For paid courses, set up Stripe payment
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(course.price * 100),  # Convert to cents
            currency='inr',
            metadata={
                'user_id': request.user.id,
                'course_id': course.id,
                'email': request.user.email
            },
            # In the latest version of the API, specifying the `automatic_payment_methods` parameter is optional
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        # Prepare context
        context = {
            'page_title': 'Complete Your Purchase',
            'course': course,
            'total_amount': course.price,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
            'client_secret': intent.client_secret,
        }
        
        return render(request, 'CoursePlatform/payment.html', context)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error creating payment intent: {str(e)}")
        messages.error(request, 'Unable to process payment at this time. Please try again later.')
        return redirect('courseplatform:course_detail', pk=course_id)
