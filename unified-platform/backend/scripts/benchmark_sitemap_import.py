import time
from unittest.mock import MagicMock, patch
from django.core.management import call_command
from django.db import transaction
from cms.models import ProgramPage, ProgramIndexPage

def generate_sitemap_xml(count=1000):
    xml = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    for i in range(count):
        xml += f'<url><loc>https://custommortgageinc.com/loan-programs/program-{i}</loc></url>'
    xml += '</urlset>'
    return xml.encode('utf-8')

def run_benchmark():
    print("Preparing benchmark...")

    # Mock response
    mock_response = MagicMock()
    mock_response.content = generate_sitemap_xml(count=500)
    mock_response.status_code = 200

    print("Scenario: Re-running import when pages ALREADY exist (Skipping phase)...")

    # We need to setup the DB state first.
    # We will do this inside the atomic block so it all gets rolled back.
    try:
        with transaction.atomic():
            # 1. Setup: Create the pages that match the sitemap
            # We assume the command handles index creation, but we need to run it once to populate.
            # However, running it via command is slow (we know that).
            # Let's cheat and use the command itself to populate, but don't time it.
            print("Populating DB (Setup)...")
            with patch('requests.get', return_value=mock_response):
                with patch('sys.stdout', new=MagicMock()):
                    call_command('import_sitemap', sitemap='programs')

            print("DB Populated. Now measuring the 'Update/Skip' performance...")

            start_time = time.time()
            with patch('requests.get', return_value=mock_response):
                with patch('sys.stdout', new=MagicMock()):
                     call_command('import_sitemap', sitemap='programs')

            end_time = time.time()
            print(f"Time taken (Optimized): {end_time - start_time:.4f} seconds")

            # Rollback to keep DB clean
            raise Exception("Benchmark complete - rolling back")
    except Exception as e:
        if str(e) != "Benchmark complete - rolling back":
            print(f"Error occurred: {e}")
        pass
