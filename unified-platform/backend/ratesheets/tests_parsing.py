from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from ratesheets.models import RateSheet
from pricing.models import Lender
from ratesheets.tasks import process_ratesheet
from celery import current_app
import os

class AcraParsingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.lender = Lender.objects.create(company_name="Acra Lending")

    def setUp(self):
        current_app.conf.update(task_always_eager=True)
        # Read real fixture
        fixture_path = "/app/ratesheets/fixtures/acra.pdf"
        with open(fixture_path, "rb") as f:
            content = f.read()
            
        pdf_file = SimpleUploadedFile("acra_sample.pdf", content, content_type="application/pdf")
        
        self.ratesheet = RateSheet.objects.create(
            lender=self.lender,
            name="Acra Test Sheet",
            file=pdf_file
        )

    def test_acra_parsing_logic(self):
        """
        Runs the full pipeline against the real Acra PDF sample.
        """
        process_ratesheet.delay(self.ratesheet.id)
        self.ratesheet.refresh_from_db()
        
        print(f"Log Output:\n{self.ratesheet.log}")
        
        self.assertEqual(self.ratesheet.status, RateSheet.STATUS_PROCESSED)
        # Check logs for extraction success
        self.assertIn("Found Date: 01/09/2026", self.ratesheet.log)
        self.assertIn("Found Potential Pricing Table", self.ratesheet.log)
        self.assertIn("Ingestion Result: Processed Acra Sheet", self.ratesheet.log)
