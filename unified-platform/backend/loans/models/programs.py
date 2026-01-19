from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from localflavor.us.models import USStateField, USZipCodeField
from phonenumber_field.modelfields import PhoneNumberField
from common.fields import ChoiceArrayField
from common.models import TimestampedModel
from loans import choices

class AddressInfo(TimestampedModel):
    name = models.CharField(max_length=255, help_text="Please enter the lenders name")
    street_1 = models.CharField(max_length=255, blank=True, null=True)
    street_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = USStateField(blank=True, null=True, choices=choices.STATE_CHOICES)
    zipcode = USZipCodeField(blank=True, null=True)

    class Meta:
        app_label = 'loans'

    def __str__(self):
        return self.name

class LenderContact(TimestampedModel):
    contact_name = models.CharField(max_length=100, null=True, blank=True)
    contact_type = models.CharField(max_length=25, null=True, blank=True, choices=choices.LENDER_CONTACT_TYPE_CHOICES, default=choices.LENDER_CONTACT_TYPE_OWN)
    address = models.ForeignKey(AddressInfo, related_name="lender_contacts", null=True, on_delete=models.CASCADE)
    contact_phone = PhoneNumberField(null=True, blank=True)
    contact_fax = PhoneNumberField(null=True, blank=True)
    contact_email = models.CharField(max_length=100, null=True, blank=True)
    lender = models.ForeignKey('Lender', related_name="contacts", null=True, on_delete=models.CASCADE)

    class Meta:
        app_label = 'loans'

    def __str__(self):
        return self.contact_name

class BaseLoan(TimestampedModel):
    name = models.CharField(max_length=500)
    lender = models.ForeignKey('loans.Lender', on_delete=models.CASCADE)
    loan_type = models.CharField(choices=choices.LOAN_TYPE_CHOICES, max_length=15, default=choices.LOAN_TYPE_CONVENTIONAL)
    income_type = models.CharField(choices=choices.INCOME_TYPE_CHOICES, default=choices.INCOME_TYPE_STATED, max_length=30)
    occupancy = ChoiceArrayField(models.CharField(choices=choices.OCCUPANCY_CHOICES, max_length=15), default=list)
    property_types = ChoiceArrayField(models.CharField(choices=choices.PROPERTY_TYPE_CHOICES, max_length=15), default=list)
    property_sub_categories = ChoiceArrayField(models.CharField(max_length=25, choices=choices.PROPERTY_TYPE_SUB_CATEGORY_CHOICES), default=list)
    property_conditions = ChoiceArrayField(models.CharField(max_length=2, choices=choices.PROPERTY_CONDITION_CHOICES), default=list)
    recourse = ChoiceArrayField(models.CharField(choices=choices.RECOURSE_CHOICES, max_length=15), default=list)
    amortization_terms = ChoiceArrayField(models.CharField(max_length=20, choices=choices.AMORTIZATION_TERM_CHOICES), default=list)
    io_offered = models.BooleanField('I/O Offered', choices=choices.YES_NO_CHOICES, default=choices.YES)
    p_and_i_offered = models.BooleanField('P&I Offered', choices=choices.YES_NO_CHOICES, default=choices.YES)
    entity_type = ChoiceArrayField(models.CharField(max_length=20, choices=choices.BORROWING_ENTITY_TYPE_CHOICES), default=list)
    employment = ChoiceArrayField(models.CharField(choices=choices.EMPLOYMENT_CHOICES, max_length=10), default=list)
    percent_ownership = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    purpose = ChoiceArrayField(models.CharField(choices=choices.LOAN_PURPOSE_CHOICES, max_length=12), default=list)
    max_cash_out = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(Decimal('0.00'))])
    min_loan_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    max_loan_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    max_loan_to_value = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], null=True)
    reserve_requirement = models.PositiveSmallIntegerField()
    min_credit = models.PositiveSmallIntegerField(validators=[MinValueValidator(300), MaxValueValidator(850)], default=580)
    min_acreage = models.PositiveSmallIntegerField(blank=True, null=True)
    max_acreage = models.PositiveSmallIntegerField(blank=True, null=True)
    max_properties_financed = models.PositiveIntegerField(blank=True, null=True)
    refinance_seasoning = models.CharField(max_length=5, choices=choices.REFINANCE_SEASONING_CHOICES)
    ysp_available = models.BooleanField('YSP Available', choices=choices.YES_NO_CHOICES, default=choices.YES)
    max_ysp = models.PositiveSmallIntegerField('Max YSP', blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_compensation = models.PositiveSmallIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    processing_fee_allowed = models.BooleanField(choices=choices.YES_NO_CHOICES, default=choices.YES)
    max_dti = models.PositiveIntegerField('Max DTI', blank=True, null=True)
    lender_fee = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    prepayment_penalty = models.CharField(max_length=10, choices=choices.PPP_CHOICES)
    prepayment_cost = models.CharField(max_length=4, choices=choices.PPP_COST_CHOICES)
    rate_lock_available = models.BooleanField(choices=choices.YES_NO_CHOICES, default=choices.YES)
    rate_lock_terms = models.PositiveSmallIntegerField(choices=choices.RATE_LOCK_TERMS, blank=True, null=True)
    bk_allowed = models.BooleanField('BK Allowed', choices=choices.YES_NO_CHOICES, default=choices.YES)
    time_since_bk = models.PositiveSmallIntegerField('Time since BK', blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    foreclosure_allowed = models.BooleanField(choices=choices.YES_NO_CHOICES, default=choices.YES)
    time_since_foreclosure = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    short_sales_allowed = models.BooleanField(choices=choices.YES_NO_CHOICES, default=choices.YES)
    time_since_short_sale = models.PositiveSmallIntegerField(blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    nod_allowed = models.BooleanField('NOD Allowed', choices=choices.YES_NO_CHOICES, default=choices.YES)
    time_since_nod = models.PositiveSmallIntegerField('Time since NOD', blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    nos_allowed = models.BooleanField('NOS Allowed', choices=choices.YES_NO_CHOICES, default=choices.YES)
    time_since_nos = models.PositiveSmallIntegerField('Time since NOS', blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(10)])
    potential_rate_min = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    potential_rate_max = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    potential_cost_min = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    potential_cost_max = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    lien_position = models.CharField(max_length=5, choices=choices.MORTGAGE_NUMBER_CHOICES, default=choices.MORTGAGE_NUMBER_OTHER)

    class Meta:
        app_label = 'loans'
        abstract = True
        ordering = ['lender', 'loan_type']

    def __str__(self):
        return f"{self.lender} - {self.get_loan_type_display()}"

class LoanProgram(BaseLoan):
    max_ltv_on_purchase_price = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_ltv_on_arv = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_ltv_on_cost = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    max_ltv_on_rehab = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    min_borrower_contribution = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    min_dscr = models.FloatField('Min DSCR')

    def get_matching_qual_infos(self):
        from loans.queries import get_quals_for_loan_program
        return get_quals_for_loan_program(self)

    def get_absolute_url(self):
        return reverse('view_loan', kwargs={'loan_id': self.pk})

    class Meta:
        app_label = 'loans'

class Lender(TimestampedModel):
    company_name = models.CharField(max_length=500)
    include_states = ChoiceArrayField(USStateField(choices=choices.STATE_CHOICES), default=list)
    company_website = models.URLField(blank=True, null=True)
    company_phone = PhoneNumberField(blank=True, null=True)
    company_fax = PhoneNumberField(blank=True, null=True)
    company_email = models.EmailField(blank=True, null=True)
    company_notes = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'loans'
        ordering = ['company_name']

    def __str__(self):
        return self.company_name
