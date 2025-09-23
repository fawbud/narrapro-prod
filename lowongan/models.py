from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from narasumber.models import ExpertiseCategory
import uuid

User = get_user_model()


class Lowongan(models.Model):
    """
    Model representing job opportunities/gigs created by Event users
    that Narasumber users can apply for.
    """

    # Job types
    JOB_TYPE_CHOICES = [
        ('speaker', 'Speaker/Presenter'),
        ('workshop_facilitator', 'Workshop Facilitator'),
        ('moderator', 'Event Moderator'),
        ('panelist', 'Panel Discussion'),
        ('trainer', 'Training Session'),
        ('consultant', 'Consultation'),
        ('other', 'Other'),
    ]

    # Experience level required
    EXPERIENCE_LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('EXPERT', 'Expert'),
        ('ANY', 'Any Level'),
    ]

    # Status choices
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('OPEN', 'Open for Applications'),
        ('CLOSED', 'Closed'),
        ('COMPLETED', 'Completed'),
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

    # Basic information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the lowongan"
    )

    title = models.CharField(
        max_length=200,
        help_text="Title of the job opportunity"
    )

    description = models.TextField(
        help_text="Detailed description of the job requirements and responsibilities"
    )

    # Creator relationship
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lowongan_created',
        help_text="Event user who created this lowongan"
    )

    # Job details
    job_type = models.CharField(
        max_length=25,
        choices=JOB_TYPE_CHOICES,
        help_text="Type of job/role"
    )

    expertise_category = models.ForeignKey(
        ExpertiseCategory,
        on_delete=models.CASCADE,
        related_name='lowongan_opportunities',
        help_text="Required expertise category"
    )

    experience_level_required = models.CharField(
        max_length=15,
        choices=EXPERIENCE_LEVEL_CHOICES,
        default='ANY',
        help_text="Minimum experience level required"
    )

    # Location and timing
    location = models.CharField(
        max_length=50,
        choices=PROVINCE_CHOICES,
        help_text="Province/location where the job will take place"
    )

    is_remote = models.BooleanField(
        default=False,
        help_text="Whether this job can be done remotely"
    )

    event_date = models.DateField(
        help_text="Date when the event/job will take place"
    )

    event_time = models.TimeField(
        blank=True,
        null=True,
        help_text="Time when the event/job will start (optional)"
    )

    duration_hours = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(24)],
        help_text="Expected duration in hours"
    )

    # Compensation
    budget_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Budget/compensation amount in IDR (optional)"
    )

    budget_negotiable = models.BooleanField(
        default=True,
        help_text="Whether the budget is negotiable"
    )

    # Application details
    application_deadline = models.DateField(
        help_text="Deadline for applications"
    )

    max_applicants = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Maximum number of applicants (optional)"
    )

    requirements = models.TextField(
        blank=True,
        help_text="Additional requirements or qualifications"
    )

    contact_email = models.EmailField(
        help_text="Contact email for this opportunity"
    )

    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number (optional)"
    )

    # Status and management
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='DRAFT',
        help_text="Current status of the lowongan"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the lowongan was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the lowongan was last updated"
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the lowongan was published/made open"
    )

    class Meta:
        verbose_name = "Lowongan"
        verbose_name_plural = "Lowongan"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.get_job_type_display()}"

    def clean(self):
        """
        Custom validation
        """
        from django.core.exceptions import ValidationError

        # Validate event date is in the future
        if self.event_date and self.event_date < timezone.now().date():
            raise ValidationError({
                'event_date': 'Event date must be in the future.'
            })

        # Validate application deadline is before event date
        if self.application_deadline and self.event_date:
            if self.application_deadline >= self.event_date:
                raise ValidationError({
                    'application_deadline': 'Application deadline must be before event date.'
                })

        # Validate that only Event users can create lowongan
        # Only check if created_by is actually set and accessible
        try:
            if self.created_by_id and self.created_by and self.created_by.user_type != 'event':
                raise ValidationError({
                    'created_by': 'Only Event users can create lowongan.'
                })
        except (AttributeError, Lowongan.created_by.RelatedObjectDoesNotExist):
            # Skip validation if created_by is not accessible yet
            # This will be validated later when the relationship is properly set
            pass

    def save(self, *args, **kwargs):
        """
        Custom save method
        """
        # Set published_at when status changes to OPEN
        if self.status == 'OPEN' and not self.published_at:
            self.published_at = timezone.now()

        # Only run validation after the instance is properly initialized
        try:
            if self.created_by_id:
                self.full_clean()
        except (AttributeError, ValueError):
            # Skip validation if created_by is not set yet
            pass

        super().save(*args, **kwargs)

    @property
    def is_open_for_applications(self):
        """
        Check if lowongan is currently accepting applications
        """
        today = timezone.now().date()
        return (
            self.status == 'OPEN' and
            self.application_deadline >= today and
            self.event_date > today
        )

    @property
    def days_until_deadline(self):
        """
        Calculate days until application deadline
        """
        if not self.application_deadline:
            return None

        today = timezone.now().date()
        delta = self.application_deadline - today
        return delta.days if delta.days >= 0 else 0

    @property
    def location_display(self):
        """
        Get the display name of the location
        """
        return self.get_location_display()

    def get_applications_count(self):
        """
        Get the number of applications for this lowongan
        """
        return self.applications.count()

    def can_user_apply(self, user):
        """
        Check if a user can apply for this lowongan
        """
        if not user.is_authenticated:
            return False

        if user.user_type != 'narasumber':
            return False

        if not self.is_open_for_applications:
            return False

        # Check if user already applied
        if self.applications.filter(applicant=user).exists():
            return False

        return True


