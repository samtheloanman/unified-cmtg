from celery import shared_task
from django.utils import timezone
from .models import RateSheet
from .services.processors.pdf_plumber import PdfPlumberProcessor
import logging
import traceback

logger = logging.getLogger(__name__)

@shared_task
def process_ratesheet(ratesheet_id):
    """
    Celery task to process a uploaded rate sheet.
    """
    try:
        sheet = RateSheet.objects.get(id=ratesheet_id)
    except RateSheet.DoesNotExist:
        logger.error(f"RateSheet {ratesheet_id} not found.")
        return

    sheet.status = RateSheet.STATUS_PROCESSING
    sheet.save(update_fields=['status'])
    
    try:
        # Determine processor based on file extension (naive implementation)
        # For now, default to PdfPlumberProcessor
        processor = PdfPlumberProcessor(sheet)
        result = processor.process()
        
        sheet.status = RateSheet.STATUS_PROCESSED
        sheet.processed_at = timezone.now()
        sheet.log += f"\nProcessing finished successfully. Result: {result}"
        sheet.save()
        
    except Exception as e:
        logger.error(f"Error processing RateSheet {ratesheet_id}: {e}")
        sheet.status = RateSheet.STATUS_FAILED
        sheet.log += f"\nCRITICAL ERROR: {str(e)}\n{traceback.format_exc()}"
        sheet.save()
