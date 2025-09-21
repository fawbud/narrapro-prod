from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import uuid


class User(AbstractUser):
    """
    Custom User model extending AbstractUser with additional fields for user type,
    approval status, timestamps, and UUID primary key.
    """
    
    # Override the default id field with UUID
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user"
    )
    
    USER_TYPE_CHOICES = [
        ('', 'Pilih Role'),
        ('narasumber', 'Narasumber'),
        ('event', 'Event'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        blank=True,  # Allow blank for the default choice
        help_text="Type of user account"
    )
    
    is_approved = models.BooleanField(
        default=False,
        help_text="Indicates whether the user's registration was approved by admin"
    )
    
    approval_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when the admin approved the user's registration"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the user account was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the user account was last updated"
    )
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def approve_user(self):
        """
        Approve the user and set the approval date to now.
        """
        self.is_approved = True
        self.approval_date = timezone.now()
        self.save(update_fields=['is_approved', 'approval_date'])
    
    def send_approval_email(self):
        """
        Send an email to the user when their account is approved.
        This method uses Resend SMTP via django-anymail.
        """
        if not self.is_approved:
            raise ValueError("Cannot send approval email to unapproved user")
        
        subject = "Your NarraPro Account Has Been Approved!"
        
        message = f"""
        Dear {self.first_name or self.username},
        
        Great news! Your NarraPro account has been approved by our admin team.
        
        Account Details:
        - Username: {self.username}
        - Email: {self.email}
        - User Type: {self.get_user_type_display()}
        - Approved on: {self.approval_date.strftime('%B %d, %Y at %I:%M %p') if self.approval_date else 'N/A'}
        
        You can now access all features available to {self.get_user_type_display().lower()} users.
        
        Welcome to NarraPro!
        
        Best regards,
        The NarraPro Team
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@narrapro.com'),
                recipient_list=[self.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Log the error in production
            print(f"Failed to send approval email to {self.email}: {str(e)}")
            return False
