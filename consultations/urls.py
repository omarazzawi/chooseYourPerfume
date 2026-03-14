from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('', views.consultation_list, name='consultation_list'),
    path('book/<int:session_id>/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('edit/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
     path('checkout/<int:booking_id>/', views.checkout, name='checkout'),
]