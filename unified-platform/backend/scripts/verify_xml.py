"""
Script to verify MismoXmlService.
"""
import os
from open_los.models import LoanApplication
from open_los.xml_generator import MismoXmlService

def run_verification():
    print("--- Verifying MISMO XML Generator ---")
    
    # 1. Get sample loan (Prioritize Homer Simpson from fixture)
    try:
        app = LoanApplication.objects.get(floify_loan_id='PROSPECT-123-TEST')
    except LoanApplication.DoesNotExist:
        app = LoanApplication.objects.first()

    if not app:
        print("No applications found. Run verify_ingestion.py first.")
        return

    print(f"Generating XML for Loan {app.floify_loan_id}...")
    
    # 2. Generate XML
    xml_output = MismoXmlService.generate_xml(app)
    
    # 3. Print (head)
    print("\n--- XML Output (First 20 lines) ---")
    print("\n".join(xml_output.split('\n')[:20]))
    
    # 4. Save to file
    output_path = f"open_los/output_{app.floify_loan_id}.xml"
    with open(output_path, "w") as f:
        f.write(xml_output)
    
    print(f"\nSaved full XML to {output_path}")

run_verification()
