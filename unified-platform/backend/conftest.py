"""
Pytest configuration and fixtures for unified-cmtg backend tests
"""
import pytest
from django.conf import settings
from django.test import Client
from wagtail.models import Site, Page
from cms.models import HomePage, ProgramIndexPage, ProgramPage


@pytest.fixture
def client():
    """Django test client"""
    return Client()


@pytest.fixture
def api_client():
    """API client for testing REST endpoints"""
    return Client()


@pytest.fixture
def site(db):
    """Get the default Wagtail site"""
    return Site.objects.get(is_default_site=True)


@pytest.fixture
def home_page(site):
    """Get the site's home page"""
    return site.root_page.specific


@pytest.fixture
def program_index(home_page):
    """Get or create ProgramIndexPage"""
    program_index = ProgramIndexPage.objects.child_of(home_page).first()
    if not program_index:
        program_index = ProgramIndexPage(title="Loan Programs", slug="programs")
        home_page.add_child(instance=program_index)
        program_index.save_revision().publish()
    return program_index


@pytest.fixture
def sample_program(program_index):
    """Create a sample ProgramPage for testing"""
    program = ProgramPage(
        title="Test FHA Loan Program",
        slug="test-fha-loan",
        program_type="residential",
        minimum_loan_amount="100000",
        maximum_loan_amount="5000000",
        min_credit_score=580,
        max_ltv="96.5%",
        interest_rates="5.5% - 7.5%",
        property_types=["Single Family", "Condo", "Townhouse"],
        occupancy_types=["Primary Residence", "Second Home"],
        mortgage_program_highlights="Great for first-time buyers",
        what_are="FHA loans are government-backed mortgages",
        benefits_of="Low down payment, flexible credit requirements",
        requirements="Valid SSN, 2 years employment history",
    )
    program_index.add_child(instance=program)
    program.save_revision().publish()
    return program


@pytest.fixture
def enable_db_access_for_all_tests(db):
    """
    Automatically enable database access for all tests.
    Remove this if you want to explicitly mark tests that need DB access.
    """
    pass
