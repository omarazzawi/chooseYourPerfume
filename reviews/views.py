from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from consultations.models import ConsultationSession
from .models import Review
from .forms import ReviewForm


@login_required
def create_review(request, session_id):
    """Create a new review for a consultation session."""
    session = get_object_or_404(ConsultationSession, id=session_id)
    
    # Check if user already reviewed this session
    if Review.objects.filter(user=request.user, session=session).exists():
        messages.error(request, 'You have already reviewed this consultation.')
        return redirect('consultations:consultation_list')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.session = session
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('reviews:review_list')
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/create_review.html', {
        'form': form,
        'session': session
    })


@login_required
def review_list(request):
    """Display all reviews by the user."""
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'reviews/review_list.html', {'reviews': reviews})