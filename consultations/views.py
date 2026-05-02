from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from datetime import date, datetime
import stripe
import json

from .models import ConsultationSession, Booking, Payment
from .forms import BookingForm
from reviews.models import Review

stripe.api_key = settings.STRIPE_SECRET_KEY


def consultation_list(request):
    """
    Display all available consultation sessions.
    
    Shows consultation cards with title, description, duration, and price
    for all sessions marked as available in the database.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered consultation_list.html template with available sessions
    """
    sessions = ConsultationSession.objects.filter(is_available=True)
    return render(request,
                  'consultations/consultation_list.html',
                  {'sessions': sessions})


@login_required
def create_booking(request, session_id):
    """
    Create a new booking for a consultation session.
    
    Handles GET requests by displaying booking form and POST requests
    by creating a new booking with status 'pending' for the logged-in user.
    
    Args:
        request: HTTP request object
        session_id: ID of the ConsultationSession to book
        
    Returns:
        GET: Rendered create_booking.html with empty form
        POST: Redirect to my_bookings on success, or form with errors
    """
    session = get_object_or_404(ConsultationSession,
                                id=session_id, is_available=True)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.session = session
            booking.status = 'pending'
            booking.save()
            messages.success(request, f'Booking created successfully! Your {session.title} is scheduled for {booking.booking_date} at {booking.booking_time}.')
            return redirect('consultations:my_bookings')
    else:
        form = BookingForm()

    return render(request, 'consultations/create_booking.html', {
        'form': form,
        'session': session
    })


@login_required
def my_bookings(request):
    """
    Display user's bookings separated into upcoming and past consultations.
    
    Automatically updates booking statuses:
    - Past confirmed bookings → completed
    - Today's past-time bookings → completed
    
    Separates bookings into two categories:
    - Upcoming: Future dates + today's future times
    - Past: Past dates + today's past times
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered my_bookings.html with upcoming_bookings, past_bookings,
        and reviewed_sessions list
    """
    today = date.today()
    now = datetime.now().time()

    # Show payment success message
    if request.GET.get('payment') == 'success':
        messages.success(request,
                         'Payment successful! Your booking is confirmed.')

    # Auto-update confirmed bookings that are now in the past to completed
    Booking.objects.filter(
        user=request.user,
        booking_date__lt=today,
        status='confirmed',
        is_paid=True
    ).update(status='completed')

    # Get all bookings for today
    today_bookings = Booking.objects.filter(
        user=request.user,
        booking_date=today
    )

    # Separate today's bookings into upcoming (future time) and past (past time)
    upcoming_today = []
    past_today = []

    for booking in today_bookings:
        if booking.booking_time > now:
            upcoming_today.append(booking.id)
        else:
            past_today.append(booking.id)
            # Auto-complete today's past bookings if paid
            if booking.status == 'confirmed' and booking.is_paid:
                booking.status = 'completed'
                booking.save()

    # Upcoming: future dates + today's future times
    upcoming_bookings = Booking.objects.filter(
        user=request.user
    ).filter(
        Q(booking_date__gt=today) | Q(id__in=upcoming_today)
    ).order_by('booking_date', 'booking_time')

    # Past: past dates + today's past times
    past_bookings = Booking.objects.filter(
        user=request.user
    ).filter(
        Q(booking_date__lt=today) | Q(id__in=past_today)
    ).order_by('-booking_date', '-booking_time')

    # Get list of sessions user has already reviewed
    reviewed_sessions = Review.objects.filter(user=request.user).values_list('session_id', flat=True)

    return render(request, 'consultations/my_bookings.html', {
        'upcoming_bookings': upcoming_bookings,
        'past_bookings': past_bookings,
        'reviewed_sessions': list(reviewed_sessions),
    })


