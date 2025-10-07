from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from narasumber.models import ExpertiseCategory, NarasumberProfile, Education
from event.models import EventProfile
from profiles.forms import PenggunaProfileForm

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
            'profile_picture', 'pekerjaan', 'jabatan', 'bio', 'expertise_area', 'experience_level',
            'years_of_experience', 'email', 'phone_number', 'is_phone_public',
            'location', 'portfolio_link', 'linkedin_url'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'pekerjaan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Pekerjaan',
                'maxlength': '40'
            }),
            'jabatan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Jabatan',
                'maxlength': '40'
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
            'name', 'description', 'event_type', 'location', 'target_audience',
            'email', 'phone_number', 'is_phone_public', 'website', 
            'linkedin_url', 'cover_image', 'start_date', 'end_date'
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
            'event_type': forms.Select(attrs={
                'class': 'form-control',
                'id': 'event_type_select'
            }),
            'location': forms.Select(attrs={
                'class': 'form-control', 
                'id': 'location_select'
            }),
            'target_audience': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your target audience...',
                'rows': 3
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set initial location choices based on event_type
        if self.instance and self.instance.pk:
            event_type = self.instance.event_type
        elif 'event_type' in (self.data or {}):
            event_type = self.data['event_type']
        else:
            event_type = 'offline'  # Default

        # Set initial value for event_type if not set
        if not self.instance.pk and not self.data:
            self.fields['event_type'].initial = 'offline'

        # Update location choices based on event type
        self.fields['location'].choices = EventProfile.get_location_choices_for_event_type(event_type)


class CombinedRegistrationForm:
    """
    Utility class to handle both base user and role-specific forms
    """
    
    def __init__(self, data=None, files=None):
        self.data = data  # Store data for education extraction
        self.base_form = BaseUserRegistrationForm(data=data)
        self.narasumber_form = NarasumberRegistrationForm(data=data, files=files) if data else None
        self.event_form = EventRegistrationForm(data=data, files=files) if data else None
        self.pengguna_form = PenggunaProfileForm(data=data, files=files) if data else None
    
    def is_valid(self, user_type):
        """
        Validate forms based on selected user type
        """
        base_valid = self.base_form.is_valid()
        
        if user_type == 'narasumber':
            role_valid = self.narasumber_form.is_valid() if self.narasumber_form else False
        elif user_type == 'event':
            role_valid = self.event_form.is_valid() if self.event_form else False
        elif user_type == 'pengguna':
            role_valid = self.pengguna_form.is_valid() if self.pengguna_form else False
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
            
            # Handle education entries from POST data
            education_data = self._extract_education_data()
            for edu_data in education_data:
                if edu_data.get('degree') and edu_data.get('school_university'):
                    Education.objects.create(
                        narasumber_profile=profile,
                        degree=edu_data['degree'],
                        school_university=edu_data['school_university'],
                        field_of_study=edu_data.get('field_of_study', ''),
                        graduation_year=edu_data.get('graduation_year', None)
                    )
            
            return user, profile
        elif user_type == 'event' and self.event_form:
            profile = self.event_form.save(commit=False)
            profile.user = user
            profile.save()
            return user, profile
        elif user_type == 'pengguna' and self.pengguna_form:
            profile = self.pengguna_form.save(commit=False)
            profile.user = user
            # optionally set default full_name from user fields
            profile.full_name = f"{user.first_name} {user.last_name}".strip()
            profile.save()
            return user, profile
        
        return user, None
    
    def _extract_education_data(self):
        """
        Extract education data from form data
        """
        education_entries = []
        if not hasattr(self, 'data') or not self.data:
            return education_entries

        i = 0
        while f'education-{i}-degree' in self.data:
            entry = {
                'degree': self.data.get(f'education-{i}-degree', ''),
                'school_university': self.data.get(f'education-{i}-school_university', ''),
                'field_of_study': self.data.get(f'education-{i}-field_of_study', ''),
                'graduation_year': self.data.get(f'education-{i}-graduation_year', None)
            }

            # Convert empty string to None for graduation_year
            if entry['graduation_year'] == '':
                entry['graduation_year'] = None
            elif entry['graduation_year']:
                try:
                    entry['graduation_year'] = int(entry['graduation_year'])
                except ValueError:
                    entry['graduation_year'] = None

            education_entries.append(entry)
            i += 1

        return education_entries

    def validate_education_entries(self):
        """
        Validate that at least one complete education entry is provided
        """
        education_entries = self._extract_education_data()

        # Check if at least one entry has both degree and school
        for entry in education_entries:
            if entry.get('degree') and entry.get('school_university'):
                return True

        return len(education_entries) == 0  # Allow no education entries, but not incomplete ones
    
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
        elif user_type == 'pengguna' and self.pengguna_form:
            errors.update(self.pengguna_form.errors)
        
        return errors


# Education FormSet for Narasumber
EducationFormSet = inlineformset_factory(
    NarasumberProfile,
    Education,
    fields=['degree', 'school_university', 'field_of_study', 'graduation_year'],
    extra=1,  # Show one empty form by default
    can_delete=True,
    widgets={
        'degree': forms.Select(attrs={
            'class': 'form-select'
        }),
        'school_university': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nama Sekolah/Universitas'
        }),
        'field_of_study': forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Jurusan/Bidang Studi (opsional)'
        }),
        'graduation_year': forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tahun Lulus (opsional)',
            'min': '1950',
            'max': '2030'
        }),
    }
)
