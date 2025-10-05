from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import os
from django.core.validators import URLValidator


def get_storage():
    """Get the appropriate storage backend based on environment"""
    if os.getenv("PRODUCTION") == "true":
        from narrapro.simple_storage import SimpleSupabaseStorage
        print(f"NARASUMBER MODEL DEBUG: Using SimpleSupabaseStorage for production")
        return SimpleSupabaseStorage()
    else:
        from django.core.files.storage import default_storage
        print(f"NARASUMBER MODEL DEBUG: Using default storage for development")
        return default_storage
    
User = get_user_model()

def pengguna_profile_picture_upload_path(instance, filename):
    """
    Generate a unique upload path for pengguna profile pictures.
    Format: pengguna_profiles/user_id/uuid_filename
    """
    ext = filename.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return f"pengguna_profiles/{instance.user.id}/{unique_filename}"

def pengguna_avatar_upload_path(instance, filename):
    """
    Generate path unik untuk foto pengguna
    Format: pengguna_avatars/user_id/uuid_filename
    """
    ext = filename.split('.')[-1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    return f"pengguna_avatars/{instance.user.id}/{unique_filename}"


class PenggunaProfile(models.Model):
    """
    Profile untuk user biasa (bukan event organizer).
    User ini bisa melakukan booking, tapi tidak bisa membuat lowongan.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="pengguna_profile",
        help_text="User account yang terkait"
    )

    # Basic info
    full_name = models.CharField(max_length=200, help_text="Nama lengkap pengguna")
    bio = models.TextField(blank=True, null=True, help_text="Tentang pengguna (opsional)")
    email = models.EmailField(help_text="Alamat email pengguna")

    # 🆕 Add profile picture here
    profile_picture = models.ImageField(
        upload_to=pengguna_profile_picture_upload_path,
        blank=True,
        null=True,
        help_text="Foto profil pengguna (opsional)",
        storage=get_storage()
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Nomor telepon (opsional)"
    )
    is_phone_public = models.BooleanField(
        default=False,
        help_text="Apakah nomor telepon ditampilkan secara publik"
    )

    avatar = models.ImageField(
        upload_to=pengguna_avatar_upload_path,
        blank=True,
        null=True,
        help_text="Foto profil pengguna"
    )

    website = models.URLField(blank=True, null=True, help_text="Website pribadi (opsional)")
    linkedin_url = models.URLField(blank=True, null=True, help_text="LinkedIn (opsional)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pengguna Profile"
        verbose_name_plural = "Pengguna Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"

    def get_public_phone(self):
        return self.phone_number if self.is_phone_public else None


class PenggunaBooking(models.Model):
    """
    Extension booking khusus untuk pengguna biasa.
    One-to-one dengan Booking ori.
    """

    booking = models.OneToOneField(
        "profiles.Booking",
        on_delete=models.CASCADE,
        related_name="pengguna_extension",
        help_text="Relasi ke booking asli"
    )

    pengguna = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="pengguna_bookings",
        limit_choices_to={'user_type': 'pengguna'},  # pastikan ini user biasa
        help_text="Pengguna biasa yang membuat booking"
    )

    # Tambahan field mirip EventProfile tapi khusus untuk kebutuhan interview booking
    interview_topic = models.CharField(
        max_length=200,
        help_text="Topik wawancara atau tujuan booking"
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text="Deskripsi singkat tentang wawancara"
    )

    # Lokasi/Platform untuk wawancara
    platform = models.CharField(
        max_length=100,
        choices=[
            ('zoom', 'Zoom'),
            ('google_meet', 'Google Meet'),
            ('teams', 'Microsoft Teams'),
            ('offline', 'Offline (tatap muka)'),
        ],
        default='zoom',
        help_text="Media untuk wawancara"
    )

    location_detail = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Detail lokasi jika wawancara offline"
    )

    contact_email = models.EmailField(
        help_text="Email kontak pengguna"
    )

    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Nomor telepon pengguna (opsional)"
    )

    is_phone_public = models.BooleanField(
        default=False,
        help_text="Apakah nomor telepon ditampilkan ke narasumber"
    )

    website = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Website terkait wawancara (opsional)"
    )

    linkedin_url = models.URLField(
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="LinkedIn (opsional)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pengguna Booking"
        verbose_name_plural = "Pengguna Bookings"
        ordering = ["-created_at"]

    def __str__(self):
        return f"PenggunaBooking {self.pengguna.username} untuk {self.booking.narasumber.get_full_name()}"

    def get_public_phone(self):
        return self.contact_phone if self.is_phone_public else None