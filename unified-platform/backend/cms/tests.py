from django.test import TestCase
from wagtail.models import Page
from cms.models import (
    ProgramPage, ProgramIndexPage,
    FundedLoanPage, FundedLoanIndexPage,
    BlogPage, BlogIndexPage
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