class LowonganApplication(models.Model):
    """
    Model representing applications from Narasumber users to Lowongan
    """

    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('WITHDRAWN', 'Withdrawn'),
    ]

    # Basic information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the application"
    )

    lowongan = models.ForeignKey(
        Lowongan,
        on_delete=models.CASCADE,
        related_name='applications',
        help_text="The lowongan being applied for"
    )

    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='lowongan_applications',
        help_text="The narasumber user applying"
    )

    # Application details
    cover_letter = models.TextField(
        help_text="Cover letter or motivation for applying"
    )

    proposed_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Proposed compensation rate in IDR (optional)"
    )

    availability_notes = models.TextField(
        blank=True,
        help_text="Notes about availability or scheduling (optional)"
    )

    # Status management
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Current status of the application"
    )

    # Timestamps
    applied_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the application was submitted"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the application was last updated"
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the application was reviewed"
    )

    class Meta:
        verbose_name = "Lowongan Application"
        verbose_name_plural = "Lowongan Applications"
        ordering = ['-applied_at']
        unique_together = ['lowongan', 'applicant']

    def __str__(self):
        return f"{self.applicant.username} -> {self.lowongan.title}"

    def clean(self):
        """
        Custom validation
        """
        from django.core.exceptions import ValidationError

        # Validate that only narasumber users can apply
        if self.applicant and self.applicant.user_type != 'narasumber':
            raise ValidationError({
                'applicant': 'Only Narasumber users can apply for lowongan.'
            })

        # Validate that lowongan is open for applications
        if self.lowongan and not self.lowongan.is_open_for_applications:
            raise ValidationError({
                'lowongan': 'This lowongan is not currently accepting applications.'
            })

    def save(self, *args, **kwargs):
        """
        Custom save method
        """
        # Set reviewed_at when status changes from PENDING
        if self.pk:
            old_instance = LowonganApplication.objects.get(pk=self.pk)
            if old_instance.status == 'PENDING' and self.status != 'PENDING':
                self.reviewed_at = timezone.now()

        self.full_clean()
        super().save(*args, **kwargs)
