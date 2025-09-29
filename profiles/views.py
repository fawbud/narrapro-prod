from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse
from django.http import Http404
from .models import User
from .forms import UserProfileForm, PasswordChangeForm, NarasumberProfileForm, EventProfileForm, EducationForm
from narasumber.models import ExpertiseCategory, Education
from django.forms import inlineformset_factory
from profiles.models import Booking
from .forms import BookingForm
from django.db.models import Q


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
        education_formset = None
        
        # Create user-type specific forms
        if user.user_type == 'narasumber' and narasumber_profile:
            narasumber_form = NarasumberProfileForm(
                request.POST, 
                request.FILES, 
                instance=narasumber_profile
            )
            # Create education formset
            EducationFormSet = inlineformset_factory(
                NarasumberProfile, 
                Education, 
                form=EducationForm,
                extra=1, 
                can_delete=True
            )
            education_formset = EducationFormSet(
                request.POST,
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
        if education_formset:
            forms_valid = forms_valid and education_formset.is_valid()
        
        if forms_valid:
            user_form.save()
            if narasumber_form:
                narasumber_form.save()
            if event_form:
                event_form.save()
            if education_formset:
                education_formset.save()
            messages.success(request, 'Profil Anda berhasil diperbarui!')
            return redirect('profiles:profile_detail', username=user.username)
    else:
        user_form = UserProfileForm(instance=user)
        narasumber_form = None
        event_form = None
        education_formset = None
        
        if user.user_type == 'narasumber' and narasumber_profile:
            narasumber_form = NarasumberProfileForm(instance=narasumber_profile)
            # Create education formset for GET requests
            EducationFormSet = inlineformset_factory(
                NarasumberProfile, 
                Education, 
                form=EducationForm,
                extra=1, 
                can_delete=True
            )
            education_formset = EducationFormSet(instance=narasumber_profile)
        elif user.user_type == 'event' and event_profile:
            event_form = EventProfileForm(instance=event_profile)
    
    context = {
        'user_form': user_form,
        'narasumber_form': narasumber_form,
        'event_form': event_form,
        'education_formset': education_formset,
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
    from lowongan.models import LowonganApplication
    from django.core.paginator import Paginator

    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.username == profile_user.username

    # Only allow access to own profile or if user is narasumber
    if not is_own_profile:
        raise Http404("You can only view your own applications.")

    if profile_user.user_type != 'narasumber':
        raise Http404("This page is only available for narasumber users.")

    applications_qs = LowonganApplication.objects.filter(
        applicant=profile_user
    ).select_related('lowongan', 'lowongan__created_by').order_by('-applied_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications_qs = applications_qs.filter(status=status_filter)

    # Calculate statistics
    total_applications = LowonganApplication.objects.filter(applicant=profile_user).count()
    pending_applications = LowonganApplication.objects.filter(applicant=profile_user, status='PENDING').count()
    accepted_applications = LowonganApplication.objects.filter(applicant=profile_user, status='ACCEPTED').count()
    rejected_applications = LowonganApplication.objects.filter(applicant=profile_user, status='REJECTED').count()

    # Pagination
    paginator = Paginator(applications_qs, 10)
    page_number = request.GET.get('page')
    applications_page = paginator.get_page(page_number)

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'active_section': 'lamaran',
        'applications_page': applications_page,
        'status_filter': status_filter,
        'status_choices': LowonganApplication.STATUS_CHOICES,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'accepted_applications': accepted_applications,
        'rejected_applications': rejected_applications,
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

    # Import lowongan models
    from lowongan.models import Lowongan, LowonganApplication

    # Get user's lowongan
    user_lowongan = Lowongan.objects.filter(created_by=profile_user)

    # Calculate statistics
    stats = {
        'total_lowongan': user_lowongan.count(),
        'open_lowongan': user_lowongan.filter(status='OPEN').count(),
        'draft_lowongan': user_lowongan.filter(status='DRAFT').count(),
        'total_applications': LowonganApplication.objects.filter(
            lowongan__created_by=profile_user
        ).count(),
    }

    # Get recent lowongan (last 5)
    recent_lowongan = user_lowongan.select_related('expertise_category').order_by('-created_at')[:5]

    # Get recent applications (last 5)
    recent_applications = LowonganApplication.objects.filter(
        lowongan__created_by=profile_user
    ).select_related('applicant', 'lowongan').order_by('-applied_at')[:5]

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'active_section': 'lowongan',
        'stats': stats,
        'recent_lowongan': recent_lowongan,
        'recent_applications': recent_applications,
        'total_lowongan': stats['total_lowongan'],
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

    bookings_qs = []
    if profile_user.user_type == 'event':
        bookings_qs = profile_user.outgoing_bookings.all()
    elif profile_user.user_type == 'narasumber':
        bookings_qs = profile_user.incoming_bookings.all()

    status_options = [
        ('PENDING', 'Menunggu'),
        ('APPROVED', 'Disetujui'),
        ('REJECTED', 'Ditolak'),
        ('CANCELED', 'Dibatalkan'),
    ]
    all_statuses = [s[0] for s in status_options]

    # Filtering
    status_filters = request.GET.getlist('status')
    if not request.GET:
        status_filters = ['PENDING', 'APPROVED']

    if status_filters:
        bookings = bookings_qs.filter(status__in=status_filters)
    else:
        bookings = bookings_qs

    total_bookings = bookings_qs.count()
    pending_bookings = bookings_qs.filter(status='PENDING').count()
    approved_bookings = bookings_qs.filter(status='APPROVED').count()

    filters_data = []
    for status, label in status_options:
        next_filters = status_filters[:]
        if status in next_filters:
            next_filters.remove(status)
        else:
            next_filters.append(status)
        
        query_string = '&'.join([f'status={s}' for s in sorted(next_filters)])
        
        filters_data.append({
            'status': status,
            'label': label,
            'query_string': '?' + query_string if query_string else '',
            'is_active': status in status_filters,
        })

    all_selected = sorted(status_filters) == sorted(all_statuses)
    
    if all_selected:
        semua_reset_qs = ''
    else:
        semua_reset_qs = '?' + '&'.join([f'status={s}' for s in all_statuses])

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'active_section': 'booking',
        'bookings': bookings,
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'approved_bookings': approved_bookings,
        'status_filters': status_filters,
        'filters_data': filters_data,
        'all_selected': all_selected,
        'semua_reset_qs': semua_reset_qs,
    }

    return render(request, 'profiles/profile_booking.html', context)


@login_required
def book_narasumber(request, username):
    """
    View for event organizers to browse and book narasumber.
    """
    if not request.user.is_approved:
        messages.error(request, 'unapproved_user')
        # Redirect back to the previous page, or home if referrer is not available
        return redirect(request.META.get('HTTP_REFERER', reverse('main:home')))
    
    narasumber_list = User.objects.filter(user_type='narasumber', is_approved=True)
    categories = ExpertiseCategory.objects.all()

    # Search query
    query = request.GET.get('q')
    if query:
        narasumber_list = narasumber_list.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(narasumber_profile__expertise_area__name__icontains=query)
        ).distinct()

    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        narasumber_list = narasumber_list.filter(narasumber_profile__expertise_area__id=category_id)

    context = {
        'narasumber_list': narasumber_list,
        'categories': categories,
    }
    return render(request, 'profiles/book_narasumber.html', context)


@login_required
def create_booking(request, username, narasumber_id):
    """
    View for an event organizer to book a narasumber.
    """
    if not request.user.is_approved:
        messages.error(request, 'unapproved_user')
        # Redirect back to the previous page, or home if referrer is not available
        return redirect(request.META.get('HTTP_REFERER', reverse('main:home')))

    narasumber = get_object_or_404(User, id=narasumber_id, user_type='narasumber')
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.event = request.user
            booking.narasumber = narasumber
            booking.save()
            messages.success(request, f"Booking request sent to {narasumber.get_full_name()}.")
            return redirect('profiles:profile_booking', username=request.user.username)
    else:
        form = BookingForm()
        
    context = {
        'form': form,
        'narasumber': narasumber,
    }
    return render(request, 'profiles/create_booking.html', context)


@login_required
def cancel_booking(request, username, booking_id):
    """
    View for an event organizer to cancel a booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if the user is the event organizer for this booking
    if request.user != booking.event:
        raise Http404("You are not authorized to cancel this booking.")
        
    # Check if the booking can be canceled
    if booking.status not in ['PENDING', 'APPROVED']:
        messages.error(request, "This booking cannot be canceled.")
        return redirect('profiles:profile_booking', username=request.user.username)

    if request.method == 'POST':
        booking.status = 'CANCELED'
        booking.save()
        messages.success(request, "The booking has been canceled.")
        return redirect('profiles:profile_booking', username=request.user.username)
    
    return redirect('profiles:profile_booking', username=request.user.username)


@login_required
def update_booking_status(request, username, booking_id, action):
    """
    View for a narasumber to accept or decline a booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if the user is the narasumber for this booking
    if request.user != booking.narasumber:
        raise Http404("You are not authorized to update this booking.")

    # Check if the booking is pending
    if booking.status != 'PENDING':
        messages.error(request, "This booking can no longer be updated.")
        return redirect('profiles:profile_booking', username=request.user.username)

    if request.method == 'POST':
        if action == 'accept':
            booking.status = 'APPROVED'
            messages.success(request, "The booking has been approved.")
        elif action == 'decline':
            booking.status = 'REJECTED'
            messages.success(request, "The booking has been declined.")
        booking.save()
        return redirect('profiles:profile_booking', username=request.user.username)

    return redirect('profiles:profile_booking', username=request.user.username)

@login_required
def booking_detail(request, username, booking_id):
    """
    Booking detail view.
    """
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.username == profile_user.username

    if not is_own_profile:
        raise Http404("You can only view your own bookings.")

    booking = get_object_or_404(Booking, id=booking_id)

    # Authorization check
    if request.user != booking.event and request.user != booking.narasumber:
        raise Http404("You are not authorized to view this booking.")

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'booking': booking,
        'active_section': 'booking',
    }

    return render(request, 'profiles/booking_detail.html', context)


@login_required
def application_detail(request, username, application_id):
    """
    View for narasumber users to see their own application details
    """
    from lowongan.models import LowonganApplication

    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.username == profile_user.username

    # Only allow access to own profile
    if not is_own_profile:
        raise Http404("You can only view your own applications.")

    if profile_user.user_type != 'narasumber':
        raise Http404("This page is only available for narasumber users.")

    application = get_object_or_404(
        LowonganApplication.objects.select_related('applicant', 'lowongan'),
        id=application_id,
        applicant=profile_user
    )

    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'application': application,
        'active_section': 'lamaran',
    }

    return render(request, 'profiles/application_detail.html', context)