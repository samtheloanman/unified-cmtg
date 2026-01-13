from celery import shared_task
from django.utils import timezone
import traceback

@shared_task
def process_ratesheet(ratesheet_id):
    from .models import RateSheet

    try:
        rs = RateSheet.objects.get(id=ratesheet_id)
        rs.status = 'PROCESSING'
        rs.save()

        # Placeholder for actual processing logic (Phase 4.4)
        # processor = RateSheetProcessor(rs.file.path)
        # processor.process()

        # Simulate work
        import time
        time.sleep(2)

        rs.status = 'PROCESSED'
        rs.processed_at = timezone.now()
        rs.save()

    except Exception as e:
        if 'rs' in locals():
            rs.status = 'FAILED'
            rs.log = traceback.format_exc()
            rs.save()
        raise e