@login_required
def edit_booking(request, booking_id):
    """
    Edit an existing booking's date, time, or notes.
    
    Only allows editing of bookings owned by the logged-in user.
    Preserves booking status and payment information.
    
    Args:
        request: HTTP request object
        booking_id: ID of the Booking to edit
        
    Returns:
        GET: Rendered edit_booking.html with pre-filled form
        POST: Redirect to my_bookings on success, or form with errors
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('consultations:my_bookings')
    else:
        form = BookingForm(instance=booking)

    return render(request, 'consultations/edit_booking.html', {
        'form': form,
        'booking': booking
    })


@login_required
def delete_booking(request, booking_id):
    """
    Cancel and delete a booking.
    
    Only allows deletion of bookings owned by the logged-in user.
    Permanently removes the booking and associated payment records.
    
    Args:
        request: HTTP request object
        booking_id: ID of the Booking to delete
        
    Returns:
        GET: Rendered delete_booking.html confirmation page
        POST: Redirect to my_bookings after deletion
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        session_title = booking.session.title
        booking_date = booking.booking_date
        booking.delete()
        messages.success(request,
                         f'Booking for {session_title} on {booking_date} has been cancelled.')
        return redirect('consultations:my_bookings')

    return render(request,
                  'consultations/delete_booking.html', {'booking': booking})


@login_required
def checkout(request, booking_id):
    """
    Handle Stripe payment processing for a booking.
    
    Displays checkout page with Stripe payment form on GET request.
    Processes payment through Stripe API on POST request and updates
    booking status to 'confirmed' and is_paid to True on success.
    
    Args:
        request: HTTP request object
        booking_id: ID of the Booking to pay for
        
    Returns:
        GET: Rendered checkout.html with Stripe public key
        POST: JSON response with success status and redirect URL
        
    Raises:
        stripe.error.CardError: Card declined or invalid
        stripe.error.StripeError: Stripe API error
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Check if already paid
    if booking.is_paid:
        messages.info(request, 'This booking has already been paid.')
        return redirect('consultations:my_bookings')

    if request.method == 'POST':
        try:
            # Get payment method from request
            data = json.loads(request.body)
            payment_method_id = data.get('payment_method_id')

            print(f"Payment Method ID: {payment_method_id}")  # Debug

            # Create Stripe Payment Intent with payment method
            intent = stripe.PaymentIntent.create(
                amount=int(booking.session.price * 100),  # Convert to cents
                currency='eur',
                payment_method=payment_method_id,
                confirm=True,
                return_url=request.build_absolute_uri
                          ('/consultations/my-bookings/'),
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'
                },
                metadata={
                    'booking_id': booking.id,
                    'user_id': request.user.id,
                }
            )

            print(f"Payment Intent Status: {intent.status}")  # Debug

            # Create Payment record
            payment = Payment.objects.create(
                booking=booking,
                stripe_payment_intent_id=intent.id,
                amount=booking.session.price,
                status='succeeded'
            )

            # Mark booking as paid and confirmed
            booking.is_paid = True
            booking.status = 'confirmed'
            booking.save()

            print(f"Booking saved: {booking.id}")  # Debug

            return JsonResponse({
                'success': True,
                'redirect_url': '/consultations/my-bookings/?payment=success'
            })

        except stripe.error.CardError as e:
            print(f"CARD ERROR: {e.user_message}")  # Debug
            return JsonResponse({
                'success': False,
                'error': e.user_message
            })
        except stripe.error.StripeError as e:
            print(f"STRIPE ERROR: {str(e)}")  # Debug
            return JsonResponse({
                'success': False,
                'error': 'Payment failed. Please try again.'
            })
        except Exception as e:
            print(f"GENERAL ERROR: {str(e)}")  # Debug
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    context = {
        'booking': booking,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'consultations/checkout.html', context)


@login_required
def booking_detail(request, booking_id):
    """
    Display detailed information about a specific booking.
    
    Shows complete booking information including date, time, duration,
    price, session description, status, payment status, and booking reference.
    
    Args:
        request: HTTP request object
        booking_id: ID of the Booking to display
        
    Returns:
        Rendered booking_detail.html with booking details
    """
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    context = {
        'booking': booking,
    }

    return render(request, 'consultations/booking_detail.html', context)