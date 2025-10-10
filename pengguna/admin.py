from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import PenggunaProfile, PenggunaBooking


@admin.register(PenggunaProfile)
class PenggunaProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for PenggunaProfile model.
    """
    list_display = [
        'full_name',
        'user_username',
        'email',
        'phone_status',
        'created_at',
    ]
    list_filter = [
        'is_phone_public',
        'created_at',
    ]
    search_fields = [
        'full_name',
        'user__username',
        'user__email',
        'email',
        'bio',
    ]
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'bio'),
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'is_phone_public'),
        }),
        ('Profile Picture', {
            'fields': ('profile_picture', 'avatar'),
        }),
        ('Online Presence', {
            'fields': ('website', 'linkedin_url'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    ordering = ['-created_at']

    def user_username(self, obj):
        return obj.user.username if obj.user else "-"
    user_username.short_description = "Username"
    user_username.admin_order_field = "user__username"

    def phone_status(self, obj):
        if obj.phone_number:
            if obj.is_phone_public:
                return format_html('<span style="color: green;">✓ Public</span>')
            else:
                return format_html('<span style="color: orange;">✓ Private</span>')
        return format_html('<span style="color: gray;">✗ Not provided</span>')
    phone_status.short_description = "Phone Status"


@admin.register(PenggunaBooking)
class PenggunaBookingAdmin(admin.ModelAdmin):
    """
    Admin configuration for PenggunaBooking model.
    """
    list_display = [
        'booking_link',
        'pengguna_username',
        'narasumber_name',
        'interview_topic',
        'platform',
        'contact_email',
        'created_at',
    ]
    list_filter = [
        'platform',
        'created_at',
    ]
    search_fields = [
        'pengguna__username',
        'pengguna__email',
        'booking__narasumber__full_name',
        'interview_topic',
        'description',
        'contact_email',
        'contact_phone',
    ]
    readonly_fields = ['created_at', 'updated_at', 'booking_link']

    fieldsets = (
        ('Booking Relation', {
            'fields': ('booking', 'booking_link', 'pengguna'),
        }),
        ('Interview Information', {
            'fields': ('interview_topic', 'description', 'platform', 'location_detail'),
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone', 'is_phone_public'),
        }),
        ('Online Presence', {
            'fields': ('website', 'linkedin_url'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    ordering = ['-created_at']

    def booking_link(self, obj):
        """
        Display booking ID and provide admin link that bypasses user views.
        """
        if obj.booking_id:
            # Use JavaScript to ensure we stay in admin context
            onclick_script = f"window.open('/admin/profiles/booking/{obj.booking_id}/change/', '_blank'); return false;"
            return format_html(
                '<a href="/admin/profiles/booking/{}/change/" onclick="{}" target="_blank" style="color: #007cba;">Booking #{}</a>',
                obj.booking_id, onclick_script, obj.booking_id
            )
        return "-"
    booking_link.short_description = "Booking"

    def pengguna_username(self, obj):
        return obj.pengguna.username if obj.pengguna else "UnknownPengguna"
    pengguna_username.short_description = "Pengguna"
    pengguna_username.admin_order_field = "pengguna__username"

    def narasumber_name(self, obj):
        if obj.booking and hasattr(obj.booking, 'narasumber'):
            return obj.booking.narasumber.get_full_name()
        return "UnknownNarasumber"
    narasumber_name.short_description = "Narasumber"
