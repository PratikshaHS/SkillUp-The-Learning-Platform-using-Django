import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import Course, Enrollment
from django.contrib.auth.decorators import login_required

# Set your secret key. Remember to switch to your live secret key in production.
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(request, course_id):
    """
    Create a PaymentIntent for a course purchase
    """
    try:
        course = Course.objects.get(id=course_id, is_published=True)
        
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(course.price * 100),  # Convert to cents
            currency='inr',
            metadata={
                'course_id': course.id,
                'user_id': request.user.id if request.user.is_authenticated else None,
            },
            automatic_payment_methods={
                'enabled': True,
            },
        )
        
        return JsonResponse({
            'clientSecret': intent.client_secret,
            'stripe_publishable_key': settings.STRIPE_PUBLIC_KEY,
            'course': {
                'id': course.id,
                'title': course.title,
                'price': str(course.price),
                'currency': 'inr'
            }
        })
        
    except Course.DoesNotExist:
        return JsonResponse({'error': 'Course not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_successful_payment(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_failed_payment(payment_intent)
    
    return JsonResponse({'status': 'success'})

def handle_successful_payment(payment_intent):
    """
    Handle a successful payment
    """
    try:
        metadata = payment_intent.get('metadata', {})
        course_id = metadata.get('course_id')
        user_id = metadata.get('user_id')
        
        if not course_id or not user_id:
            return
            
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)
        
        # Create enrollment
        Enrollment.objects.get_or_create(
            student=user,
            course=course,
            status='active',
            payment_intent_id=payment_intent.id,
            payment_status='succeeded',
            amount=payment_intent.amount / 100  # Convert back to dollars
        )
        
    except (User.DoesNotExist, Course.DoesNotExist) as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing successful payment: {str(e)}")

def handle_failed_payment(payment_intent):
    """
    Handle a failed payment
    """
    try:
        metadata = payment_intent.get('metadata', {})
        course_id = metadata.get('course_id')
        user_id = metadata.get('user_id')
        
        if not course_id or not user_id:
            return
            
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id)
        
        # Update or create enrollment with failed status
        Enrollment.objects.update_or_create(
            student=user,
            course=course,
            payment_intent_id=payment_intent.id,
            defaults={
                'status': 'failed',
                'payment_status': 'failed',
                'amount': payment_intent.amount / 100
            }
        )
        
    except (User.DoesNotExist, Course.DoesNotExist) as e:
        # Log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error processing failed payment: {str(e)}")
