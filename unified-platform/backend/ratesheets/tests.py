import uuid
from unittest.mock import patch
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from celery import current_app
from pricing.models import Lender
from ratesheets.tasks import process_ratesheet
from ratesheets.models import RateSheet
import os

# --- Model Tests ---
class RateSheetModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.lender = Lender.objects.create(company_name="Test Lender")

    def test_ratesheet_creation(self):
        dummy_file = SimpleUploadedFile("test_sheet.pdf", b"dummy pdf", content_type="application/pdf")
        ratesheet = RateSheet.objects.create(
            lender=self.lender,
            name="January Test Sheet",
            file=dummy_file
        )
        self.assertIsInstance(ratesheet, RateSheet)
        self.assertEqual(ratesheet.lender.company_name, "Test Lender")
        self.assertTrue(ratesheet.file.name.startswith("rate_sheets/"))

    def test_ratesheet_status_default(self):
        dummy_file = SimpleUploadedFile("test_sheet_2.pdf", b"dummy content", content_type="application/pdf")
        ratesheet = RateSheet.objects.create(
            lender=self.lender,
            name="February Test Sheet",
            file=dummy_file
        )
        self.assertEqual(ratesheet.status, RateSheet.STATUS_PENDING)

# --- Task and Integration Tests ---
class RateSheetProcessingTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.lender = Lender.objects.create(company_name="Processing Test Lender")

    def setUp(self):
        current_app.conf.update(task_always_eager=True)
        pdf_content = b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n3 0 obj<</Type/Page/MediaBox[0 0 612 792]>>endobj"
        dummy_file = SimpleUploadedFile("integration_sheet.pdf", pdf_content, content_type="application/pdf")
        self.ratesheet = RateSheet.objects.create(
            lender=self.lender,
            name="Integration Test Sheet",
            file=dummy_file
        )

    @patch('ratesheets.tasks.PdfPlumberProcessor')
    def test_process_ratesheet_success(self, MockProcessor):
        """ Test task success pathway with mocked processor """
        mock_instance = MockProcessor.return_value
        mock_instance.process.return_value = {"status": "success"}

        process_ratesheet.delay(self.ratesheet.id)
        self.ratesheet.refresh_from_db()

        self.assertEqual(self.ratesheet.status, RateSheet.STATUS_PROCESSED)
        self.assertIn("Processing finished successfully", self.ratesheet.log)
        MockProcessor.assert_called_once_with(self.ratesheet)
        mock_instance.process.assert_called_once()

    @patch('ratesheets.tasks.PdfPlumberProcessor')
    def test_process_ratesheet_failure(self, MockProcessor):
        """ Test task failure pathway with mocked processor """
        mock_instance = MockProcessor.return_value
        mock_instance.process.side_effect = Exception("Mocked processing failure")

        process_ratesheet.delay(self.ratesheet.id)
        self.ratesheet.refresh_from_db()

        self.assertEqual(self.ratesheet.status, RateSheet.STATUS_FAILED)
        self.assertIn("CRITICAL ERROR: Mocked processing failure", self.ratesheet.log)
        MockProcessor.assert_called_once_with(self.ratesheet)
        mock_instance.process.assert_called_once()
    
    def tearDown(self):
        if self.ratesheet and self.ratesheet.file:
            if os.path.exists(self.ratesheet.file.path):
                os.remove(self.ratesheet.file.path)