from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating/editing a review."""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Summary of your experience'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about your consultation experience...',
                'rows': 5
            }),
        }
        labels = {
            'rating': 'Rating',
            'title': 'Review Title',
            'comment': 'Your Review',
        }