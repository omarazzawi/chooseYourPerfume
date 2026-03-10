from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ConsultationSession, Booking
from .forms import BookingForm

def consultation_list(request):
    """Display all available consultation sessions."""
    sessions = ConsultationSession.objects.filter(is_available=True)
    return render(request, 'consultations/consultation_list.html', {'sessions': sessions})

@login_required
def create_booking(request, session_id):
    """Create a new booking for a consultation session."""
    session = get_object_or_404(ConsultationSession, id=session_id, is_available=True)
    
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
    """Display user's bookings."""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date', '-booking_time')
    return render(request, 'consultations/my_bookings.html', {'bookings': bookings})