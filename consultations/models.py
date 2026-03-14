# Create your models here.

from django.db import models
from django.conf import settings


class ConsultationSession(models.Model):
    """
    Consultation service offerings.
    Represents different types of consultation sessions available for booking.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text="Duration in minutes")
    price = models.DecimalField(max_digits=6, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - €{self.price} ({self.duration} min)"
    
    class Meta:
        verbose_name = 'Consultation Session'
        verbose_name_plural = 'Consultation Sessions'
        ordering = ['price']


class Booking(models.Model):
    """
    Customer bookings for consultation sessions.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    session = models.ForeignKey(ConsultationSession, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateField()
    booking_time = models.TimeField()
    notes = models.TextField(blank=True, help_text="Special requests or notes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.session.title} on {self.booking_date}"
    
    class Meta:
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        ordering = ['-booking_date', '-booking_time']


class Payment(models.Model):
    """Payment records for bookings."""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    currency = models.CharField(max_length=3, default='eur')
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment for {self.booking} - €{self.amount}"
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'