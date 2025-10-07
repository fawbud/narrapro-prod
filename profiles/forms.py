from django import forms
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm

from pengguna.models import PenggunaBooking, PenggunaProfile
from .models import User, Booking
from narasumber.models import Education, ProfessionalCertification


class UserProfileForm(forms.ModelForm):
    """
    Form for editing basic user profile information.
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Depan'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Belakang'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email'
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
        labels = {
            'first_name': 'Nama Depan',
            'last_name': 'Nama Belakang',
            'email': 'Email',
            'username': 'Username',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Email ini sudah digunakan oleh pengguna lain.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Username ini sudah digunakan oleh pengguna lain.")
        return username


class NarasumberProfileForm(forms.ModelForm):
    """
    Form for editing narasumber-specific profile information.
    """
    
    class Meta:
        from narasumber.models import NarasumberProfile, ExpertiseCategory
        model = NarasumberProfile
        fields = [
            'profile_picture', 'full_name', 'pekerjaan', 'jabatan', 'bio', 'expertise_area',
            'experience_level', 'years_of_experience', 'email',
            'phone_number', 'is_phone_public', 'location',
            'portfolio_link', 'linkedin_url'
        ]
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Lengkap'
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
                'rows': 4,
                'placeholder': 'Ceritakan tentang diri Anda dan pengalaman...'
            }),
            'expertise_area': forms.Select(attrs={
                'class': 'form-select'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'years_of_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Tahun'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email kontak'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor telepon'
            }),
            'is_phone_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'location': forms.Select(attrs={
                'class': 'form-select'
            }),
            'portfolio_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://portfolio-anda.com'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/username'
            }),
        }
        labels = {
            'profile_picture': 'Foto Profil',
            'full_name': 'Nama Lengkap',
            'pekerjaan': 'Pekerjaan',
            'jabatan': 'Jabatan',
            'bio': 'Biografi',
            'expertise_area': 'Area Keahlian',
            'experience_level': 'Level Pengalaman',
            'years_of_experience': 'Tahun Pengalaman',
            'email': 'Email Kontak',
            'phone_number': 'Nomor Telepon',
            'is_phone_public': 'Tampilkan nomor telepon di profil publik',
            'location': 'Lokasi',
            'portfolio_link': 'Link Portfolio',
            'linkedin_url': 'Link LinkedIn',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text for existing profile pictures
        if self.instance and self.instance.pk and self.instance.profile_picture:
            self.fields['profile_picture'].help_text = 'Leave empty to keep current profile picture'


class EventProfileForm(forms.ModelForm):
    """
    Form for editing event organizer-specific profile information.
    """
    
    class Meta:
        from event.models import EventProfile
        model = EventProfile
        fields = [
            'name', 'description', 'event_type', 'location', 'target_audience',
            'email', 'phone_number', 'is_phone_public', 'website', 
            'linkedin_url', 'cover_image', 'start_date', 'end_date'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Event atau Organisasi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Deskripsi event atau organisasi...'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'event_type_select'
            }),
            'location': forms.Select(attrs={
                'class': 'form-select',
                'id': 'location_select'
            }),
            'target_audience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deskripsi target audiens event ini...'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email kontak'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor telepon (opsional)'
            }),
            'is_phone_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://website-anda.com'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/username'
            }),
            'cover_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'name': 'Nama Event/Organisasi',
            'description': 'Deskripsi',
            'event_type': 'Tipe Event',
            'location': 'Lokasi/Platform',
            'target_audience': 'Target Audiens',
            'email': 'Email Kontak',
            'phone_number': 'Nomor Telepon',
            'is_phone_public': 'Tampilkan nomor telepon di profil publik',
            'website': 'Website',
            'linkedin_url': 'Link LinkedIn',
            'cover_image': 'Cover Image',
            'start_date': 'Tanggal Mulai (Opsional)',
            'end_date': 'Tanggal Selesai (Opsional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set initial location choices based on event_type
        if self.instance and self.instance.pk:
            event_type = self.instance.event_type
        elif 'event_type' in self.data:
            event_type = self.data['event_type']
        else:
            event_type = 'offline'  # Default

        # Update location choices based on event type
        from event.models import EventProfile
        self.fields['location'].choices = EventProfile.get_location_choices_for_event_type(event_type)

        # Debug logging
        print(f"DEBUG EventProfileForm: event_type={event_type}, location_choices_count={len(self.fields['location'].choices)}")

        # Cover image is now always optional (model was updated)
        self.fields['cover_image'].required = False

        if self.instance and self.instance.pk and self.instance.cover_image:
            self.fields['cover_image'].help_text = 'Leave empty to keep current image'
            print(f"DEBUG EventProfileForm: Made cover_image optional for existing instance")
        else:
            self.fields['cover_image'].help_text = 'Upload a cover image for your event (recommended)'
            print(f"DEBUG EventProfileForm: cover_image is optional for new instance")

    def clean(self):
        """Custom validation with better error messages"""
        cleaned_data = super().clean()
        event_type = cleaned_data.get('event_type')
        location = cleaned_data.get('location')

        print(f"DEBUG EventProfileForm.clean(): event_type={event_type}, location={location}")

        if event_type and location:
            # Check if location is valid for the event type
            from event.models import EventProfile
            valid_locations = [choice[0] for choice in EventProfile.get_location_choices_for_event_type(event_type)]

            if location not in valid_locations:
                error_msg = f"Location '{location}' is not valid for {event_type} events. Please select a valid option."
                print(f"DEBUG EventProfileForm.clean(): VALIDATION ERROR - {error_msg}")
                self.add_error('location', error_msg)
            else:
                print(f"DEBUG EventProfileForm.clean(): Location validation PASSED")

        return cleaned_data


class PasswordChangeForm(DjangoPasswordChangeForm):
    """
    Custom password change form with styling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
        
        # Update labels to Indonesian
        self.fields['old_password'].label = 'Password Lama'
        self.fields['new_password1'].label = 'Password Baru'
        self.fields['new_password2'].label = 'Konfirmasi Password Baru'
        
        # Update placeholders
        self.fields['old_password'].widget.attrs['placeholder'] = 'Masukkan password lama'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Masukkan password baru'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Konfirmasi password baru'

