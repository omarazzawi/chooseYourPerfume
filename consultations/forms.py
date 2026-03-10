from django import forms
from .models import Booking
from datetime import date


class BookingForm(forms.ModelForm):
    """Form for creating a booking."""
    
    class Meta:
        model = Booking
        fields = ['booking_date', 'booking_time', 'notes']
        widgets = {
            'booking_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'booking_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any special requests or notes? (Optional)',
                'rows': 4
            }),
        }
        labels = {
            'booking_date': 'Consultation Date',
            'booking_time': 'Preferred Time',
            'notes': 'Additional Notes',
        }
    
    def clean_booking_date(self):
        booking_date = self.cleaned_data['booking_date']
        if booking_date < date.today():
            raise forms.ValidationError('Booking date cannot be in the past.')
        return booking_date