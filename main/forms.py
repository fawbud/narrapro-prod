from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from narasumber.models import ExpertiseCategory, NarasumberProfile
from event.models import EventProfile

User = get_user_model()


class BaseUserRegistrationForm(UserCreationForm):
    """
    Base registration form with common user fields
    """
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        initial='',  # Default to empty (Pilih Role)
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'user_type_select'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'user_type', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add CSS classes to inherited fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })


class NarasumberRegistrationForm(forms.ModelForm):
    """
    Form for additional Narasumber-specific fields
    """
    
    class Meta:
        model = NarasumberProfile
        fields = [
            'profile_picture', 'bio', 'expertise_area', 'experience_level', 
            'years_of_experience', 'email', 'phone_number', 'is_phone_public',
            'location', 'portfolio_link', 'linkedin_url'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself and your expertise...',
                'rows': 4
            }),
            'expertise_area': forms.Select(attrs={
                'class': 'form-control'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Years of Experience',
                'min': 0
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number (optional)'
            }),
            'is_phone_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
            'portfolio_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Portfolio Website (optional)'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'LinkedIn Profile (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure expertise categories are available
        self.fields['expertise_area'].queryset = ExpertiseCategory.objects.all().order_by('name')


class EventRegistrationForm(forms.ModelForm):
    """
    Form for additional Event organizer-specific fields
    """
    
    class Meta:
        model = EventProfile
        fields = [
            'name', 'description', 'location', 'email', 'phone_number', 
            'is_phone_public', 'website', 'linkedin_url', 'cover_image', 'start_date', 'end_date'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event/Organization Name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your event or organization...',
                'rows': 4
            }),
            'location': forms.Select(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact Email'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number (optional)'
            }),
            'is_phone_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Website URL (optional)'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'LinkedIn Profile (optional)'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'Start Date (optional)'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'placeholder': 'End Date (optional)'
            }),
        }


class CombinedRegistrationForm:
    """
    Utility class to handle both base user and role-specific forms
    """
    
    def __init__(self, data=None, files=None):
        self.base_form = BaseUserRegistrationForm(data=data)
        self.narasumber_form = NarasumberRegistrationForm(data=data, files=files) if data else None
        self.event_form = EventRegistrationForm(data=data, files=files) if data else None
    
    def is_valid(self, user_type):
        """
        Validate forms based on selected user type
        """
        base_valid = self.base_form.is_valid()
        
        if user_type == 'narasumber':
            role_valid = self.narasumber_form.is_valid() if self.narasumber_form else False
        elif user_type == 'event':
            role_valid = self.event_form.is_valid() if self.event_form else False
        else:
            role_valid = False
        
        return base_valid and role_valid
    
    def save(self, user_type):
        """
        Save user and create appropriate profile
        """
        # Save the base user
        user = self.base_form.save()
        
        # Create role-specific profile
        if user_type == 'narasumber' and self.narasumber_form:
            profile = self.narasumber_form.save(commit=False)
            profile.user = user
            # Auto-generate full_name from first_name and last_name
            profile.full_name = f"{user.first_name} {user.last_name}".strip()
            profile.save()
            return user, profile
        elif user_type == 'event' and self.event_form:
            profile = self.event_form.save(commit=False)
            profile.user = user
            profile.save()
            return user, profile
        
        return user, None
    
    def get_errors(self, user_type):
        """
        Get all form errors
        """
        errors = {}
        errors.update(self.base_form.errors)
        
        if user_type == 'narasumber' and self.narasumber_form:
            errors.update(self.narasumber_form.errors)
        elif user_type == 'event' and self.event_form:
            errors.update(self.event_form.errors)
        
        return errors
