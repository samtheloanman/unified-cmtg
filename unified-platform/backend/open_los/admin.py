from django.contrib import admin
from .models import (
    LoanApplication,
    Borrower,
    EmploymentEntry,
    AssetEntry,
    LiabilityEntry,
    Declarations
)
from django.http import HttpResponse
from .xml_generator import MismoXmlService
from .pdf_generator import PDFGeneratorService

class EmploymentInline(admin.StackedInline):
    model = EmploymentEntry
    extra = 0

class DeclarationsInline(admin.StackedInline):
    model = Declarations
    extra = 0
    can_delete = False

class BorrowerInline(admin.StackedInline):
    model = Borrower
    extra = 0
    show_change_link = True
    fields = (
        ('first_name', 'last_name', 'ssn', 'birth_date'),
        ('email', 'phone', 'is_primary'),
        ('current_address_street', 'current_address_city', 'current_address_state', 'current_address_zip'),
        'years_at_current'
    )

class AssetInline(admin.TabularInline):
    model = AssetEntry
    extra = 0
    fields = ('account_type', 'financial_institution', 'cash_or_market_value', 'borrower')

class LiabilityInline(admin.TabularInline):
    model = LiabilityEntry
    extra = 0
    fields = ('liability_type', 'creditor_name', 'unpaid_balance', 'monthly_payment', 'to_be_paid_off', 'borrower')

@admin.register(LoanApplication)
class LoanApplicationAdmin(admin.ModelAdmin):
    list_display = ('floify_loan_id', 'borrower_summary', 'loan_amount', 'property_address', 'status', 'created_at')
    list_filter = ('status', 'property_state')
    search_fields = ('floify_loan_id', 'borrowers__last_name', 'borrowers__email', 'property_address')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [BorrowerInline, AssetInline, LiabilityInline]
    
    fieldsets = (
        ('Loan Details', {
            'fields': (
                ('floify_loan_id', 'status'),
                ('loan_amount', 'interest_rate', 'loan_purpose'),
                ('property_address', 'property_state')
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def borrower_summary(self, obj):
        return ", ".join([str(b) for b in obj.borrowers.all()])
    borrower_summary.short_description = "Borrowers"

    actions = ['export_xml_action', 'export_pdf_action']

    @admin.action(description='Export Fannie Mae 3.4 XML')
    def export_xml_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one loan to export.", level='ERROR')
            return
        
        app = queryset.first()
        xml_content = MismoXmlService.generate_xml(app)
        
        response = HttpResponse(xml_content, content_type="application/xml")
        response['Content-Disposition'] = f'attachment; filename="loan_{app.floify_loan_id}.xml"'
        return response

    @admin.action(description='Export Summary PDF')
    def export_pdf_action(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Please select exactly one loan to export.", level='ERROR')
            return
            
        app = queryset.first()
        pdf_content = PDFGeneratorService.generate_pdf(app)
        
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="loan_{app.floify_loan_id}.pdf"'
        return response

@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'application_link', 'email', 'is_primary')
    search_fields = ('first_name', 'last_name', 'email')
    inlines = [EmploymentInline, DeclarationsInline]

    def application_link(self, obj):
        return obj.application.floify_loan_id
    application_link.short_description = "Application"
