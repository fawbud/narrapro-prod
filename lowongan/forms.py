from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Lowongan, LowonganApplication
from narasumber.models import ExpertiseCategory


class LowonganForm(forms.ModelForm):
    """
    Form for creating and updating Lowongan
    """

    class Meta:
        model = Lowongan
        fields = [
            'title', 'description', 'job_type', 'expertise_category',
            'experience_level_required', 'location', 'is_remote',
            'event_date', 'event_time', 'duration_hours',
            'budget_amount', 'budget_negotiable', 'application_deadline',
            'max_applicants', 'requirements', 'contact_email', 'contact_phone'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the job requirements and responsibilities'
            }),
            'job_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expertise_category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'experience_level_required': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_remote': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'event_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'event_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '24'
            }),
            'budget_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Amount in IDR'
            }),
            'budget_negotiable': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'application_deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'max_applicants': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional requirements or qualifications'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact email for this opportunity'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact phone number (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Set default contact email to user's email
        if self.user and not self.instance.pk:
            self.fields['contact_email'].initial = self.user.email

    def clean_event_date(self):
        event_date = self.cleaned_data.get('event_date')
        if event_date and event_date < timezone.now().date():
            raise ValidationError('Event date must be in the future.')
        return event_date

    def clean_application_deadline(self):
        application_deadline = self.cleaned_data.get('application_deadline')
        event_date = self.cleaned_data.get('event_date')

        if application_deadline and application_deadline < timezone.now().date():
            raise ValidationError('Application deadline must be in the future.')

        if application_deadline and event_date and application_deadline >= event_date:
            raise ValidationError('Application deadline must be before event date.')

        return application_deadline

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.created_by = self.user
        if commit:
            instance.save()
        return instance


class LowonganStatusForm(forms.ModelForm):
    """
    Simple form for updating Lowongan status
    """

    class Meta:
        model = Lowongan
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }


class LowonganApplicationForm(forms.ModelForm):
    """
    Form for Narasumber users to apply for Lowongan
    """

    class Meta:
        model = LowonganApplication
        fields = ['cover_letter', 'proposed_rate', 'availability_notes']

        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Tell the event organizer why you are interested in this opportunity and what qualifications you bring...'
            }),
            'proposed_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Your proposed rate in IDR (optional)'
            }),
            'availability_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any notes about your availability or scheduling preferences (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.lowongan = kwargs.pop('lowongan', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        if self.user and self.user.user_type != 'narasumber':
            raise ValidationError('Only Narasumber users can apply for lowongan.')

        if self.lowongan and not self.lowongan.is_open_for_applications:
            raise ValidationError('This lowongan is not currently accepting applications.')

        # Check if user already applied
        if self.user and self.lowongan:
            existing_application = LowonganApplication.objects.filter(
                lowongan=self.lowongan,
                applicant=self.user
            ).exists()
            if existing_application:
                raise ValidationError('You have already applied for this lowongan.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.applicant = self.user
        if self.lowongan:
            instance.lowongan = self.lowongan
        if commit:
            instance.save()
        return instance


class LowonganApplicationStatusForm(forms.ModelForm):
    """
    Form for Event users to update application status
    """

    class Meta:
        model = LowonganApplication
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }


class LowonganFilterForm(forms.Form):
    """
    Form for filtering Lowongan listings
    """

    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or description...'
        })
    )

    job_type = forms.ChoiceField(
        choices=[('', 'All Job Types')] + Lowongan.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    expertise_category = forms.ModelChoiceField(
        queryset=ExpertiseCategory.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    experience_level = forms.ChoiceField(
        choices=[('', 'All Levels')] + Lowongan.EXPERIENCE_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    location = forms.ChoiceField(
        choices=[('', 'All Locations')] + Lowongan.PROVINCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    is_remote = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Lowongan.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )