from django.contrib import admin
from .models import RateSheet
from .tasks import process_ratesheet

@admin.action(description='Reprocess selected rate sheets')
def reprocess_ratesheets(modeladmin, request, queryset):
    for rs in queryset:
        process_ratesheet.delay(rs.id)

@admin.register(RateSheet)
class RateSheetAdmin(admin.ModelAdmin):
    list_display = ['name', 'lender', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'lender']
    actions = [reprocess_ratesheets]
    readonly_fields = ['log', 'processed_at']
