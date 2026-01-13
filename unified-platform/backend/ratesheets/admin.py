from django.contrib import admin
from .models import RateSheet
from .tasks import process_ratesheet

@admin.action(description='Reprocess selected rate sheets')
def reprocess_ratesheets(modeladmin, request, queryset):
    for rs in queryset:
        process_ratesheet.delay(rs.id)

@admin.register(RateSheet)
class RateSheetAdmin(admin.ModelAdmin):
    list_display = ('lender', 'name', 'status', 'processed_at', 'created_at')
    list_filter = ('status', 'lender', 'created_at')
    search_fields = ('name', 'lender__company_name')
    readonly_fields = ('processed_at', 'log')
    actions = [reprocess_ratesheets]
