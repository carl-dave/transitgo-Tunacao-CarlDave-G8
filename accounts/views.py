from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistrationForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('dashboard_redirect')
        messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login')

@login_required
def dashboard_redirect(request):
    try:
        role = request.user.profile.role
        if role == 'operator':
            return redirect('operator_dashboard')
        else:
            return redirect('commuter_dashboard')
    except AttributeError:
        return redirect('commuter_dashboard')

@login_required
def commuter_dashboard(request):
    if hasattr(request.user, 'profile') and request.user.profile.role != 'commuter':
        messages.error(request, "Access denied. You cannot view another role's dashboard.")
        return redirect('dashboard_redirect')
    return render(request, 'accounts/commuter_dashboard.html')

@login_required
def operator_dashboard(request):
    if hasattr(request.user, 'profile') and request.user.profile.role != 'operator':
        messages.error(request, "Access denied. You cannot view another role's dashboard.")
        return redirect('dashboard_redirect')
    return render(request, 'accounts/operator_dashboard.html')

@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()

        profile.contact_number = request.POST.get('contact_number', profile.contact_number)
        if 'profile_photo' in request.FILES:
            profile.profile_photo = request.FILES['profile_photo']
        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'accounts/profile.html', {'profile': profile})
