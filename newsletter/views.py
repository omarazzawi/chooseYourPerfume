from django.shortcuts import render, redirect
from django.contrib import messages
from .models import NewsletterSubscriber
from .forms import NewsletterForm


def home(request):
    """
    Render the homepage with hero video and newsletter signup.
    
    Displays perfume consultation information, featured services,
    and newsletter subscription form in the footer.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered home.html template
    """
    return render(request, 'home.html')


def subscribe(request):
    """
    Handle newsletter subscription with reactivation support.
    
    Implements soft-delete pattern:
    - New email: Creates active subscriber
    - Existing active email: Shows "already subscribed" message
    - Existing inactive email: Reactivates subscription
    
    Args:
        request: HTTP request object (POST only)
        
    Returns:
        Redirect to home with appropriate success/info message
    """
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if email exists
        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            # Email exists - reactivate if inactive
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()
                messages.success(request, 'Welcome back! You have been re-subscribed to our newsletter.')
            else:
                messages.info(request, 'You are already subscribed to our newsletter!')
        except NewsletterSubscriber.DoesNotExist:
            # New subscriber
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you for subscribing! You will receive perfume tips and exclusive offers.')

        return redirect('home')

    return redirect('home')


def unsubscribe(request):
    """
    Handle newsletter unsubscription with soft delete.
    
    Sets is_active to False instead of deleting the record,
    allowing for future resubscription with the same email.
    
    Args:
        request: HTTP request object
        
    Returns:
        GET: Rendered unsubscribe.html confirmation page
        POST: Redirect to home with success/error message
    """
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            subscriber = NewsletterSubscriber.objects.get(email=email)
            subscriber.is_active = False
            subscriber.save()
            messages.success(request,
                             'You have been unsubscribed successfully.')
        except NewsletterSubscriber.DoesNotExist:
            messages.error(request, 'Email not found in our subscriber list.')

        return redirect('home')

    return render(request, 'newsletter/unsubscribe.html')