from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.forms import modelform_factory
from .models import Course, CourseVideo, Enrollment
from .forms import CourseForm, CourseVideoFormSet
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import stripe
from django.conf import settings
from django.shortcuts import redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
import json


stripe.api_key = settings.STRIPE_SECRET_KEY


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


@login_required
def payment_page(request):
    """
    View for the payment page
    """
    from .models import Course, Enrollment
    
    # Get course ID from URL parameters
    course_id = request.GET.get('course_id')
    if not course_id:
        return redirect('courseplatform:course_list')
    
    try:
        course = Course.objects.get(id=course_id, is_published=True)
    except (Course.DoesNotExist, ValueError):
        messages.error(request, 'The requested course is not available.')
        return redirect('courseplatform:course_list')
    
    # Check if user is already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, 'You are already enrolled in this course.')
        return redirect('courseplatform:course_detail', pk=course.id)
    
    # Prepare context
    context = {
        'page_title': 'Complete Your Enrollment',
        'course': course,
        'total_amount': course.discount_price if course.discount_price else course.price,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLISHABLE_KEY if hasattr(settings, 'STRIPE_PUBLISHABLE_KEY') else '',
    }
    
    return render(request, 'CoursePlatform/payment.html', context)

@login_required
def process_payment(request):
    """
    Process payment and enroll user in the course
    """
    from .models import Course, Enrollment
    import stripe
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    try:
        data = json.loads(request.body)
        course_id = data.get('course_id')
        payment_method_id = data.get('payment_method_id')
        
        if not course_id or not payment_method_id:
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        # Get course
        try:
            course = Course.objects.get(id=course_id, is_published=True)
        except Course.DoesNotExist:
            return JsonResponse({'error': 'Course not found'}, status=404)
        
        # Check if already enrolled
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            return JsonResponse({'redirect': reverse('courseplatform:course_detail', args=[course.id])})
        
        # Initialize Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Create payment intent
        amount = int((course.discount_price if course.discount_price else course.price) * 100)  # Convert to cents
        
        try:
            # Create or retrieve customer
            customer = stripe.Customer.create(
                payment_method=payment_method_id,
                email=request.user.email,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                customer=customer.id,
                payment_method=payment_method_id,
                amount=amount,
                currency='inr',
                description=f'Payment for {course.title}',
                confirm=True,
                off_session=True,
            )
            
            # Create enrollment
            Enrollment.objects.create(
                student=request.user,
                course=course,
                payment_status='completed',
                payment_amount=amount / 100,  # Convert back to rupees
                payment_id=payment_intent.id
            )
            
            return JsonResponse({
                'success': True,
                'redirect': reverse('courseplatform:course_detail', args=[course.id])
            })
            
        except stripe.error.CardError as e:
            return JsonResponse({'error': e.user_message or 'Your card was declined.'}, status=400)
        except stripe.error.StripeError as e:
            return JsonResponse({'error': 'Payment processing failed. Please try again.'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

@csrf_exempt
def create_checkout_session(request, course_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        return JsonResponse({'error': 'You are already enrolled in this course'}, status=400)
    
    try:
        # Convert price to cents and ensure it's an integer
        price = int(float(course.discount_price if course.discount_price else course.price) * 100)
        
        # Create a new checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'inr',  # Using INR for Indian Rupees
                        'unit_amount': price,
                        'product_data': {
                            'name': course.title,
                            'description': course.description[:200],  # First 200 chars of description
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            customer_email=request.user.email,
            client_reference_id=course_id,
            metadata={
                'user_id': request.user.id,
                'course_id': course_id
            },
            success_url=request.build_absolute_uri(
                reverse('courseplatform:payment-success') + f'?session_id={{CHECKOUT_SESSION_ID}}&course_id={course_id}'
            ),
            cancel_url=request.build_absolute_uri(
                reverse('courseplatform:course_detail', kwargs={'pk': course_id})
            ),
        )
        
        return JsonResponse({'id': checkout_session.id})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def payment_success(request):
    from django.http import HttpResponse
    
    session_id = request.GET.get('session_id')
    course_id = request.GET.get('course_id')
    
    if not session_id or not course_id:
        messages.error(request, 'Invalid request')
        return redirect('courseplatform:course_list')
    
    try:
        # Verify the session to ensure it's valid
        session = stripe.checkout.Session.retrieve(session_id)
        
        # Get the course
        course = get_object_or_404(Course, id=course_id, is_published=True)
        
        # Check if already enrolled to prevent duplicate enrollments
        if not Enrollment.objects.filter(user=request.user, course=course).exists():
            # Create enrollment record
            Enrollment.objects.create(
                user=request.user,
                course=course,
                payment_status='completed',
                payment_amount=float(session.amount_total) / 100,  # Convert from cents
                payment_id=session.payment_intent,
                payment_date=timezone.now()
            )
        
        # Render success page with course context
        return render(request, 'CoursePlatform/payment_success.html', {
            'course': course
        })
        
    except Exception as e:
        messages.error(request, f'Error processing your enrollment: {str(e)}')
        return redirect('courseplatform:course_detail', pk=course_id)

def payment_cancel(request):
    messages.warning(request, 'Your payment was cancelled. You can complete your enrollment at any time.')
    return redirect('courseplatform:course_list')
