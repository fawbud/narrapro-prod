from django.contrib import admin
from django.utils.html import format_html
from .models import ExpertiseCategory, NarasumberProfile


@admin.register(ExpertiseCategory)
class ExpertiseCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for ExpertiseCategory model.
    """
    list_display = ['name', 'description_preview', 'narasumber_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    ordering = ['name']
    
    def description_preview(self, obj):
        """
        Show a preview of the description.
        """
        if obj.description:
            return obj.description[:100] + "..." if len(obj.description) > 100 else obj.description
        return "-"
    description_preview.short_description = "Description Preview"
    
    def narasumber_count(self, obj):
        """
        Show the number of narasumber profiles in this category.
        """
        count = obj.narasumber_profiles.count()
        return format_html('<strong>{}</strong>', count)
    narasumber_count.short_description = "Narasumber Count"


@admin.register(NarasumberProfile)
class NarasumberProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for NarasumberProfile model.
    """
    list_display = [
        'full_name', 
        'user_username',
        'expertise_area', 
        'experience_level', 
        'years_of_experience',
        'location_display',
        'phone_status',
        'created_at'
    ]
    
    list_filter = [
        'expertise_area', 
        'experience_level', 
        'location', 
        'is_phone_public',
        'created_at'
    ]
    
    search_fields = [
        'full_name', 
        'user__username', 
        'user__email',
        'email',
        'bio'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'bio')
        }),
        ('Expertise', {
            'fields': ('expertise_area', 'experience_level', 'years_of_experience')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number', 'is_phone_public')
        }),
        ('Location', {
            'fields': ('location',)
        }),
        ('Online Presence', {
            'fields': ('portfolio_link', 'linkedin_url'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-created_at']
    
    def user_username(self, obj):
        """
        Display the associated user's username.
        """
        return obj.user.username
    user_username.short_description = "Username"
    user_username.admin_order_field = 'user__username'
    
    def phone_status(self, obj):
        """
        Display phone number availability status.
        """
        if obj.phone_number:
            if obj.is_phone_public:
                return format_html('<span style="color: green;">✓ Public</span>')
            else:
                return format_html('<span style="color: orange;">✓ Private</span>')
        return format_html('<span style="color: gray;">✗ Not provided</span>')
    phone_status.short_description = "Phone Status"
    
    def location_display(self, obj):
        """
        Display the location in a more readable format.
        """
        return obj.get_location_display()
    location_display.short_description = "Location"
    location_display.admin_order_field = 'location'
    
    def save_model(self, request, obj, form, change):
        """
        Custom save method to handle any additional processing.
        """
        super().save_model(request, obj, form, change)
    
    actions = ['make_phone_public', 'make_phone_private']
    
    def make_phone_public(self, request, queryset):
        """
        Admin action to make phone numbers public for selected profiles.
        """
        updated = queryset.filter(phone_number__isnull=False).update(is_phone_public=True)
        self.message_user(
            request,
            f'{updated} profile(s) phone numbers are now public (only profiles with phone numbers were updated).'
        )
    make_phone_public.short_description = "Make phone numbers public"
    
    def make_phone_private(self, request, queryset):
        """
        Admin action to make phone numbers private for selected profiles.
        """
        updated = queryset.update(is_phone_public=False)
        self.message_user(
            request,
            f'{updated} profile(s) phone numbers are now private.'
        )
    make_phone_private.short_description = "Make phone numbers private"
