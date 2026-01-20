"""
Open Broker LOS - Data Models
Mapping the standard 1003 (UrlA) to a relational database.
"""

from django.db import models
from common.models import TimestampedModel


class LoanApplication(TimestampedModel):
    """
    The aggregate root for a single loan application.
    Corresponds to the 'Loan' container in MISMO 3.4.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('processing', 'Processing'),
        ('underwriting', 'Underwriting'),
    ]

    # Links to other systems
    floify_loan_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # High-level loan info
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=3, null=True, blank=True)
    loan_purpose = models.CharField(max_length=50, blank=True)  # Purchase, Refinance
    property_address = models.TextField(blank=True)
    property_state = models.CharField(max_length=2, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Loan {self.floify_loan_id} - ${self.loan_amount or 0}"


class Borrower(TimestampedModel):
    """
    An individual borrower on the application.
    Section 1: Borrower Information.
    """
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='borrowers')
    
    # 1. Identity
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    suffix = models.CharField(max_length=10, blank=True)
    
    CITIZENSHIP_CHOICES = [
        ('citizen', 'US Citizen'),
        ('permanent_alien', 'Permanent Resident Alien'),
        ('non_permanent_alien', 'Non-Permanent Resident Alien'),
    ]
    citizenship = models.CharField(max_length=50, choices=CITIZENSHIP_CHOICES, blank=True)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    ssn = models.CharField(max_length=11, blank=True)  # Consider encryption
    birth_date = models.DateField(null=True, blank=True)
    
    # 1. Current Address
    current_address_street = models.CharField(max_length=255, blank=True)
    current_address_city = models.CharField(max_length=100, blank=True)
    current_address_state = models.CharField(max_length=2, blank=True)
    current_address_zip = models.CharField(max_length=10, blank=True)
    years_at_current = models.FloatField(default=0)
    
    # Flags
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class EmploymentEntry(TimestampedModel):
    """
    Section 1b: Current Employment / Self-Employment and Income.
    """
    borrower = models.ForeignKey(Borrower, on_delete=models.CASCADE, related_name='employments')
    
    employer_name = models.CharField(max_length=255)
    full_address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    position = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(null=True, blank=True)
    years_on_job = models.FloatField(default=0)
    is_self_employed = models.BooleanField(default=False)
    
    # Monthly Income Breakdown
    base_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    overtime = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.employer_name} ({self.borrower})"


class AssetEntry(TimestampedModel):
    """
    Section 2a: Assets - Bank Accounts, Retirement, etc.
    """
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='assets')
    borrower = models.ForeignKey(Borrower, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    
    ASSET_TYPES = [
        ('Checking', 'Checking Account'),
        ('Savings', 'Savings Account'),
        ('Retirement', 'Retirement Fund'),
        ('Stock', 'Stocks/Bonds'),
        ('Other', 'Other'),
    ]
    
    account_type = models.CharField(max_length=50, choices=ASSET_TYPES)
    financial_institution = models.CharField(max_length=255)
    account_number_last4 = models.CharField(max_length=4, blank=True)
    cash_or_market_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.account_type} - ${self.cash_or_market_value}"


class LiabilityEntry(TimestampedModel):
    """
    Section 2c: Liabilities - Credit Cards, Other Loans.
    """
    application = models.ForeignKey(LoanApplication, on_delete=models.CASCADE, related_name='liabilities')
    borrower = models.ForeignKey(Borrower, on_delete=models.SET_NULL, null=True, blank=True, related_name='liabilities')
    
    LIABILITY_TYPES = [
        ('Revolving', 'Revolving (Credit Card)'),
        ('Installment', 'Installment (Car/Student Loan)'),
        ('Mortgage', 'Mortgage'),
        ('Other', 'Other'),
    ]
    
    liability_type = models.CharField(max_length=50, choices=LIABILITY_TYPES)
    creditor_name = models.CharField(max_length=255)
    account_number_last4 = models.CharField(max_length=4, blank=True)
    
    unpaid_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    to_be_paid_off = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.creditor_name} - ${self.unpaid_balance}"


class Declarations(TimestampedModel):
    """
    Section 5: Declarations (Legal questions a-m).
    Examples: Outstanding judgments, bankruptcy, foreclosure.
    """
    borrower = models.OneToOneField(Borrower, on_delete=models.CASCADE, related_name='declarations')
    
    outstanding_judgments = models.BooleanField(default=False)
    bankruptcy_past_7_years = models.BooleanField(default=False)
    foreclosure_past_7_years = models.BooleanField(default=False)
    party_to_lawsuit = models.BooleanField(default=False)
    
    # ... (There are about 15 of these, keeping it simple for v1)
    
    def __str__(self):
        return f"Declarations for {self.borrower}"
