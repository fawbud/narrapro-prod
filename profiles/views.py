from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse
from django.http import Http404
from .models import User
from .forms import UserProfileForm, PasswordChangeForm, NarasumberProfileForm, EventProfileForm


def myprofile_redirect(request):
    """
    Redirect view for /myprofile URL.
    - If user is logged in: redirect to /profiles/[username]
    - If user is guest: redirect to home page
    """
    if request.user.is_authenticated:
        return redirect('profiles:profile_detail', username=request.user.username)
    else:
        return redirect('main:home')


def profile_detail(request, username):
    """
    Profile detail view for /profiles/[username] URL.
    Shows main profile information with navigation to sub-pages.
    Allows anonymous access for public narasumber profiles.
    """
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user.username == profile_user.username
    
    # For accessing own profile, require login
    if is_own_profile and not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if trying to access own profile without auth
    
    # Get user-specific profile data
    narasumber_profile = None
    event_profile = None
    
    if profile_user.user_type == 'narasumber':
        try:
            narasumber_profile = profile_user.narasumber_profile
        except:
            narasumber_profile = None
    elif profile_user.user_type == 'event':
        try:
            event_profile = profile_user.event_profile
        except:
            event_profile = None
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'active_section': 'profile',
        'narasumber_profile': narasumber_profile,
        'event_profile': event_profile,
    }
    
    # Use custom template for public narasumber profiles
    if not is_own_profile and profile_user.user_type == 'narasumber' and narasumber_profile:
        return render(request, 'profiles/narasumber_public_profile.html', context)
    
    # Use custom template for public event profiles
    if not is_own_profile and profile_user.user_type == 'event' and event_profile:
        return render(request, 'profiles/event_public_profile.html', context)
    
    # For own profile or other user types, require login
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'profiles/profile_detail.html', context)


@login_required
def edit_profile(request, username):
    """
    Edit profile view - only accessible by the profile owner.
    Handles both basic user info and user-type specific profiles.
    """
    if request.user.username != username:
        raise Http404("You can only edit your own profile.")
    
    user = get_object_or_404(User, username=username)
    
    # Get or create user-specific profile
    narasumber_profile = None
    event_profile = None
    
    if user.user_type == 'narasumber':
        from narasumber.models import NarasumberProfile
        narasumber_profile, created = NarasumberProfile.objects.get_or_create(user=user)
    elif user.user_type == 'event':
        from event.models import EventProfile
        event_profile, created = EventProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=user)
        narasumber_form = None
        event_form = None
        
        # Create user-type specific forms
        if user.user_type == 'narasumber' and narasumber_profile:
            narasumber_form = NarasumberProfileForm(
                request.POST, 
                request.FILES, 
                instance=narasumber_profile
            )
        elif user.user_type == 'event' and event_profile:
            event_form = EventProfileForm(
                request.POST, 
                request.FILES, 
                instance=event_profile
            )
        
        # Validate all forms
        forms_valid = user_form.is_valid()
        if narasumber_form:
            forms_valid = forms_valid and narasumber_form.is_valid()
        if event_form:
            forms_valid = forms_valid and event_form.is_valid()
        
        if forms_valid:
            user_form.save()
            if narasumber_form:
                narasumber_form.save()
            if event_form:
                event_form.save()
            messages.success(request, 'Profil Anda berhasil diperbarui!')
            return redirect('profiles:profile_detail', username=user.username)
    else:
        user_form = UserProfileForm(instance=user)
        narasumber_form = None
        event_form = None
        
        if user.user_type == 'narasumber' and narasumber_profile:
            narasumber_form = NarasumberProfileForm(instance=narasumber_profile)
        elif user.user_type == 'event' and event_profile:
            event_form = EventProfileForm(instance=event_profile)
    
    context = {
        'user_form': user_form,
        'narasumber_form': narasumber_form,
        'event_form': event_form,
        'profile_user': user,
        'narasumber_profile': narasumber_profile,
        'event_profile': event_profile,
    }
    
    return render(request, 'profiles/edit_profile.html', context)


@login_required
def change_password(request, username):
    """
    Change password view - only accessible by the profile owner.
    """
    if request.user.username != username:
        raise Http404("You can only change your own password.")
    
    user = get_object_or_404(User, username=username)
    
    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Password Anda berhasil diubah!')
            return redirect('profiles:profile_detail', username=user.username)
    else:
        form = PasswordChangeForm(user)
    
    context = {
        'form': form,
        'profile_user': user,
    }
    
    return render(request, 'profiles/change_password.html', context)


@login_required
def profile_lamaran(request, username):
    """
    Profile lamaran view - shows user's applications (for narasumber users).
    """
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.username == profile_user.username
    
    # Only allow access to own profile or if user is narasumber
    if not is_own_profile:
        raise Http404("You can only view your own applications.")
    
    if profile_user.user_type != 'narasumber':
        raise Http404("This page is only available for narasumber users.")
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'active_section': 'lamaran',
    }
    
    return render(request, 'profiles/profile_lamaran.html', context)


@login_required
def profile_lowongan(request, username):
    """
    Profile lowongan view - shows user's job postings (for event users).
    """
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.username == profile_user.username
    
    # Only allow access to own profile or if user is event
    if not is_own_profile:
        raise Http404("You can only view your own job postings.")
    
    if profile_user.user_type != 'event':
        raise Http404("This page is only available for event users.")
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'active_section': 'lowongan',
    }
    
    return render(request, 'profiles/profile_lowongan.html', context)


@login_required
def profile_booking(request, username):
    """
    Profile booking view - shows user's bookings (incoming for narasumber, outgoing for event).
    """
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.username == profile_user.username
    
    # Only allow access to own profile
    if not is_own_profile:
        raise Http404("You can only view your own bookings.")
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'active_section': 'booking',
    }
    
    return render(request, 'profiles/profile_booking.html', context)
