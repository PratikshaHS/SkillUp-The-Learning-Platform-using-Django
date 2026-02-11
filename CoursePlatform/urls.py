from django.urls import path
from . import views
from .enroll_views import enroll_course

app_name = "courseplatform"

urlpatterns = [
    path("courses/", views.course_list, name="course_list"),
    path("courses/create/", views.course_create, name="course_create"),
    path("courses/<int:pk>/", views.course_detail, name="course_detail"),
    path("courses/<int:pk>/edit/", views.course_update, name="course_update"),
    path("courses/<int:pk>/delete/", views.course_delete, name="course_delete"),
    path("courses/enroll/<int:course_id>/", enroll_course, name="enroll_course"),
    path("test-template-tags/", views.test_template_tags, name="test_template_tags"),
    path("payment/", views.payment_page, name="payment"),
    path("payment/process/", views.process_payment, name="process_payment"),
    path("create-checkout-session/<int:course_id>/", views.create_checkout_session, name="create-checkout-session"),
    path("success/", views.payment_success, name="payment-success"),
    path("cancel/", views.payment_cancel, name="payment-cancel"),
    path("checkout/<int:course_id>/", views.create_checkout_session, name="checkout"),
]
