from django.db import models
from django.core.validators import URLValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import os

User = get_user_model()


def event_cover_upload_path(instance, filename):
    """
    Generate a unique upload path for event cover images.
    Format: event_covers/user_id/uuid_filename
    """
    # Get file extension
    ext = filename.split('.')[-1].lower()
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Create path with user ID for organization
    return f"event_covers/{instance.user.id}/{unique_filename}"


class EventProfile(models.Model):
    """
    Profile model for event organizers containing detailed information
    about their events, contact details, and scheduling.
    """
    
    # Event type choices
    EVENT_TYPE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('hybrid', 'Hybrid'),
    ]
    
    # Indonesian provinces choices (for offline/hybrid events)
    PROVINCE_CHOICES = [
        ('aceh', 'Aceh'),
        ('sumatera_utara', 'Sumatera Utara'),
        ('sumatera_selatan', 'Sumatera Selatan'),
        ('sumatera_barat', 'Sumatera Barat'),
        ('bengkulu', 'Bengkulu'),
        ('riau', 'Riau'),
        ('kepulauan_riau', 'Kepulauan Riau'),
        ('jambi', 'Jambi'),
        ('lampung', 'Lampung'),
        ('bangka_belitung', 'Bangka Belitung'),
        ('kalimantan_barat', 'Kalimantan Barat'),
        ('kalimantan_timur', 'Kalimantan Timur'),
        ('kalimantan_selatan', 'Kalimantan Selatan'),
        ('kalimantan_tengah', 'Kalimantan Tengah'),
        ('kalimantan_utara', 'Kalimantan Utara'),
        ('banten', 'Banten'),
        ('dki_jakarta', 'DKI Jakarta'),
        ('jawa_barat', 'Jawa Barat'),
        ('jawa_tengah', 'Jawa Tengah'),
        ('daerah_istimewa_yogyakarta', 'Daerah Istimewa Yogyakarta'),
        ('jawa_timur', 'Jawa Timur'),
        ('bali', 'Bali'),
        ('nusa_tenggara_timur', 'Nusa Tenggara Timur'),
        ('nusa_tenggara_barat', 'Nusa Tenggara Barat'),
        ('gorontalo', 'Gorontalo'),
        ('sulawesi_barat', 'Sulawesi Barat'),
        ('sulawesi_tengah', 'Sulawesi Tengah'),
        ('sulawesi_utara', 'Sulawesi Utara'),
        ('sulawesi_tenggara', 'Sulawesi Tenggara'),
        ('sulawesi_selatan', 'Sulawesi Selatan'),
        ('maluku_utara', 'Maluku Utara'),
        ('maluku', 'Maluku'),
        ('papua_barat', 'Papua Barat'),
        ('papua_barat_daya', 'Papua Barat Daya'),
        ('papua_tengah', 'Papua Tengah'),
        ('papua', 'Papua'),
        ('papua_selatan', 'Papua Selatan'),
        ('papua_pegunungan', 'Papua Pegunungan'),
    ]
    
    # Online platform choices (for online events)
    ONLINE_PLATFORM_CHOICES = [
        ('zoom', 'Zoom'),
        ('google_meet', 'Google Meet'),
        ('teams', 'Microsoft Teams'),
        ('webex', 'Cisco Webex'),
        ('skype', 'Skype'),
        ('discord', 'Discord'),
        ('youtube_live', 'YouTube Live'),
        ('facebook_live', 'Facebook Live'),
        ('instagram_live', 'Instagram Live'),
        ('twitch', 'Twitch'),
        ('lainnya', 'Lainnya'),
    ]
    
    # User relationship (one-to-one with custom User model)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='event_profile',
        help_text="Associated user account"
    )
    
    # Basic information
    name = models.CharField(
        max_length=200,
        help_text="Name of the event or organization"
    )
    
    description = models.TextField(
        help_text="Description of the event or organization"
    )
    
    # Event type
    event_type = models.CharField(
        max_length=10,
        choices=EVENT_TYPE_CHOICES,
        default='offline',
        help_text="Type of event: Online, Offline, or Hybrid"
    )
    
    # Location (dynamic based on event type)
    location = models.CharField(
        max_length=50,
        help_text="Location/platform where events are held"
    )
    
    # Target audience
    target_audience = models.TextField(
        blank=True,
        null=True,
        help_text="Description of the target audience for this event (optional)"
    )
    
    # Contact information
    email = models.EmailField(
        help_text="Contact email address"
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Phone number (optional)"
    )
    
    is_phone_public = models.BooleanField(
        default=False,
        help_text="Whether to display phone number publicly"
    )
    
    # Website
    website = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Event or organization website URL (optional)"
    )
    
    # LinkedIn profile
    linkedin_url = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="LinkedIn profile URL (optional)"
    )
    
    # Cover image (optional, but recommended)
    cover_image = models.ImageField(
        upload_to=event_cover_upload_path,
        blank=True,
        null=True,
        help_text="Cover image for the event or organization (recommended)"
    )
    
    # Event dates (nullable for one-time events)
    start_date = models.DateField(
        blank=True,
        null=True,
        help_text="Start date for one-time events (optional)"
    )
    
    end_date = models.DateField(
        blank=True,
        null=True,
        help_text="End date for one-time events (optional)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the profile was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the profile was last updated"
    )
    
    class Meta:
        verbose_name = "Event Profile"
        verbose_name_plural = "Event Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_location_display()}"
    
    def get_public_phone(self):
        """
        Return phone number only if user wants it to be public.
        """
        return self.phone_number if self.is_phone_public else None
    
    def clean(self):
        """
        Custom validation to ensure end_date is after start_date
        and location is appropriate for event type.
        """
        from django.core.exceptions import ValidationError
        import os

        print(f"DEBUG EventProfile.clean(): event_type={self.event_type}, location={self.location}")

        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'End date must be after start date.'
                })

        # Validate location based on event type - with better error handling
        if self.event_type == 'online':
            # For online events, location should be from online platform choices
            valid_platforms = [choice[0] for choice in self.ONLINE_PLATFORM_CHOICES]
            if self.location and self.location not in valid_platforms:
                print(f"DEBUG EventProfile.clean(): Online validation failed. location='{self.location}', valid_platforms={valid_platforms[:5]}...")
                raise ValidationError({
                    'location': f'Please select a valid online platform for online events. Current: "{self.location}"'
                })
        elif self.event_type in ['offline', 'hybrid']:
            # For offline/hybrid events, location should be from province choices
            valid_provinces = [choice[0] for choice in self.PROVINCE_CHOICES]
            if self.location and self.location not in valid_provinces:
                print(f"DEBUG EventProfile.clean(): Offline/hybrid validation failed. location='{self.location}', valid_provinces={valid_provinces[:5]}...")
                raise ValidationError({
                    'location': f'Please select a valid province for offline/hybrid events. Current: "{self.location}"'
                })

        print(f"DEBUG EventProfile.clean(): Validation PASSED")
    
    def save(self, *args, **kwargs):
        """
        Custom save method to run validation.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def location_display(self):
        """
        Get the display name of the location based on event type.
        """
        if self.event_type == 'online':
            # Get display name from online platform choices
            for choice_value, choice_display in self.ONLINE_PLATFORM_CHOICES:
                if choice_value == self.location:
                    return choice_display
            return self.location  # Fallback if not found
        else:
            # Get display name from province choices
            for choice_value, choice_display in self.PROVINCE_CHOICES:
                if choice_value == self.location:
                    return choice_display
            return self.location  # Fallback if not found
    
    @classmethod
    def get_location_choices_for_event_type(cls, event_type):
        """
        Get appropriate location choices based on event type.
        """
        if event_type == 'online':
            return cls.ONLINE_PLATFORM_CHOICES
        elif event_type in ['offline', 'hybrid']:
            return cls.PROVINCE_CHOICES
        else:
            return []
    
    @property
    def is_one_time_event(self):
        """
        Check if this is a one-time event (has start/end dates).
        """
        return self.start_date is not None or self.end_date is not None
    
    @property
    def event_duration_display(self):
        """
        Get formatted event duration information.
        """
        if not self.is_one_time_event:
            return "Ongoing/Regular Events"
        
        if self.start_date and self.end_date:
            if self.start_date == self.end_date:
                return f"Single Day: {self.start_date.strftime('%B %d, %Y')}"
            else:
                return f"{self.start_date.strftime('%B %d, %Y')} - {self.end_date.strftime('%B %d, %Y')}"
        elif self.start_date:
            return f"Starting: {self.start_date.strftime('%B %d, %Y')}"
        elif self.end_date:
            return f"Ending: {self.end_date.strftime('%B %d, %Y')}"
        
        return "Date not specified"
    
    @property
    def is_active_event(self):
        """
        Check if the event is currently active (ongoing or future).
        """
        if not self.is_one_time_event:
            return True  # Ongoing/regular events are always considered active
        
        today = timezone.now().date()
        
        if self.end_date:
            return today <= self.end_date
        elif self.start_date:
            return today <= self.start_date
        
        return True  # If no dates specified, consider active
    
    @property
    def event_status(self):
        """
        Get the current status of the event.
        """
        if not self.is_one_time_event:
            return "Ongoing"
        
        today = timezone.now().date()
        
        if self.start_date and self.end_date:
            if today < self.start_date:
                return "Upcoming"
            elif self.start_date <= today <= self.end_date:
                return "Active"
            else:
                return "Completed"
        elif self.start_date:
            if today < self.start_date:
                return "Upcoming"
            else:
                return "Active"
        elif self.end_date:
            if today <= self.end_date:
                return "Active"
            else:
                return "Completed"
        
        return "Active"
