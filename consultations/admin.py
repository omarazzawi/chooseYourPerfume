# Register your models here.

from django.contrib import admin
from .models import ConsultationSession, Booking


@admin.register(ConsultationSession)
class ConsultationSessionAdmin(admin.ModelAdmin):
    """Admin configuration for ConsultationSession."""
    list_display = ['title', 'duration', 'price', 'is_available', 'created_at']
    list_filter = ['is_available', 'created_at']
    search_fields = ['title', 'description']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for Booking."""
    list_display = ['user', 'session', 'booking_date', 'booking_time', 'status', 'is_paid', 'created_at']
    list_filter = ['status', 'is_paid', 'booking_date']
    search_fields = ['user__username', 'session__title', 'notes']
    date_hierarchy = 'booking_date'