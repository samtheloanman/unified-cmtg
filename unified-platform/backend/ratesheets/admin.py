from django.contrib import admin
from .models import RateSheet
<<<<<<< HEAD

@admin.register(RateSheet)
class RateSheetAdmin(admin.ModelAdmin):
    list_display = ('lender', 'name', 'status', 'processed_at', 'created_at')
    list_filter = ('status', 'lender', 'created_at')
    search_fields = ('name', 'lender__company_name')
    readonly_fields = ('processed_at', 'log')
    
    actions = ['reprocess_ratesheets']
    
    def reprocess_ratesheets(self, request, queryset):
        # Placeholder for celery task trigger
        for sheet in queryset:
            # process_ratesheet.delay(sheet.id)
            pass
        self.message_user(request, f"Started processing for {queryset.count()} rate sheets.")
    reprocess_ratesheets.short_description = "Reprocess selected rate sheets"

=======
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
>>>>>>> origin/jules/phase1-foundation-10297780927730413954
