"""
Script to simulate Floify Webhook and verify Open LOS integration.
Mocks the external Floify API calls.
"""
import os
import django
from unittest.mock import MagicMock, patch
from rest_framework.test import APIRequestFactory

# Must setup Django if running standalone script, but we run via 'manage.py shell', so it is fine.
from api.views import floify_webhook
from open_los.models import LoanApplication, Borrower

def run_simulation():
    print("--- Simulating Floify Webhook ---")
    
    factory = APIRequestFactory()
    floify_id = 'PROSPECT-SIM-001'
    loan_id = 'LOAN-SIM-001'
    
    # 1. Prepare Request
    payload = {
        'event': 'application.created',
        'payload': {'id': floify_id, 'loanId': loan_id}
    }
    request = factory.post('/api/v1/webhooks/floify/', payload, format='json')
    
    # 2. Mock FloifyClient
    with patch('api.views.FloifyClient') as MockClient:
        instance = MockClient.return_value
        instance.__enter__.return_value = instance
        
        # Mock Response for get_application (Standard App Sync)
        instance.get_application.return_value = {
            'id': floify_id,
            'loanId': loan_id,
            'email': 'simulation@example.com',
            'firstName': 'Sim',
            'lastName': 'User',
            'loanAmount': 600000,
            'subjectPropertyAddress': '100 Mockingbird Ln',
            'loanPurpose': 'Purchase'
        }
        
        # Mock Response for get_1003_json (Open LOS Ingest)
        instance.get_1003_json.return_value = {
            'loanAmount': 600000,
            'loanPurpose': 'Purchase',
            'subjectPropertyAddress': {'street': '100 Mockingbird Ln', 'state': 'NY'},
            'applications': [
                {
                    'borrower': {
                        'firstName': 'Sim',
                        'lastName': 'User', 
                        'email': 'simulation@example.com',
                        'employment': [
                            {'employerName': 'Simulation Inc', 'baseIncome': 9000}
                        ]
                    }
                }
            ]
        }
        
        # 3. Execute View
        print("Executing webhook view...")
        response = floify_webhook(request)
        print(f"View Response: {response.status_code}")
        
    # 4. Verify Database
    print("\n--- Verifying Database ---")
    
    # Check Application (Standard)
    from applications.models import Application
    std_app = Application.objects.get(floify_id=floify_id)
    print(f"Standard App Created: {std_app} (Status: {std_app.status})")
    
    # Check Open LOS (New)
    try:
        los_app = LoanApplication.objects.get(floify_loan_id=loan_id)
        print(f"Open LOS App Created: {los_app}")
        print(f"  - Amount: ${los_app.loan_amount}")
        print(f"  - State: {los_app.property_state}")
        
        bor = los_app.borrowers.first()
        print(f"  - Borrower: {bor}")
        
        emp = bor.employments.first()
        print(f"  - Employer: {emp.employer_name}")
        
        print("\nSUCCESS: Webhook triggered full 1003 ingestion!")
        
    except LoanApplication.DoesNotExist:
        print("\nFAILURE: Open LOS Application not found.")

run_simulation()
