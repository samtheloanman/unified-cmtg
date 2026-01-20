"""
Script to verify Open LOS API Endpoints.
"""
import os
import json
from rest_framework.test import APIClient, APIRequestFactory
from django.contrib.auth import get_user_model
from open_los.models import LoanApplication

User = get_user_model()

def run_verification():
    print("--- Verifying Open LOS API ---")
    
    # 1. Setup Data
    # Ensure we have at least one application (from previous tasks)
    if LoanApplication.objects.count() == 0:
        print("No applications found. Please run verify_ingestion.py first.")
        return

    # 2. Setup Client & Auth
    client = APIClient()
    # Create test user for auth (API is permission protected)
    user, created = User.objects.get_or_create(username='api_tester_bot')
    if created:
        user.set_password('testpass')
        user.save()
    client.force_authenticate(user=user)
    
    # 3. Test List Endpoint
    print("\nTesting GET /api/v1/open-los/loans/")
    response = client.get('/api/v1/open-los/loans/')
    
    if response.status_code == 200:
        data = response.json()
        
        results = []
        if isinstance(data, list):
            print(f"Success! Found {len(data)} loans (Unpaginated).")
            results = data
        else:
            print(f"Success! Found {data.get('count')} loans (Paginated).")
            results = data.get('results', [])

        if results:
            loan = results[0]
            print(f"Sample Loan: {loan.get('floify_loan_id')} - ${loan.get('loan_amount')}")
            print(f"Borrowers: {len(loan.get('borrowers', []))}")
            print(f"Assets: {len(loan.get('assets', []))}")
    else:
        print(f"FAILED: Status {response.status_code}")
        print(response.content)

    # 4. Test Single Endpoint
    if response.status_code == 200 and results:
        loan_id = results[0]['id']
        print(f"\nTesting GET /api/v1/open-los/loans/{loan_id}/")
        
        detail_response = client.get(f'/api/v1/open-los/loans/{loan_id}/')
        if detail_response.status_code == 200:
             detail = detail_response.json()
             print(f"Success! Detail View retrieved for {detail['floify_loan_id']}")
        else:
            print(f"FAILED Detail: {detail_response.status_code}")

run_verification()
