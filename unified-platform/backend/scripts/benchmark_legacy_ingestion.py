import os
import sys
import time
import json
import logging
import random
import django
from decimal import Decimal

# Setup Django Environment
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.db import transaction
from ratesheets.services.ingestion import update_pricing_from_extraction
from pricing.models import Lender, RateAdjustment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Suppress django db logs to avoid noise
logging.getLogger('django.db.backends').setLevel(logging.WARNING)

def generate_legacy_data(num_programs=10, adjustments_per_program=100):
    """
    Generates a legacy JSON string payload.
    """
    data = []
    for p_idx in range(num_programs):
        program_name = f"Benchmark Program {p_idx}"
        for a_idx in range(adjustments_per_program):
            adjustment = {
                "program_name": program_name,
                "min_fico": random.randint(600, 800),
                "max_fico": random.randint(600, 800) + 20,
                "min_ltv": random.randint(60, 90),
                "max_ltv": random.randint(60, 90) + 5,
                "adjustment": round(random.uniform(-2.0, 2.0), 3)
            }
            data.append(adjustment)
    return json.dumps(data)

def run_benchmark():
    print("--- Starting Benchmark for Legacy Ingestion ---")

    # Setup Lender
    lender, _ = Lender.objects.get_or_create(company_name="Benchmark Lender")

    # Generate Payload
    # 50 programs * 200 adjustments = 10,000 creates
    num_programs = 50
    adjustments_per_program = 200
    payload = generate_legacy_data(num_programs, adjustments_per_program)
    total_records = num_programs * adjustments_per_program
    print(f"Generated payload with {total_records} records.")

    # Warmup / Cleanup
    RateAdjustment.objects.filter(offering__lender=lender).delete()

    # Measure Baseline
    start_time = time.time()
    # We rely on the fact that update_pricing_from_extraction calls _handle_legacy_format
    # when passed a string.
    update_pricing_from_extraction(lender, payload)
    end_time = time.time()

    duration = end_time - start_time
    print(f"Ingestion took {duration:.4f} seconds for {total_records} records.")
    print(f"Rate: {total_records / duration:.2f} records/sec")

    # Verification
    count = RateAdjustment.objects.filter(offering__lender=lender).count()
    print(f"Verified RateAdjustments in DB: {count}")

    # Cleanup
    # RateAdjustment.objects.filter(offering__lender=lender).delete()
    # lender.delete()

if __name__ == "__main__":
    try:
        run_benchmark()
    except Exception as e:
        print(f"Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