class EducationForm(forms.ModelForm):
    """
    Form for managing education entries for narasumber profiles.
    """
    class Meta:
        model = Education
        fields = ['degree', 'school_university', 'field_of_study', 'graduation_year']
        widgets = {
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
        labels = {
            'degree': 'Jenjang Pendidikan',
            'school_university': 'Sekolah/Universitas',
            'field_of_study': 'Jurusan/Bidang Studi',
            'graduation_year': 'Tahun Lulus',
        }


class ProfessionalCertificationForm(forms.ModelForm):
    """
    Form for managing professional certification entries for narasumber profiles.
    """
    class Meta:
        model = ProfessionalCertification
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nama Sertifikasi'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Deskripsi sertifikasi, organisasi penerbit, atau detail lainnya'
            }),
        }
        labels = {
            'title': 'Nama Sertifikasi',
            'description': 'Deskripsi',
        }


class PenggunaBookingForm(forms.ModelForm):
    """
    Form untuk membuat booking khusus pengguna biasa (ekstensi Booking).
    """
    class Meta:
        model = PenggunaBooking
        fields = [
            "interview_topic",
            "description",
            "platform",
            "location_detail",
            "contact_email",
            "contact_phone",
            "is_phone_public",
            "website",
            "linkedin_url",
        ]
        widgets = {
            "interview_topic": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Topik wawancara atau tujuan booking"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Deskripsi singkat tentang wawancara"
            }),
            "platform": forms.Select(attrs={
                "class": "form-select"
            }),
            "location_detail": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Detail lokasi (jika offline)"
            }),
            "contact_email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email kontak Anda"
            }),
            "contact_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nomor telepon (opsional)"
            }),
            "is_phone_public": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
            "website": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://website-anda.com (opsional)"
            }),
            "linkedin_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://linkedin.com/in/username (opsional)"
            }),
        }
        labels = {
            "interview_topic": "Topik Wawancara",
            "description": "Deskripsi",
            "platform": "Platform",
            "location_detail": "Detail Lokasi (Offline)",
            "contact_email": "Email Kontak",
            "contact_phone": "Nomor Telepon",
            "is_phone_public": "Tampilkan Nomor Telepon",
            "website": "Website",
            "linkedin_url": "LinkedIn",
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'message']
        widgets = {
            'booking_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': 'required',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tuliskan pesan untuk narasumber...',
                'required': 'required',
            }),
        }
        labels = {
            'booking_date': 'Tanggal & Waktu Booking',
            'message': 'Pesan untuk Narasumber',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make message field required
        self.fields['message'].required = True
        
class PenggunaProfileForm(forms.ModelForm):
    class Meta:
        model = PenggunaProfile
        fields = ['profile_picture', 'bio', 'email', 'phone_number', 'is_phone_public', 'website', 'linkedin_url']
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ceritakan tentang dirimu (opsional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email kontak'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nomor telepon (opsional)'
            }),
            'is_phone_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://website-anda.com (opsional)'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/username (opsional)'
            }),
        }
        labels = {
            'profile_picture': 'Foto Profil',
            'bio': 'Bio / Tentang Diri',
            'email': 'Email Kontak',
            'phone_number': 'Nomor Telepon',
            'is_phone_public': 'Tampilkan nomor telepon di profil publik',
            'website': 'Website',
            'linkedin_url': 'Link LinkedIn',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add help text for existing profile pictures
        if self.instance and self.instance.pk and self.instance.profile_picture:
            self.fields['profile_picture'].help_text = 'Leave empty to keep current profile picture'