from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, Booking


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model with additional fields and actions.
    """
    
    # Add custom fields to the user admin
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('user_type', 'is_approved', 'approval_date', 'created_at', 'updated_at')
        }),
    )
    
    # Add custom fields to the add user form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('user_type', 'email', 'first_name', 'last_name')
        }),
    )
    
    # Display these fields in the user list
    list_display = [
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'user_type', 
        'is_approved', 
        'approval_status_display',
        'is_staff', 
        'date_joined'
    ]
    
    # Add filters for the admin list view
    list_filter = BaseUserAdmin.list_filter + ('user_type', 'is_approved', 'approval_date')
    
    # Add search functionality
    search_fields = BaseUserAdmin.search_fields + ('user_type',)
    
    # Make some fields read-only
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
    
    # Custom actions
    actions = ['approve_selected_users', 'disapprove_selected_users']
    
    def approval_status_display(self, obj):
        """
        Display approval status with color coding.
        """
        if obj.is_approved:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Approved</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Pending</span>'
            )
    approval_status_display.short_description = 'Approval Status'
    
    def approve_selected_users(self, request, queryset):
        """
        Admin action to approve selected users and send approval emails.
        """
        approved_count = 0
        email_sent_count = 0
        
        for user in queryset.filter(is_approved=False):
            user.approve_user()
            approved_count += 1
            
            # Try to send approval email
            if user.email and user.send_approval_email():
                email_sent_count += 1
        
        if approved_count > 0:
            self.message_user(
                request,
                f'Successfully approved {approved_count} user(s). '
                f'Approval emails sent to {email_sent_count} user(s).'
            )
        else:
            self.message_user(request, 'No users were approved (they may already be approved).')
    
    approve_selected_users.short_description = "Approve selected users and send emails"
    
    def disapprove_selected_users(self, request, queryset):
        """
        Admin action to disapprove selected users.
        """
        updated = queryset.update(is_approved=False, approval_date=None)
        if updated:
            self.message_user(request, f'Successfully disapproved {updated} user(s).')
        else:
            self.message_user(request, 'No users were updated.')
    
    disapprove_selected_users.short_description = "Disapprove selected users"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('event', 'narasumber', 'status', 'booking_date', 'created_at')
    list_filter = ('status', 'booking_date', 'created_at')
    search_fields = ('event__username', 'narasumber__username', 'message')
    date_hierarchy = 'booking_date'
    ordering = ('-created_at',)
