from open_los.models import LoanApplication, Borrower, EmploymentEntry

# Create Application
app = LoanApplication.objects.create(
    floify_loan_id="TEST-1001",
    loan_amount=500000.00,
    loan_purpose="Purchase",
    property_state="CA"
)
print(f"Created: {app}")

# Create Borrower
bor = Borrower.objects.create(
    application=app,
    first_name="Open",
    last_name="Broker",
    is_primary=True
)
print(f"Created Borrower: {bor}")

# Verify Relationship
assert app.borrowers.count() == 1
print("Relationship Verified")
