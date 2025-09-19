from django.db import models
from django.core.validators import MinValueValidator, URLValidator
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class ExpertiseCategory(models.Model):
    """
    Model to represent different expertise categories for narasumber.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name of the expertise category"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Optional description of the expertise category"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the category was created"
    )
    
    class Meta:
        verbose_name = "Expertise Category"
        verbose_name_plural = "Expertise Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class NarasumberProfile(models.Model):
    """
    Profile model for narasumber users containing detailed information
    about their expertise, experience, and contact details.
    """
    
    # Experience level choices
    EXPERIENCE_LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('EXPERT', 'Expert'),
    ]
    
    # Indonesian provinces choices
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
        related_name='narasumber_profile',
        help_text="Associated user account"
    )
    
    # Basic information
    full_name = models.CharField(
        max_length=200,
        help_text="Full name of the narasumber"
    )
    
    bio = models.TextField(
        help_text="Biography or description of the narasumber"
    )
    
    # Expertise information
    expertise_area = models.ForeignKey(
        ExpertiseCategory,
        on_delete=models.CASCADE,
        related_name='narasumber_profiles',
        help_text="Area of expertise"
    )
    
    experience_level = models.CharField(
        max_length=15,
        choices=EXPERIENCE_LEVEL_CHOICES,
        help_text="Level of experience in the expertise area"
    )
    
    years_of_experience = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        help_text="Number of years of experience"
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
    
    # Location
    location = models.CharField(
        max_length=50,
        choices=PROVINCE_CHOICES,
        help_text="Province/location in Indonesia"
    )
    
    # Portfolio and social media
    portfolio_link = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Portfolio website URL (optional)"
    )
    
    social_media_links = models.JSONField(
        default=dict,
        blank=True,
        help_text="Social media links in JSON format (e.g., {'linkedin': 'url', 'twitter': 'url'})"
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
        verbose_name = "Narasumber Profile"
        verbose_name_plural = "Narasumber Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.expertise_area.name}"
    
    def get_public_phone(self):
        """
        Return phone number only if user wants it to be public.
        """
        return self.phone_number if self.is_phone_public else None
    
    def get_social_media_link(self, platform):
        """
        Get a specific social media link by platform name.
        """
        return self.social_media_links.get(platform, None)
    
    def add_social_media_link(self, platform, url):
        """
        Add or update a social media link.
        """
        if self.social_media_links is None:
            self.social_media_links = {}
        self.social_media_links[platform] = url
        self.save(update_fields=['social_media_links'])
    
    def remove_social_media_link(self, platform):
        """
        Remove a social media link.
        """
        if self.social_media_links and platform in self.social_media_links:
            del self.social_media_links[platform]
            self.save(update_fields=['social_media_links'])
    
    @property
    def experience_display(self):
        """
        Get formatted experience information.
        """
        return f"{self.get_experience_level_display()} ({self.years_of_experience} years)"
    
    @property
    def location_display(self):
        """
        Get the display name of the location.
        """
        return self.get_location_display()
