from django.urls import path
from . import views 


urlpatterns = [
    path('', views.index, name='index'),
    #path('register/', views.register, name='register'),
    # path('<int:question_id>/', views.detail, name='detail'),
    # path('<int:question_id>/results/', views.results, name='results'),
]