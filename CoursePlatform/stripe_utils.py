import stripe
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def initialize_stripe():
    """Initialize Stripe with API key from settings."""
    if not hasattr(settings, 'STRIPE_SECRET_KEY') or not settings.STRIPE_SECRET_KEY:
        raise ImproperlyConfigured("STRIPE_SECRET_KEY is not set in Django settings")
    
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe

def create_checkout_session(course, user, request):
    """Create a Stripe checkout session."""
    try:
        stripe = initialize_stripe()
        
        return stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {
                        'name': course.title,
                    },
                    'unit_amount': int(course.price * 100),  # Convert to paise
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(
                f'/course/payment/success/{course.pk}/'
            ),
            cancel_url=request.build_absolute_uri(
                f'/course/payment/cancelled/{course.pk}/'
            ),
            client_reference_id=str(user.id),
            customer_email=user.email,
        )
    except stripe.error.StripeError as e:
        print(f"Stripe Error: {str(e)}")
        raise
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        raise