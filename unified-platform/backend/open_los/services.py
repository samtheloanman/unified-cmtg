"""
Open Broker LOS - Ingestion Service
Handles parsing of 1003 JSON data (Floify or MISMO) into relational models.
"""

import logging
from django.db import transaction
from .models import (
    LoanApplication, 
    Borrower, 
    EmploymentEntry, 
    AssetEntry, 
    LiabilityEntry, 
    Declarations
)

logger = logging.getLogger(__name__)


class Ingest1003Service:
    """
    Service to convert 1003 JSON blob into relational database records.
    """

    @staticmethod
    @transaction.atomic
    def ingest_floify_json(floify_loan_id: str, json_data: dict) -> LoanApplication:
        """
        Main entry point.
        Takes full 1003 JSON from Floify and creates/updates a LoanApplication.
        """
        logger.info(f"Ingesting 1003 for Loan {floify_loan_id}")
        
        # 1. Create/Update Root Application
        # Handle simple property address structure or more complex one if needed
        prop_addr = json_data.get('subjectPropertyAddress', {})
        
        app, created = LoanApplication.objects.update_or_create(
            floify_loan_id=floify_loan_id,
            defaults={
                'loan_amount': json_data.get('loanAmount'),
                'loan_purpose': json_data.get('loanPurpose', 'Purchase'),
                'property_address': prop_addr.get('street', ''),
                'property_state': prop_addr.get('state', ''),
            }
        )
        
        # 2. Clear old data (simple full refresh strategy for v0.1)
        if not created:
            # Cascade delete should handle children if configured, but being explicit is safer
            # assuming on_delete=CASCADE in models
            app.borrowers.all().delete()
            # Asset/Liabilities are linked to Application OR Borrower. 
            # If linked to Application directly, we must clear them.
            app.assets.all().delete()
            app.liabilities.all().delete()

        # 3. Process Applications Array (MISMO has 'applications', usually one per borrower pair)
        applications = json_data.get('applications', [])
        
        for idx, app_data in enumerate(applications):
            # Borrower
            borrower_data = app_data.get('borrower', {})
            if borrower_data:
                # First borrower in first application is usually primary
                is_primary = (idx == 0)
                borrower = Ingest1003Service._create_borrower(app, borrower_data, is_primary)
                
                # Co-Borrower
                co_borrower_data = app_data.get('coborrower', {})
                if co_borrower_data:
                    Ingest1003Service._create_borrower(app, co_borrower_data, is_primary=False)

        logger.info(f"Successfully ingested Loan {floify_loan_id} (ID: {app.id})")
        return app

    @staticmethod
    def _create_borrower(app: LoanApplication, data: dict, is_primary: bool) -> Borrower:
        """Create a single borrower and their related records."""
        curr_addr = data.get('currentAddress', {})
        
        # New Floify Apply Now 3.0 Schema Handling
        # Structure: borrower -> personalInfo -> legalFullName -> firstName
        personal_info = data.get('personalInfo', {})
        full_name = personal_info.get('legalFullName', {})
        
        # Fallback to old flat structure if nested not found (backward compatibility)
        if not full_name and 'firstName' in data:
             full_name = data  # Treat the root data as the name container
             
        # Citizenship
        citizenship = personal_info.get('citizenship', '')
        
        borrower = Borrower.objects.create(
            application=app,
            first_name=full_name.get('firstName', ''),
            middle_name=full_name.get('middleName', ''),
            last_name=full_name.get('lastName', ''),
            suffix=full_name.get('suffix', ''),
            citizenship=citizenship,
            email=personal_info.get('email', data.get('email', '')), # email also moved to personalInfo
            phone=data.get('mobilePhoneNumber', ''),
            ssn=data.get('ssn', ''),
            birth_date=personal_info.get('dateOfBirth', data.get('birthDate')), # DOB moved too
            current_address_street=curr_addr.get('street', ''),
            current_address_city=curr_addr.get('city', ''),
            current_address_state=curr_addr.get('state', ''),
            current_address_zip=curr_addr.get('zip', ''),
            is_primary=is_primary
        )

        # Employment
        for emp in data.get('employment', []):
            EmploymentEntry.objects.create(
                borrower=borrower,
                employer_name=emp.get('employerName', ''),
                position=emp.get('jobTitle', ''),
                start_date=emp.get('startDate'),
                years_on_job=emp.get('yearsOnJob', 0),
                base_income=emp.get('baseIncome', 0)
            )
            
        # Assets (Linked to Borrower for now, can be joint)
        for asset in data.get('assets', []):
            AssetEntry.objects.create(
                application=app,
                borrower=borrower,
                account_type=asset.get('type', 'Other'),
                financial_institution=asset.get('institutionName', ''),
                cash_or_market_value=asset.get('value', 0)
            )

        # Liabilities
        for liab in data.get('liabilities', []):
            LiabilityEntry.objects.create(
                application=app,
                borrower=borrower,
                liability_type=liab.get('type', 'Other'),
                creditor_name=liab.get('creditorName', ''),
                unpaid_balance=liab.get('unpaidBalance', 0),
                monthly_payment=liab.get('monthlyPayment', 0)
            )
            
        # Declarations
        decs = data.get('declarations', {})
        if decs:
            Declarations.objects.create(
                borrower=borrower,
                outstanding_judgments=decs.get('outstandingJudgments', False),
                bankruptcy_past_7_years=decs.get('bankruptcy', False),
                foreclosure_past_7_years=decs.get('foreclosure', False),
                party_to_lawsuit=decs.get('partyToLawsuit', False)
            )
            
        return borrower
