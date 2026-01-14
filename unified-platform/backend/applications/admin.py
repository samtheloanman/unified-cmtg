"""
Django Admin Configuration for Applications
"""

from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """Admin interface for Application model."""

    list_display = [
        'id',
        'full_name',
        'borrower_email',
        'loan_amount',
        'status',
        'selected_program',
        'created_at',
        'status_updated_at',
    ]

    list_filter = [
        'status',
        'loan_purpose',
        'property_type',
        'property_state',
        'created_at',
    ]

    search_fields = [
        'borrower_email',
        'borrower_first_name',
        'borrower_last_name',
        'floify_id',
        'floify_loan_id',
        'property_address',
    ]

    readonly_fields = [
        'floify_id',
        'floify_loan_id',
        'created_at',
        'updated_at',
        'status_updated_at',
        'floify_data',
    ]

    fieldsets = [
        ('Floify Identifiers', {
            'fields': ['floify_id', 'floify_loan_id']
        }),
        ('Borrower Information', {
            'fields': [
                'borrower_first_name',
                'borrower_last_name',
                'borrower_email',
                'borrower_phone',
            ]
        }),
        ('Loan Details', {
            'fields': [
                'loan_amount',
                'loan_purpose',
                'property_type',
                'property_address',
                'property_state',
            ]
        }),
        ('Program Selection', {
            'fields': ['selected_program', 'selected_lender']
        }),
        ('Status', {
            'fields': ['status', 'status_updated_at']
        }),
        ('Metadata', {
            'fields': ['notes', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
        ('Floify Raw Data', {
            'fields': ['floify_data'],
            'classes': ['collapse']
        }),
    ]

    date_hierarchy = 'created_at'

    def full_name(self, obj):
        """Display full borrower name."""
        return obj.full_name
    full_name.short_description = 'Borrower'
