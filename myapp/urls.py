# myapp\urls.py
from django.urls import path
from .views import base, dashboard, home, studentRead, studentCreate, studentUpdate, studentDelete

urlpatterns = [
    path('',base, name='base'),
    path('dashboard/',dashboard,name='dashboardName'),
    path('home/',home,name='homeName'),
    

    # CRUD
    path('studentRead/',studentRead ,name='studentRead'),
    path('studentCreate/',studentCreate ,name='studentCreate'),
    path('<int:pk>/studentUpdate/',studentUpdate ,name='studentUpdate'),
    path('<int:pk>/studentDelete/',studentDelete ,name='studentDelete'),
    
    
    
]
