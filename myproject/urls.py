from django.contrib import admin
from django.urls import path, include
from userAuth import views as accounts_views

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),
    
    # Apps
    path('', include('myapp.urls')),    # CRUD operations
    path('cp/', include('CoursePlatform.urls')),  # Case-insensitive URL for CoursePlatform
    

    # UserAuth
    path('accounts/', include('django.contrib.auth.urls')), # built in login, change/reset password, logout, 
    
    path('register/', accounts_views.register, name='register'),
    path('accounts/profile/', accounts_views.profile, name='profile'),
    path('accounts/edit_profile/', accounts_views.edit_profile, name='edit_profile'),
]
