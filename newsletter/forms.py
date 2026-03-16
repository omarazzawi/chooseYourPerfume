from django import forms
from .models import NewsletterSubscriber


class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form."""
    
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
            })
        }
        labels = {
            'email': '',
        }