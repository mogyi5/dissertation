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
    path('profile/<int:id>/create-event/', views.event_create, name='event_create' ),
    path('profile/<int:id>/events/<int:event_pk>/update-event/', views.EventUpdateView.as_view(), name='edit_event'),
    path('profile/<int:id>/events/<int:event_pk>/delete-event/', views.EventDeleteView.as_view(), name='delete_event'),
    path('profile/<int:id>/events/', views.events, name='events'),
    path('profile/<int:id>/search-result/', views.PatientSearchResultsView.as_view(), name='patient_search_results'),
    # path('profile/<int:id>/group/<slug:slug>/', views.GroupDetailsView.as_view(), name='group'),
    path('profile/<int:id>/create-task/', views.TaskCreateView.as_view(), name='create_task'),
    path('profile/<int:id>/task-home/', views.task_home, name='task'),
    path('task_complete/', views.task_complete, name='task_complete'),
    path('delete-task/<int:task_pk>', views.TaskDeleteView.as_view(), name='delete_task'),
    path('profile/<int:id>/tasks/<int:task_pk>/update-task/', views.TaskUpdateView.as_view(), name='edit_task'),
    path('profile/<int:id>/medication/', views.MedicationView, name='medication'),
    path('profile/<int:id>/add-medication/', views.MedicationCreateView.as_view(), name='create_medication'),
    path('medication-done/', views.medication_done, name='medication_done'),   
    path('profile/<int:id>/conditions/', views.ConditionsView, name='conditions'),
    path('profile/<int:id>/conditions/<int:condition_pk>/update-condition/', views.ConditionUpdateView.as_view(), name='edit_condition'),
    path('profile/<int:id>/add-condition/', views.ConditionCreateView.as_view(), name='create_condition'),
    path('profile/<int:id>/immunizations/', views.ImmunizationsView, name='immunizations'),
    path('profile/<int:id>/documents/', views.DocumentsView, name='documents'),
    path('profile/<int:id>/add-document/', views.DocumentCreateView.as_view(), name='create_document'),
    path('profile/<int:id>/pdf-view/<int:pdfid>/', views.pdf_view, name='pdf_view'),   
    path('delete-document/<int:document_pk>/', views.DocumentDeleteView.as_view(), name='delete_document'),
    path('profile/<int:id>/weight/', views.weightview, name='weight'),
    path('weight_chart_json/', views.WeightChartJSONView.as_view(), name='weight_chart_json'),
    path('profile/<int:id>/groups/', views.autocompleteGroup, name='groups'),
    # path('profile/<int:id>/groups_search/', views.autocompleteGroup, name='ajax_group_search'),

    # path('weight_chart_json2/', views.WeightChartJSON2View.as_view(), name='weight_chart_json2'),



     # path('profile/<int:id>/advanced-search/', views.AdvancedSearchView.as_view(), name='advanced_search'),
]