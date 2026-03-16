from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewsletterSubscriber
from .forms import NewsletterForm

def home(request):
    """Home page."""
    return render(request, 'home.html')

def subscribe(request):
    """Handle newsletter subscription."""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if already subscribed BEFORE form validation
        if NewsletterSubscriber.objects.filter(email=email).exists():
            messages.info(request, 'You are already subscribed to our newsletter!')
        else:
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you for subscribing! You will receive perfume tips and exclusive offers.')
        
        return redirect('home')
    
    return redirect('home')


def unsubscribe(request):
    """Unsubscribe from newsletter."""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.save()
            messages.success(request, 'You have been unsubscribed successfully.')
        except NewsletterSubscriber.DoesNotExist:
            messages.error(request, 'Email not found in our subscriber list.')
        
        return redirect('home')
    
    return render(request, 'newsletter/unsubscribe.html')