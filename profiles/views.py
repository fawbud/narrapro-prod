from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse
from django.http import Http404
from anymail.exceptions import AnymailRequestsAPIError

from narrapro.email_service import send_speaker_booking_notification, send_booking_status_update
from pengguna.models import PenggunaBooking, PenggunaProfile
from .models import User
from .forms import PenggunaBookingForm, PenggunaProfileForm, UserProfileForm, PasswordChangeForm, NarasumberProfileForm, EventProfileForm, EducationForm
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
    pengguna_profile = None
    
    if user.user_type == 'narasumber':
        from narasumber.models import NarasumberProfile
        narasumber_profile, created = NarasumberProfile.objects.get_or_create(user=user)
    elif user.user_type == 'event':
        from event.models import EventProfile
        event_profile, created = EventProfile.objects.get_or_create(user=user)
    elif user.user_type == 'pengguna':
        pengguna_profile, _ = PenggunaProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        print(f"=== DEBUG: Form submission for {user.username} ===")
        print(f"POST data: {dict(request.POST)}")
        print(f"FILES data: {dict(request.FILES)}")
        
        user_form = UserProfileForm(request.POST, instance=user)
        narasumber_form = None
        event_form = None
        education_formset = None
        pengguna_form = None
        
        # Create user-type specific forms
        if user.user_type == 'pengguna' and pengguna_profile:
            pengguna_form = PenggunaProfileForm(
                request.POST,
                request.FILES,
                instance=pengguna_profile
            )
        elif user.user_type == 'narasumber' and narasumber_profile:
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
        print(f"DEBUG: User form valid: {forms_valid}")
        if not forms_valid:
            print(f"DEBUG: User form errors: {user_form.errors}")
        
        if pengguna_form:
            pengguna_valid = pengguna_form.is_valid()
            forms_valid = forms_valid and pengguna_valid
            print(f"DEBUG: Pengguna form valid: {pengguna_valid}")
            if not pengguna_valid:
                print(f"DEBUG: Pengguna form errors: {pengguna_form.errors}")
            
        if narasumber_form:
            narasumber_valid = narasumber_form.is_valid()
            forms_valid = forms_valid and narasumber_valid
            print(f"DEBUG: Narasumber form valid: {narasumber_valid}")
            if not narasumber_valid:
                print(f"DEBUG: Narasumber form errors: {narasumber_form.errors}")
                
        if event_form:
            event_valid = event_form.is_valid()
            forms_valid = forms_valid and event_valid
            print(f"DEBUG: Event form valid: {event_valid}")
            if not event_valid:
                print(f"DEBUG: Event form errors: {event_form.errors}")
                
        if education_formset:
            education_valid = education_formset.is_valid()
            forms_valid = forms_valid and education_valid
            print(f"DEBUG: Education formset valid: {education_valid}")
            if not education_valid:
                print(f"DEBUG: Education formset errors: {education_formset.errors}")
        
        print(f"DEBUG: Overall forms valid: {forms_valid}")
        
        if forms_valid:
            print("DEBUG: All forms valid, saving...")

            # Debug storage backend info
            from django.core.files.storage import default_storage
            print(f"DEBUG: Storage backend in use: {default_storage.__class__.__name__}")
            print(f"DEBUG: Storage module: {default_storage.__class__.__module__}")

            user_form.save()
            if narasumber_form:
                saved_narasumber = narasumber_form.save()
                print(f"DEBUG: Narasumber profile saved, image: {saved_narasumber.profile_picture.name if saved_narasumber.profile_picture else 'None'}")
            if event_form:
                saved_event = event_form.save()
                print(f"DEBUG: Event profile saved, image: {saved_event.cover_image.name if saved_event.cover_image else 'None'}")
            if education_formset:
                education_formset.save()
            if pengguna_form:
                pengguna_form.save()
            messages.success(request, 'Profil Anda berhasil diperbarui!')
            return redirect('profiles:profile_detail', username=user.username)
        else:
            print("DEBUG: Form validation failed!")
            # Add form errors to messages for debugging
            all_errors = []
            if user_form.errors:
                all_errors.extend([f"User: {error}" for field, errors in user_form.errors.items() for error in errors])
            if narasumber_form and narasumber_form.errors:
                all_errors.extend([f"Narasumber: {error}" for field, errors in narasumber_form.errors.items() for error in errors])
            if event_form and event_form.errors:
                all_errors.extend([f"Event: {error}" for field, errors in event_form.errors.items() for error in errors])
            if pengguna_form and pengguna_form.errors:
                all_errors.extend([f"Pengguna: {error}" for field, errors in pengguna_form.errors.items() for error in errors])

            
            for error in all_errors[:5]:  # Show first 5 errors
                messages.error(request, error)
    else:
        user_form = UserProfileForm(instance=user)
        narasumber_form = None
        event_form = None
        education_formset = None
        pengguna_form = None
        
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
        elif user.user_type == 'pengguna' and pengguna_profile:
            pengguna_form = PenggunaProfileForm(instance=pengguna_profile)
    
    context = {
        'user_form': user_form,
        'narasumber_form': narasumber_form,
        'event_form': event_form,
        'education_formset': education_formset,
        'profile_user': user,
        'narasumber_profile': narasumber_profile,
        'event_profile': event_profile,
        'pengguna_form': pengguna_form,  
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
    Profile booking view - shows user's bookings:
    - event → outgoing bookings
    - pengguna → pengguna bookings (via PenggunaBooking)
    - narasumber → incoming bookings
    """
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.username == profile_user.username

    if not is_own_profile:
        raise Http404("You can only view your own bookings.")

    # Tentukan queryset sesuai user_type
    if profile_user.user_type == 'event':
        bookings_qs = profile_user.outgoing_bookings.all()
        is_pengguna = False
    elif profile_user.user_type == 'pengguna':
        bookings_qs = PenggunaBooking.objects.filter(pengguna=profile_user).select_related("booking", "booking__narasumber")
        is_pengguna = True
    elif profile_user.user_type == 'narasumber':
        bookings_qs = profile_user.incoming_bookings.all()
        is_pengguna = False
    else:
        bookings_qs = []
        is_pengguna = False

    status_options = [
        ('PENDING', 'Menunggu'),
        ('APPROVED', 'Disetujui'),
        ('REJECTED', 'Ditolak'),
        ('CANCELED', 'Dibatalkan'),
    ]
    all_statuses = [s[0] for s in status_options]

    # Filtering status
    status_filters = request.GET.getlist('status')
    if not request.GET:
        status_filters = ['PENDING', 'APPROVED']

    if status_filters:
        if is_pengguna:
            bookings = bookings_qs.filter(booking__status__in=status_filters)
        else:
            bookings = bookings_qs.filter(status__in=status_filters)
    else:
        bookings = bookings_qs

    # Hitung total
    if is_pengguna:
        total_bookings = bookings_qs.count()
        pending_bookings = bookings_qs.filter(booking__status='PENDING').count()
        approved_bookings = bookings_qs.filter(booking__status='APPROVED').count()
    else:
        total_bookings = bookings_qs.count()
        pending_bookings = bookings_qs.filter(status='PENDING').count()
        approved_bookings = bookings_qs.filter(status='APPROVED').count()

    # Buat filter link
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
        'is_pengguna': is_pengguna,  # supaya di template bisa bedakan
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
    View untuk membuat booking.
    - Event user booking narasumber langsung.
    - Pengguna biasa booking narasumber via extension PenggunaBooking.
    """
    narasumber = get_object_or_404(User, id=narasumber_id, user_type="narasumber")

    booking_form = BookingForm(request.POST or None)

    if request.user.user_type == "event":
        # Event booking narasumber
        if request.method == "POST" and booking_form.is_valid():
            booking = booking_form.save(commit=False)
            booking.event = request.user
            booking.narasumber = narasumber
            booking.save()
            try:
                send_speaker_booking_notification(
                    recipient_list=[narasumber.email],
                    event_name=booking.event.event_profile.name,
                    event_date=booking.booking_date.strftime("%d %B %Y"),
                    event_time=booking.booking_date.strftime("%H:%M"),
                    booker_name=booking.event.get_full_name(),
                    username=narasumber.get_full_name()
                )
            except AnymailRequestsAPIError as e:
                print(f"Error sending email: {e}")
            messages.success(request, f"Booking request sent to {narasumber.get_full_name()}.")
            return redirect("profiles:profile_booking", username=request.user.username)

        return render(request, "profiles/create_booking.html", {
            "booking_form": booking_form,
            "pengguna_form": None,  # biar template konsisten
            "narasumber": narasumber,
        })

    elif request.user.user_type == "pengguna":
        pengguna_form = PenggunaBookingForm(request.POST or None, initial={"contact_email": request.user.email})

        if request.method == "POST" and booking_form.is_valid() and pengguna_form.is_valid():
            # 1. Buat booking utama (tanpa event)
            booking = booking_form.save(commit=False)
            booking.event = None
            booking.narasumber = narasumber
            booking.save()

            # 2. Buat extension pengguna
            pengguna_booking = pengguna_form.save(commit=False)
            pengguna_booking.booking = booking
            pengguna_booking.pengguna = request.user
            pengguna_booking.save()
            try:
                send_speaker_booking_notification(
                    recipient_list=[narasumber.email],
                    event_name=pengguna_booking.interview_topic,
                    event_date=booking.booking_date.strftime("%d %B %Y"),
                    event_time=booking.booking_date.strftime("%H:%M"),
                    booker_name=pengguna_booking.pengguna.get_full_name(),
                    username=narasumber.get_full_name()
                )
            except AnymailRequestsAPIError as e:
                print(f"Error sending email: {e}")

            messages.success(request, f"Booking request sent to {narasumber.get_full_name()}.")
            return redirect("profiles:profile_booking", username=request.user.username)

        return render(request, "profiles/create_booking.html", {
            "booking_form": booking_form,
            "pengguna_form": pengguna_form,
            "narasumber": narasumber,
        })

    else:
        messages.error(request, "Tipe user tidak bisa melakukan booking.")
        return redirect("profiles:profile_detail", username=narasumber.username)

    
@login_required
def cancel_booking(request, username, booking_id):
    """
    View for an event organizer OR pengguna to cancel a booking.
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # --- check authorization ---
    if booking.event:  # booking dari event
        if request.user != booking.event:
            raise Http404("You are not authorized to cancel this booking.")
    else:  # booking dari pengguna
        pengguna_booking = get_object_or_404(PenggunaBooking, booking=booking)
        if request.user != pengguna_booking.pengguna:
            raise Http404("You are not authorized to cancel this booking.")

    # --- only allow cancel if masih pending/approved ---
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
    
        # Send email notification to the booker
        booker_email = booking.event.email if booking.event else booking.pengguna_extension.pengguna.email
        event_name = booking.event.event_profile.name if booking.event else booking.pengguna_extension.interview_topic
        try:
            send_booking_status_update([booker_email], booking.get_status_display(), event_name)
        except AnymailRequestsAPIError as e:
            print(f"Error sending email: {e}")
    
        return redirect('profiles:profile_booking', username=request.user.username)
    return redirect('profiles:profile_booking', username=request.user.username)

@login_required
def booking_detail(request, username, booking_id):
    profile_user = get_object_or_404(User, username=username)
    is_own_profile = request.user.username == profile_user.username

    if not is_own_profile:
        raise Http404("You can only view your own bookings.")

    # =============== PENGGUNA ===============
    if profile_user.user_type == "pengguna":
        pengguna_booking = get_object_or_404(
            PenggunaBooking.objects.select_related("booking", "booking__narasumber"),
            booking__id=booking_id
        )
        booking = pengguna_booking.booking
        context = {
            "profile_user": profile_user,
            "is_own_profile": is_own_profile,
            "booking": booking,
            "pengguna_booking": pengguna_booking,
            "is_pengguna": True,
            "is_event": False,
            "is_narasumber": False,
            "is_pengguna_booking": False,
            "active_section": "booking",
        }

    # =============== EVENT ===============
    elif profile_user.user_type == "event":
        booking = get_object_or_404(Booking, id=booking_id)
        if request.user != booking.event:
            raise Http404("You are not authorized to view this booking.")
        context = {
            "profile_user": profile_user,
            "is_own_profile": is_own_profile,
            "booking": booking,
            "is_pengguna": False,
            "is_event": True,
            "is_narasumber": False,
            "is_pengguna_booking": False,
            "active_section": "booking",
        }

    # =============== NARASUMBER ===============
    elif profile_user.user_type == "narasumber":
        pengguna_booking = PenggunaBooking.objects.filter(
            booking__id=booking_id, booking__narasumber=profile_user
        ).select_related("booking", "booking__narasumber").first()

        if pengguna_booking:
            booking = pengguna_booking.booking
            context = {
                "profile_user": profile_user,
                "is_own_profile": is_own_profile,
                "booking": booking,
                "pengguna_booking": pengguna_booking,
                "is_pengguna": False,
                "is_event": False,
                "is_narasumber": True,
                "is_pengguna_booking": True,
                "active_section": "booking",
            }
        else:
            booking = get_object_or_404(Booking, id=booking_id, narasumber=profile_user)
            context = {
                "profile_user": profile_user,
                "is_own_profile": is_own_profile,
                "booking": booking,
                "is_pengguna": False,
                "is_event": False,
                "is_narasumber": True,
                "is_pengguna_booking": False,
                "active_section": "booking",
            }

    else:
        raise Http404("Invalid user type.")

    return render(request, "profiles/booking_detail.html", context)




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