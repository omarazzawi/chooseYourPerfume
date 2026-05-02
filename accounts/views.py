from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, LoginForm, UserProfileForm


def register(request):
    """
    Handle user registration with automatic login on success.
    
    Creates a new user account with hashed password and automatically
    logs in the newly registered user. Redirects to homepage on success.
    
    Args:
        request: HTTP request object
        
    Returns:
        GET: Rendered register.html with empty registration form
        POST: Redirect to home on success, or form with validation errors
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def user_login(request):
    """
    Authenticate and log in existing users.
    
    Validates credentials using Django's authentication backend.
    Displays error message for invalid username/password combinations.
    
    Args:
        request: HTTP request object
        
    Returns:
        GET: Rendered login.html with empty login form
        POST: Redirect to home on success, or form with error message
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    """
    Log out the current user and end their session.
    
    Clears the user's session data and redirects to homepage
    with confirmation message.
    
    Args:
        request: HTTP request object
        
    Returns:
        Redirect to home with logout success message
    """
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile(request):
    """
    Display and update user profile information.
    
    Allows logged-in users to view and edit their profile details
    including first name, last name, email, phone, address, city,
    postal code, and country.
    
    Args:
        request: HTTP request object
        
    Returns:
        GET: Rendered profile.html with pre-filled profile form
        POST: Redirect to profile on success, or form with errors
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})