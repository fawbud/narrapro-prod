from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from lowongan.models import Lowongan
from profiles.forms import PenggunaProfileForm
from .forms import BaseUserRegistrationForm, NarasumberRegistrationForm, EventRegistrationForm, CombinedRegistrationForm
from narasumber.models import ExpertiseCategory,NarasumberProfile
# from lowongan.models import Lowongan
import json


from narrapro.email_service import send_new_user_confirmation


def home(request):
    # Ambil data expertise categories
    expertise_categories = ExpertiseCategory.objects.all()

    # Ambil 6–8 narasumber terbaru, kecuali profil user sendiri jika dia narasumber
    narasumbers_query = NarasumberProfile.objects.select_related("expertise_area").order_by("-created_at")
    if request.user.is_authenticated and request.user.user_type == 'narasumber':
        narasumbers_query = narasumbers_query.exclude(user=request.user)
    narasumbers = narasumbers_query[:8]

    # Ambil 6–8 lowongan terbaru, kecuali yang dibuat user sendiri jika dia event organizer
    lowongans_query = Lowongan.objects.order_by("-created_at")
    if request.user.is_authenticated and request.user.user_type == 'event':
        lowongans_query = lowongans_query.exclude(created_by=request.user)
    lowongans = lowongans_query[:8]

    context = {
        "expertise_categories": expertise_categories,
        "narasumbers": narasumbers,
        "lowongans": lowongans,
    }
    return render(request, "main/home_authenticated.html", context)

def register_view(request):
    """
    Registration view with dynamic form fields based on user type
    """
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        # Create combined form
        combined_form = CombinedRegistrationForm(
            data=request.POST, 
            files=request.FILES
        )
        
        # Additional validation for education entries if narasumber
        education_valid = True
        if user_type == 'narasumber':
            education_valid = combined_form.validate_education_entries()
        
        if combined_form.is_valid(user_type) and education_valid:
            try:
                user, profile = combined_form.save(user_type)
                send_new_user_confirmation([user.email], user.username)
                messages.success(
                    request, 
                    f'Pendaftaran berhasil! Akun Anda menungggu persetujuan admin. Anda akan menerima email ketika di-approve.'
                )
                return redirect('main:login')
            except Exception as e:
                messages.error(request, f'Pendaftaran gagal: {str(e)}')
        else:
            # Get all form errors
            errors = combined_form.get_errors(user_type)
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f'{field}: {error}')
            
            # Add education validation errors
            if not education_valid:
                messages.error(request, 'Silakan berikan setidaknya satu entri pendidikan lengkap dengan gelar dan sekolah/universitas.')

    # For GET requests or form errors, show the registration form
    base_form = BaseUserRegistrationForm()
    narasumber_form = NarasumberRegistrationForm()
    event_form = EventRegistrationForm()
    
    context = {
        'base_form': base_form,
        'narasumber_form': narasumber_form,
        'event_form': event_form,
        'expertise_categories': ExpertiseCategory.objects.all().order_by('name')
    }
    
    return render(request, 'main/register.html', context)


def login_view(request):
    """
    Login view
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Allow login regardless of approval status (for testing)
            login(request, user)
            
            if user.is_approved:
                messages.success(request, f'Selamat datang kembali, {user.first_name or user.username}!')
            else:
                messages.info(
                    request, 
                    f'Selamat datang kembali, {user.first_name or user.username}! Catatan: Akun Anda masih menunggu persetujuan admin.'
                )
            return redirect('main:home')
        else:
            messages.error(request, 'Username atau password tidak valid.')

    return render(request, 'main/login.html')


@login_required
def logout_view(request):
    """
    Logout view
    """
    user_name = request.user.first_name or request.user.username
    logout(request)
    messages.success(request, f'Sampai jumpa, {user_name}! Anda telah di-logout.')
    return redirect('main:home')


@csrf_exempt
@require_http_methods(["GET"])
def get_role_form_fields(request):
    """
    AJAX endpoint to get form fields for specific user role
    """
    user_type = request.GET.get('user_type')
    
    if user_type == 'narasumber':
        form = NarasumberRegistrationForm()
        form_html = render(request, 'main/partials/narasumber_fields.html', {
            'form': form,
            'expertise_categories': ExpertiseCategory.objects.all().order_by('name')
        }).content.decode('utf-8')
    elif user_type == 'event':
        form = EventRegistrationForm()
        form_html = render(request, 'main/partials/event_fields.html', {
            'form': form
        }).content.decode('utf-8')
    elif user_type == 'pengguna':
        form = PenggunaProfileForm()
        form_html = render(request, 'main/partials/pengguna_form_fields.html', {
            'pengguna_form': form
        }).content.decode('utf-8')
    else:
        # No role selected or invalid role
        form_html = '''
        <div class="text-center text-muted py-4">
            <i class="fas fa-arrow-up fa-2x mb-2"></i>
            <p>Please select your role above to continue</p>
        </div>
        '''
    
    return JsonResponse({
        'success': True,
        'html': form_html
    })
