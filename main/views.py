from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .forms import BaseUserRegistrationForm, NarasumberRegistrationForm, EventRegistrationForm, CombinedRegistrationForm
from narasumber.models import ExpertiseCategory
import json


def home(request):
    """
    Home page that shows different content based on authentication status
    """
    if request.user.is_authenticated:
        # Logged in home page
        return render(request, 'main/home_authenticated.html', {
            'user': request.user
        })
    else:
        # Guest home page
        return render(request, 'main/home_guest.html')


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
        
        if combined_form.is_valid(user_type):
            try:
                user, profile = combined_form.save(user_type)
                messages.success(
                    request, 
                    f'Registration successful! Your account is pending admin approval. You will receive an email once approved.'
                )
                return redirect('main:login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            # Get all form errors
            errors = combined_form.get_errors(user_type)
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f'{field}: {error}')
    
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
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            else:
                messages.info(
                    request, 
                    f'Welcome back, {user.first_name or user.username}! Note: Your account is still pending admin approval.'
                )
            return redirect('main:home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'main/login.html')


@login_required
def logout_view(request):
    """
    Logout view
    """
    user_name = request.user.first_name or request.user.username
    logout(request)
    messages.success(request, f'Goodbye, {user_name}! You have been logged out.')
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
