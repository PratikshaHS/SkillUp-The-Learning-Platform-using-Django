from django.conf import settings

def stripe_public_key(request):
    """
    Make the Stripe public key available in all templates.
    """
    return {
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    }
