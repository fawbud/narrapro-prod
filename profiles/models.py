from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives

from django.conf import settings
import uuid
from django.core.validators import URLValidator
import os


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
        ('pengguna', 'Pengguna'),
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
        This method uses Resend SMTP via django-anymail and includes the Narrapro logo.
        """
        if not self.is_approved:
            raise ValueError("Tidak dapat mengirim email persetujui untuk pengguna yang belum disetujui")

        subject = "Akun NarraPro Anda Telah Disetujui!"
        logo_url = "https://narrapro.up.railway.app/static/images/narrapro-logo.png"

        # Format the approval date with the correct timezone
        if self.approval_date:
            local_approval_date = self.approval_date.astimezone(timezone.get_current_timezone())
            formatted_approval_date = f"{local_approval_date.strftime('%d %B %Y pukul %H:%M')} WIB"
        else:
            formatted_approval_date = 'N/A'

        # Plain text version
        text_message = f"""
        Yth. {self.first_name or self.username},
        
        Kabar baik! Akun NarraPro Anda telah disetujui oleh tim admin kami.
        
        Detail Akun:
        - Username: {self.username}
        - Email: {self.email}
        - Tipe Pengguna: {self.get_user_type_display()}
        - Disetujui pada: {formatted_approval_date}
        
        Anda sekarang dapat mengakses semua fitur yang tersedia untuk pengguna {self.get_user_type_display().lower()}.
        
        Selamat datang di NarraPro!
        
        Hormat kami,
        Tim NarraPro
        """

        # HTML version
        html_message = f"""
        <html>
            <body style="font-family: sans-serif;">
                <img src="{logo_url}" alt="Narrapro Logo" style="max-width: 150px; margin-bottom: 20px;">
                <p>Yth. {self.first_name or self.username},</p>
                <p>Kabar baik! Akun NarraPro Anda telah disetujui oleh tim admin kami.</p>
                
                <p><b>Detail Akun:</b></p>
                <ul>
                    <li>Username: {self.username}</li>
                    <li>Email: {self.email}</li>
                    <li>Tipe Pengguna: {self.get_user_type_display()}</li>
                    <li>Disetujui pada: {formatted_approval_date}</li>
                </ul>
                
                <p>Anda sekarang dapat mengakses semua fitur yang tersedia untuk pengguna {self.get_user_type_display().lower()}.</p>
                
                <p>Selamat datang di NarraPro!</p>
                
                <p>Hormat kami,<br>
                Tim NarraPro</p>
            </body>
        </html>
        """

        try:
            # Create email message
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[self.email]
            )
            msg.attach_alternative(html_message, "text/html")
            msg.send(fail_silently=False)
            return True
        except Exception as e:
            # Log the error in production
            print(f"Gagal mengirim email persetujuan ke {self.email}: {str(e)}")
            return False

class Booking(models.Model):
    """
    Model to represent a booking made by an event organizer for a narasumber.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Menunggu'),
        ('APPROVED', 'Disetujui'),
        ('REJECTED', 'Ditolak'),
        ('CANCELED', 'Dibatalkan'),
    ]

    event = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='outgoing_bookings',
        limit_choices_to={'user_type': 'event'},
        help_text="The event organizer making the booking",
        null=True, blank=True,
    )
    narasumber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='incoming_bookings',
        limit_choices_to={'user_type': 'narasumber'},
        help_text="The narasumber being booked"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="The current status of the booking"
    )
    booking_date = models.DateTimeField(
        help_text="The date and time of the booking"
    )
    message = models.TextField(
        blank=True,
        help_text="A message from the event organizer to the narasumber"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        ordering = ['-booking_date']

    def __str__(self):
        try:
            event_name = self.event.event_profile.name if hasattr(self.event, 'event_profile') else self.event.username
        except:
            event_name = self.event.username
        return f"Booking for {self.narasumber.get_full_name()} by {event_name} on {self.booking_date}"