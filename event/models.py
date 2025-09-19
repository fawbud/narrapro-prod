from django.db import models
from django.core.validators import URLValidator
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class EventProfile(models.Model):
    """
    Profile model for event organizers containing detailed information
    about their events, contact details, and scheduling.
    """
    
    # Indonesian provinces choices (same as narasumber)
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
    
    # Location
    location = models.CharField(
        max_length=50,
        choices=PROVINCE_CHOICES,
        help_text="Province/location in Indonesia where events are held"
    )
    
    # Contact information
    contact = models.CharField(
        max_length=200,
        help_text="Contact information (phone, email, or other contact method)"
    )
    
    # Website
    website = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Event or organization website URL (optional)"
    )
    
    # Cover image
    cover_image = models.ImageField(
        upload_to='event_covers/',
        help_text="Cover image for the event or organization"
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
    
    def clean(self):
        """
        Custom validation to ensure end_date is after start_date.
        """
        from django.core.exceptions import ValidationError
        
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'End date must be after start date.'
                })
    
    def save(self, *args, **kwargs):
        """
        Custom save method to run validation.
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def location_display(self):
        """
        Get the display name of the location.
        """
        return self.get_location_display()
    
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
