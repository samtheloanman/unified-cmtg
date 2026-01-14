"""
Content Validation Management Command

Validates content migration completeness and generates reports.

Usage:
    python manage.py validate_content --report
    python manage.py validate_content --check-field=mortgage_program_highlights
    python manage.py validate_content --verbose
"""

from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from cms.models import (
    ProgramPage,
    FundedLoanPage,
    LegacyRecreatedPage,
    StandardPage,
    HomePage,
)


class Command(BaseCommand):
    help = 'Validate content migration and generate coverage reports'

    def add_arguments(self, parser):
        parser.add_argument(
            '--report',
            action='store_true',
            help='Generate full migration report'
        )
        parser.add_argument(
            '--check-field',
            type=str,
            help='Check specific field for empty values'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed page-by-page information'
        )
        parser.add_argument(
            '--threshold',
            type=int,
            default=80,
            help='Minimum coverage percentage threshold (default: 80%%)'
        )

    def handle(self, *args, **options):
        if options['report']:
            self._generate_full_report(
                verbose=options['verbose'],
                threshold=options['threshold']
            )
        elif options['check_field']:
            self._check_field(options['check_field'], verbose=options['verbose'])
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Specify --report or --check-field=<field_name>"
                )
            )

    def _generate_full_report(self, verbose=False, threshold=80):
        """Generate comprehensive migration report"""
        self.stdout.write(self.style.HTTP_INFO("\n" + "=" * 70))
        self.stdout.write(self.style.HTTP_INFO("CONTENT MIGRATION VALIDATION REPORT"))
        self.stdout.write(self.style.HTTP_INFO("=" * 70))

        # HomePage
        self._report_homepage()

        # ProgramPages
        self._report_program_pages(verbose, threshold)

        # FundedLoanPages
        self._report_funded_loans(verbose)

        # LegacyRecreatedPages
        self._report_legacy_pages(verbose)

        # StandardPages
        self._report_standard_pages()

        # Overall Summary
        self._report_summary(threshold)

        self.stdout.write(self.style.HTTP_INFO("=" * 70 + "\n"))

    def _report_homepage(self):
        """Report on HomePage"""
        self.stdout.write(self.style.HTTP_INFO("\n1. HOME PAGE"))
        self.stdout.write("-" * 70)

        home = HomePage.objects.first()
        if home:
            self.stdout.write(self.style.SUCCESS(f"✓ Title: {home.title}"))
            if home.hero_title:
                self.stdout.write(f"  Hero Title: {home.hero_title}")
            if home.hero_subtitle:
                self.stdout.write(f"  Hero Subtitle: {home.hero_subtitle[:50]}...")
        else:
            self.stdout.write(self.style.ERROR("✗ HomePage not created"))

    def _report_program_pages(self, verbose, threshold):
        """Report on ProgramPages"""
        self.stdout.write(self.style.HTTP_INFO("\n2. PROGRAM PAGES"))
        self.stdout.write("-" * 70)

        all_programs = ProgramPage.objects.all()
        total = all_programs.count()

        if total == 0:
            self.stdout.write(self.style.ERROR("✗ No ProgramPages found"))
            return

        # Define critical fields
        critical_fields = [
            'mortgage_program_highlights',
            'what_are',
            'benefits_of',
            'how_to_qualify_for',
            'requirements',
            'details_about_mortgage_loan_program',
        ]

        # Count pages with content in each field
        field_stats = {}
        for field in critical_fields:
            filter_args = {f"{field}__isnull": False}
            filter_args2 = {f"{field}__exact": ""}
            count_with_content = all_programs.filter(
                **filter_args
            ).exclude(**filter_args2).count()

            coverage = (count_with_content / total * 100) if total > 0 else 0
            field_stats[field] = {
                'count': count_with_content,
                'coverage': coverage
            }

        # Overall pages with any content
        programs_with_content = all_programs.exclude(
            Q(mortgage_program_highlights__isnull=True) | Q(mortgage_program_highlights__exact="")
        ).count()

        # Display summary
        self.stdout.write(f"Total Pages: {total}")
        self.stdout.write(f"With Content: {programs_with_content}")
        self.stdout.write(f"Empty: {total - programs_with_content}\n")

        # Field-by-field coverage
        self.stdout.write("Field Coverage:")
        for field, stats in field_stats.items():
            coverage = stats['coverage']
            if coverage >= threshold:
                style = self.style.SUCCESS
                symbol = "✓"
            elif coverage >= 50:
                style = self.style.WARNING
                symbol = "⚠"
            else:
                style = self.style.ERROR
                symbol = "✗"

            self.stdout.write(
                f"  {symbol} {field:40} {stats['count']:3}/{total:3} ({coverage:5.1f}%)"
            )

        # Verbose: List empty pages
        if verbose:
            empty_programs = all_programs.filter(
                Q(mortgage_program_highlights__isnull=True) | Q(mortgage_program_highlights__exact="")
            )
            if empty_programs.exists():
                self.stdout.write(self.style.WARNING("\nEmpty Program Pages:"))
                for page in empty_programs:
                    self.stdout.write(f"  - {page.title} (ID: {page.id})")

    def _report_funded_loans(self, verbose):
        """Report on FundedLoanPages"""
        self.stdout.write(self.style.HTTP_INFO("\n3. FUNDED LOAN PAGES"))
        self.stdout.write("-" * 70)

        funded = FundedLoanPage.objects.all()
        total = funded.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("⚠ No FundedLoanPages found"))
            return

        with_description = funded.exclude(
            Q(description__isnull=True) | Q(description__exact="")
        ).count()

        self.stdout.write(f"Total Pages: {total}")
        self.stdout.write(f"With Description: {with_description}")
        self.stdout.write(f"Empty: {total - with_description}")

        if verbose and total > 0:
            self.stdout.write(f"\nFunded Loan Pages:")
            for page in funded[:10]:  # Show first 10
                status = "✓" if page.description else "✗"
                self.stdout.write(f"  {status} {page.title} (ID: {page.id})")
            if total > 10:
                self.stdout.write(f"  ... and {total - 10} more")

    def _report_legacy_pages(self, verbose):
        """Report on LegacyRecreatedPages"""
        self.stdout.write(self.style.HTTP_INFO("\n4. LEGACY RECREATED PAGES"))
        self.stdout.write("-" * 70)

        legacy = LegacyRecreatedPage.objects.all()
        total = legacy.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("⚠ No LegacyRecreatedPages found"))
            return

        with_body = legacy.exclude(
            Q(body__isnull=True) | Q(body__exact="")
        ).count()

        self.stdout.write(f"Total Pages: {total}")
        self.stdout.write(f"With Body: {with_body}")
        self.stdout.write(f"Empty: {total - with_body}")

        if verbose and total > 0:
            self.stdout.write(f"\nLegacy Pages (sample):")
            for page in legacy[:10]:
                status = "✓" if page.body else "✗"
                self.stdout.write(f"  {status} {page.title} (ID: {page.id})")
            if total > 10:
                self.stdout.write(f"  ... and {total - 10} more")

    def _report_standard_pages(self):
        """Report on StandardPages"""
        self.stdout.write(self.style.HTTP_INFO("\n5. STANDARD PAGES"))
        self.stdout.write("-" * 70)

        standard = StandardPage.objects.all()
        total = standard.count()

        if total == 0:
            self.stdout.write(self.style.WARNING("⚠ No StandardPages found"))
            return

        with_body = standard.exclude(
            Q(body__isnull=True) | Q(body__exact="")
        ).count()

        self.stdout.write(f"Total Pages: {total}")
        self.stdout.write(f"With Body: {with_body}")
        self.stdout.write(f"Empty: {total - with_body}")

    def _report_summary(self, threshold):
        """Report overall summary"""
        self.stdout.write(self.style.HTTP_INFO("\n6. OVERALL SUMMARY"))
        self.stdout.write("-" * 70)

        # Count all pages
        program_count = ProgramPage.objects.count()
        funded_count = FundedLoanPage.objects.count()
        legacy_count = LegacyRecreatedPage.objects.count()
        standard_count = StandardPage.objects.count()
        total_count = program_count + funded_count + legacy_count + standard_count

        self.stdout.write(f"Total Pages Imported: {total_count}")
        self.stdout.write(f"  - Program Pages: {program_count}")
        self.stdout.write(f"  - Funded Loan Pages: {funded_count}")
        self.stdout.write(f"  - Legacy Pages: {legacy_count}")
        self.stdout.write(f"  - Standard Pages: {standard_count}")

        # Check if we meet threshold
        if program_count > 0:
            programs_with_content = ProgramPage.objects.exclude(
                Q(mortgage_program_highlights__isnull=True) | Q(mortgage_program_highlights__exact="")
            ).count()
            coverage = (programs_with_content / program_count * 100)

            self.stdout.write(f"\nProgram Page Content Coverage: {coverage:.1f}%")

            if coverage >= threshold:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Meets {threshold}% threshold")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ Below {threshold}% threshold")
                )

    def _check_field(self, field_name, verbose):
        """Check specific field for empty values"""
        self.stdout.write(f"\nChecking field: {field_name}\n")
        self.stdout.write("-" * 70)

        # Try to find field in ProgramPage
        if hasattr(ProgramPage, field_name):
            all_programs = ProgramPage.objects.all()
            total = all_programs.count()

            filter_args = {f"{field_name}__isnull": False}
            filter_args2 = {f"{field_name}__exact": ""}
            with_content = all_programs.filter(**filter_args).exclude(**filter_args2).count()
            empty = total - with_content

            self.stdout.write(f"ProgramPage.{field_name}:")
            self.stdout.write(f"  Total: {total}")
            self.stdout.write(f"  With Content: {with_content}")
            self.stdout.write(f"  Empty: {empty}")

            if verbose:
                empty_pages = all_programs.filter(
                    Q(**{f"{field_name}__isnull": True}) | Q(**{f"{field_name}__exact": ""})
                )
                if empty_pages.exists():
                    self.stdout.write(f"\nEmpty pages:")
                    for page in empty_pages:
                        self.stdout.write(f"  - {page.title} (ID: {page.id})")
        else:
            self.stdout.write(
                self.style.ERROR(f"Field '{field_name}' not found in ProgramPage")
            )
