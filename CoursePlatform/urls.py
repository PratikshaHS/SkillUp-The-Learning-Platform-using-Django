from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views
from .stripe_utils import create_payment_intent, stripe_webhook

app_name = "courseplatform"

urlpatterns = [
    path("courses/", views.course_list, name="course_list"),
    path("courses/create/", views.course_create, name="course_create"),
    path("courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("courses/<int:pk>/enroll/", views.enroll_course, name="enroll_course"),
    path("courses/<int:pk>/edit/", views.course_update, name="course_update"),
    path("courses/<int:pk>/delete/", views.course_delete, name="course_delete"),
    path("test-template-tags/", views.test_template_tags, name="test_template_tags"),
    path("payment/", views.payment_page, name="payment"),
    path("create-payment-intent/<int:course_id>/", create_payment_intent, name="create_payment_intent"),
    path("stripe-webhook/", csrf_exempt(stripe_webhook), name="stripe_webhook"),
]
