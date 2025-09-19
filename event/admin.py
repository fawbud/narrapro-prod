from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import EventProfile


@admin.register(EventProfile)
class EventProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for EventProfile model.
    """
    list_display = [
        'name',
        'user_username',
        'location_display',
        'event_status_display',
        'event_duration_display',
        'has_website',
        'cover_image_preview',
        'created_at'
    ]
    
    list_filter = [
        'location',
        'created_at',
        'start_date',
        'end_date'
    ]
    
    search_fields = [
        'name',
        'description',
        'user__username',
        'user__email',
        'contact'
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'cover_image_preview_large']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'name', 'description')
        }),
        ('Location & Contact', {
            'fields': ('location', 'contact', 'website')
        }),
        ('Event Dates', {
            'fields': ('start_date', 'end_date'),
            'description': 'Optional: Set dates for one-time events. Leave blank for ongoing/regular events.'
        }),
        ('Media', {
            'fields': ('cover_image', 'cover_image_preview_large'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    ordering = ['-created_at']
    date_hierarchy = 'start_date'
    
    def user_username(self, obj):
        """
        Display the associated user's username.
        """
        return obj.user.username
    user_username.short_description = "Username"
    user_username.admin_order_field = 'user__username'
    
    def location_display(self, obj):
        """
        Display the location in a more readable format.
        """
        return obj.get_location_display()
    location_display.short_description = "Location"
    location_display.admin_order_field = 'location'
    
    def event_status_display(self, obj):
        """
        Display the event status with color coding.
        """
        status = obj.event_status
        color_map = {
            'Upcoming': 'blue',
            'Active': 'green',
            'Completed': 'gray',
            'Ongoing': 'purple'
        }
        color = color_map.get(status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, status
        )
    event_status_display.short_description = "Status"
    
    def has_website(self, obj):
        """
        Display whether the event has a website.
        """
        if obj.website:
            return format_html('<span style="color: green;">✓ Yes</span>')
        return format_html('<span style="color: red;">✗ No</span>')
    has_website.short_description = "Website"
    
    def cover_image_preview(self, obj):
        """
        Display a small preview of the cover image in list view.
        """
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 30px; object-fit: cover; border-radius: 3px;" />',
                obj.cover_image.url
            )
        return format_html('<span style="color: gray;">No image</span>')
    cover_image_preview.short_description = "Cover"
    
    def cover_image_preview_large(self, obj):
        """
        Display a larger preview of the cover image in detail view.
        """
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; border-radius: 5px;" />',
                obj.cover_image.url
            )
        return "No cover image uploaded"
    cover_image_preview_large.short_description = "Cover Image Preview"
    
    actions = ['mark_as_completed', 'clear_event_dates']
    
    def mark_as_completed(self, request, queryset):
        """
        Admin action to mark events as completed by setting end_date to today.
        """
        today = timezone.now().date()
        updated = 0
        
        for event in queryset:
            if not event.end_date or event.end_date > today:
                event.end_date = today
                event.save()
                updated += 1
        
        self.message_user(
            request,
            f'{updated} event(s) marked as completed.'
        )
    mark_as_completed.short_description = "Mark selected events as completed"
    
    def clear_event_dates(self, request, queryset):
        """
        Admin action to clear event dates (convert to ongoing events).
        """
        updated = queryset.update(start_date=None, end_date=None)
        self.message_user(
            request,
            f'{updated} event(s) converted to ongoing events (dates cleared).'
        )
    clear_event_dates.short_description = "Convert to ongoing events (clear dates)"
    
    def get_queryset(self, request):
        """
        Optimize queryset to reduce database queries.
        """
        return super().get_queryset(request).select_related('user')
