from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from consultations.models import ConsultationSession
from .models import Review
from .forms import ReviewForm


@login_required
def create_review(request, session_id):
    """
    Create a new review for a completed consultation session.
    
    Prevents duplicate reviews by checking if user has already reviewed
    this session. Enforces unique_together constraint on (user, session).
    
    Args:
        request: HTTP request object
        session_id: ID of the ConsultationSession to review
        
    Returns:
        GET: Rendered create_review.html with empty form
        POST: Redirect to review_list on success, or form with errors
        
    Redirects:
        If user already reviewed this session, redirects to consultation_list
        with error message
    """
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
    """
    Display all reviews written by the logged-in user.
    
    Shows review cards with session name, rating, title, comment,
    and posted date. Provides edit/delete buttons for each review.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered review_list.html with user's reviews ordered by date
    """
    reviews = Review.objects.filter(user=request.user)
    return render(request, 'reviews/review_list.html', {'reviews': reviews})


@login_required
def edit_review(request, review_id):
    """
    Edit an existing review's rating, title, or comment.
    
    Only allows editing of reviews owned by the logged-in user.
    Preserves original session and posted date.
    
    Args:
        request: HTTP request object
        review_id: ID of the Review to edit
        
    Returns:
        GET: Rendered edit_review.html with pre-filled form
        POST: Redirect to review_list on success, or form with errors
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('reviews:review_list')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {
        'form': form,
        'review': review
    })


@login_required
def delete_review(request, review_id):
    """
    Permanently delete a review.
    
    Only allows deletion of reviews owned by the logged-in user.
    Displays confirmation page before deletion.
    
    Args:
        request: HTTP request object
        review_id: ID of the Review to delete
        
    Returns:
        GET: Rendered delete_review.html confirmation page
        POST: Redirect to review_list after deletion
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        session_title = review.session.title
        review.delete()
        messages.success(request, f'Your review for {session_title} has been deleted.')
        return redirect('reviews:review_list')

    return render(request, 'reviews/delete_review.html', {'review': review})