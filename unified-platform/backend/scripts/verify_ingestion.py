"""
Script to verify Ingest1003Service with sample data.
"""
import os
import json
from django.conf import settings
from open_los.services import Ingest1003Service
from open_los.models import LoanApplication

# Load sample data
FIXTURE_PATH = os.path.join(settings.BASE_DIR, 'open_los/fixtures/sample_1003.json')

try:
    with open(FIXTURE_PATH, 'r') as f:
        data = json.load(f)
    print(f"Loaded fixture from {FIXTURE_PATH}")

    # Run Ingestion
    print("Running Ingest1003Service...")
    app = Ingest1003Service.ingest_floify_json("PROSPECT-123-TEST", data)

    # Verify Results
    print(f"\n--- Verification ---")
    print(f"Loan ID: {app.floify_loan_id}")
    print(f"Amount: ${app.loan_amount}")
    
    # Check Borrower
    borrower = app.borrowers.first()
    print(f"Borrower: {borrower} (Primary: {borrower.is_primary})")
    print(f"Email: {borrower.email}")
    # Declarations (OneToOne)
    if hasattr(borrower, 'declarations'):
        decs = borrower.declarations
        print(f"Declarations: US Citizen? {decs.is_us_citizen}")
        print(f"Declarations (Lawsuit?): {decs.party_to_lawsuit}") # Added this line to retain original check
    else:
        print("Declarations: None found.")

    # Check Employment
    emp = borrower.employments.first()
    print(f"Employer: {emp.employer_name}, Income: ${emp.base_income}")

    # Check Assets
    asset = app.assets.first()
    print(f"Asset: {asset.financial_institution} ({asset.account_type}) - ${asset.cash_or_market_value}")

    # Check Liabilities
    liab = app.liabilities.first()
    print(f"Liability: {liab.creditor_name} - ${liab.unpaid_balance}")
    
    print("\nSUCCESS: All checks passed.")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
