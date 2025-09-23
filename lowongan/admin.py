from django.contrib import admin
from .models import Lowongan, LowonganApplication


@admin.register(Lowongan)
class LowonganAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'job_type', 'expertise_category', 'created_by',
        'location', 'status', 'event_date', 'application_deadline',
        'created_at'
    ]
    list_filter = [
        'status', 'job_type', 'expertise_category', 'location',
        'experience_level_required', 'is_remote', 'created_at'
    ]
    search_fields = ['title', 'description', 'created_by__username']
    readonly_fields = ['id', 'created_at', 'updated_at', 'published_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'created_by', 'status')
        }),
        ('Job Details', {
            'fields': (
                'job_type', 'expertise_category', 'experience_level_required',
                'requirements'
            )
        }),
        ('Location and Timing', {
            'fields': (
                'location', 'is_remote', 'event_date', 'event_time',
                'duration_hours'
            )
        }),
        ('Application Details', {
            'fields': (
                'application_deadline', 'max_applicants'
            )
        }),
        ('Compensation', {
            'fields': ('budget_amount', 'budget_negotiable')
        }),
        ('Contact Information', {
            'fields': ('contact_email', 'contact_phone')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'created_by', 'expertise_category'
        )


@admin.register(LowonganApplication)
class LowonganApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'applicant', 'lowongan', 'status', 'applied_at', 'reviewed_at'
    ]
    list_filter = ['status', 'applied_at', 'reviewed_at']
    search_fields = [
        'applicant__username', 'lowongan__title',
        'lowongan__created_by__username'
    ]
    readonly_fields = ['id', 'applied_at', 'updated_at', 'reviewed_at']
    date_hierarchy = 'applied_at'

    fieldsets = (
        ('Application Information', {
            'fields': ('lowongan', 'applicant', 'status')
        }),
        ('Application Details', {
            'fields': ('cover_letter', 'proposed_rate', 'availability_notes')
        }),
        ('Metadata', {
            'fields': ('id', 'applied_at', 'updated_at', 'reviewed_at'),
            'classes': ('collapse',)
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'applicant', 'lowongan', 'lowongan__created_by'
        )
