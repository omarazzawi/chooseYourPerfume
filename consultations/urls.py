from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('', views.consultation_list, name='consultation_list'),
]