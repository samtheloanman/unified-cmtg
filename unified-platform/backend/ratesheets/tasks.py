from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .models import RateSheet
from .services.processors.pdf_plumber import PdfPlumberProcessor
from .services.processors.gemini_ai import GeminiAIProcessor
from .services.ingestion import update_pricing_from_extraction
import logging
import traceback

logger = logging.getLogger(__name__)

@shared_task
def process_ratesheet(ratesheet_id):
    """
    Celery task to process an uploaded rate sheet.
    """
    try:
        sheet = RateSheet.objects.get(id=ratesheet_id)
    except RateSheet.DoesNotExist:
        logger.error(f"RateSheet {ratesheet_id} not found.")
        return

    sheet.status = RateSheet.STATUS_PROCESSING
    sheet.log = f"[{timezone.now()}] - Starting processing...\n"
    sheet.save(update_fields=['status', 'log'])
    
    try:
        # Check if Google API key is available for AI processing
        google_api_key = getattr(settings, 'GOOGLE_API_KEY', None)
        use_gemini = google_api_key and sheet.file.name.lower().endswith('.pdf')

        if use_gemini:
            logger.info(f"Using GeminiAIProcessor for RateSheet {ratesheet_id}")
            processor = GeminiAIProcessor(sheet)
            extracted_data = processor.process()

            # Pass extracted data to ingestion service
            ingestion_result = update_pricing_from_extraction(sheet.lender, extracted_data)
            sheet.log += f"[{timezone.now()}] - Gemini AI extraction successful.\n"
            sheet.log += f"[{timezone.now()}] - Ingestion result: {ingestion_result}\n"

        else:
            if not google_api_key:
                logger.info(f"GOOGLE_API_KEY not configured, falling back to PdfPlumberProcessor for RateSheet {ratesheet_id}")
            else:
                logger.info(f"Using PdfPlumberProcessor for RateSheet {ratesheet_id}")

            processor = PdfPlumberProcessor(sheet)
            extracted_data = processor.process()

            # PdfPlumberProcessor already calls update_pricing_from_extraction internally
            # but we log the result here for consistency
            sheet.log += f"[{timezone.now()}] - PdfPlumber processing finished.\n"

        sheet.status = RateSheet.STATUS_PROCESSED
        sheet.processed_at = timezone.now()
        sheet.log += f"[{timezone.now()}] - Processing finished successfully.\n"
        sheet.save()
        
    except Exception as e:
        logger.error(f"Error processing RateSheet {ratesheet_id}: {e}")
        sheet.status = RateSheet.STATUS_FAILED
        sheet.log += f"\n[{timezone.now()}] - CRITICAL ERROR: {str(e)}\n{traceback.format_exc()}"
        sheet.save()
