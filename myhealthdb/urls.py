from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about_this'),
    path('home-base/', views.home_base, name='home_base'),
    path('patient-home/<int:id>/', views.patient_home, name='patient_home'),
    path('staff-home/<int:id>/', views.staff_home, name='staff_home'),
    path('patient-details/<int:id>/', views.patient_details, name='patient_details'),
    path('staff-details/<int:id>/', views.staff_details, name='staff_details' ),
    path('create-event/<int:id>/', views.event_create, name='event_create' ),
    path('profile/<int:id>/events/<int:event-pk>/update-event/', views.EventUpdateView.as_view(), name='edit_event'),
    path('profile/<int:id>/events/<int:event-pk>/delete-event/', views.EventDeleteView.as_view(), name='delete_event'),
    path('profile/<int:id>/events/', views.events, name='events'),
    path('profile/<int:id>/search-result/', views.PatientSearchResultsView.as_view(), name='patient_search_results'),
    path('profile/<int:id>/group/<slug:slug>/', views.GroupDetailsView.as_view(), name='group'),
    # path('profile/<int:id>/advanced-search/', views.AdvancedSearchView.as_view(), name='advanced_search'),
]