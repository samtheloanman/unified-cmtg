from django.test import TestCase
from wagtail.models import Page
from cms.models import (
    ProgramPage, ProgramIndexPage,
    FundedLoanPage, FundedLoanIndexPage,
    BlogPage, BlogIndexPage,
    Office
)
from pricing.models import ProgramType

class ProgramPageTests(TestCase):
    def test_create_program_page(self):
        root = Page.get_first_root_node()
        index = ProgramIndexPage(title="Programs", slug="programs")
        root.add_child(instance=index)

        program_type = ProgramType.objects.create(name="Test Program Type")

        program = ProgramPage(
            title="Test Program",
            slug="test-program",
            program_type="residential",
            linked_program_type=program_type,
            target_city="Los Angeles",
            target_state="CA",
            target_region="SoCal"
        )
        index.add_child(instance=program)

        saved_program = ProgramPage.objects.get(slug="test-program")
        self.assertEqual(saved_program.program_type, "residential")
        self.assertEqual(saved_program.linked_program_type, program_type)
        self.assertEqual(saved_program.target_city, "Los Angeles")

class FundedLoanPageTests(TestCase):
    def test_create_funded_loan_page(self):
        root = Page.get_first_root_node()
        index = FundedLoanIndexPage(title="Funded Loans", slug="funded-loans")
        root.add_child(instance=index)

        loan = FundedLoanPage(
            title="Test Loan",
            slug="test-loan",
            loan_amount=500000,
            location="Miami, FL"
        )
        index.add_child(instance=loan)

        saved_loan = FundedLoanPage.objects.get(slug="test-loan")
        self.assertEqual(saved_loan.loan_amount, 500000)

class BlogPageTests(TestCase):
    def test_create_blog_page(self):
        root = Page.get_first_root_node()
        index = BlogIndexPage(title="Blog", slug="blog")
        root.add_child(instance=index)

        blog = BlogPage(
            title="Test Blog",
            slug="test-blog",
            date="2023-01-01",
            author="John Doe"
        )
        index.add_child(instance=blog)

        saved_blog = BlogPage.objects.get(slug="test-blog")
        self.assertEqual(saved_blog.author, "John Doe")

class OfficeModelTest(TestCase):
    def setUp(self):
        self.hq = Office.objects.create(
            name="HQ",
            city="Encino",
            state="CA",
            latitude=34.154500,
            longitude=-118.495300,
            is_headquarters=True,
            is_active=True
        )
        self.branch = Office.objects.create(
            name="Branch",
            city="San Diego",
            state="CA",
            latitude=32.715700,
            longitude=-117.161100,
            is_headquarters=False,
            is_active=True
        )
        self.closed = Office.objects.create(
            name="Closed",
            city="Nowhere",
            state="ZZ",
            latitude=0,
            longitude=0,
            is_headquarters=False,
            is_active=False
        )

    def test_office_creation(self):
        self.assertEqual(Office.objects.count(), 3)
        self.assertEqual(str(self.hq), "HQ - Encino, CA")

    def test_manager_active(self):
        active_offices = Office.objects.active()
        self.assertEqual(active_offices.count(), 2)
        self.assertIn(self.hq, active_offices)
        self.assertIn(self.branch, active_offices)
        self.assertNotIn(self.closed, active_offices)

    def test_manager_headquarters(self):
        hq = Office.objects.headquarters()
        self.assertEqual(hq, self.hq)
