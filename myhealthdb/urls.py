from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about_this'),
    path('home_base/', views.home_base, name='home_base'),
    path('patient_home/<int:id>/', views.patient_home, name='patient_home'),
    path('staff_home/<int:id>/', views.staff_home, name='staff_home'),
    path('patient_details/<int:id>/', views.patient_details, name='patient_details'),
    path('staff_details/<int:id>/', views.staff_details, name='staff_details' ),
    path('create_event/<int:id>/', views.event_create, name='event_create' ),
]