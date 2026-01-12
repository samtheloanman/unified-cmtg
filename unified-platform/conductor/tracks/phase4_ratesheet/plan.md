# Phase 4: Rate Sheet Agent

> **Goal**: Automate the ingestion and parsing of lender rate sheets (PDF/Excel) into structured data for the pricing engine. Human-in-the-loop approval required.

---

## 📋 Task Breakdown

### Task 4.1: Build CSV Reader for Lender List

**Agent**: Rate Sheet Agent  
**Priority**: P0 - Critical  
**Estimated Time**: 1-2 hours

#### Context
The file `Ratesheet List - Ratesheets.csv` contains lender names, URLs, and access information. This is the source of truth for which rate sheets to fetch.

#### CSV Structure
```csv
Lender,Emailed,PW,Type,Ratesheet Link
Acra Non Prime,N,none,NonQM,https://acralending.com/.../acra-ws-ratematrix-1stTDs.pdf
BluePoint,Y,password123,Agency,https://bluepoint.com/rates.pdf
...
```

#### Instructions

1. **Create the rate sheet ingestion module**
   ```python
   # ratesheets/ingestion/csv_reader.py
   
   import csv
   from dataclasses import dataclass
   from pathlib import Path
   from typing import List, Optional
   
   @dataclass
   class LenderRateSheetConfig:
       """Configuration for a lender's rate sheet source."""
       lender_name: str
       url: str
       program_type: str
       requires_auth: bool = False
       password: Optional[str] = None
       is_emailed: bool = False
   
   class RateSheetCSVReader:
       """
       Read lender rate sheet configuration from CSV.
       
       Expected columns:
       - Lender: Lender name (must match Lender.company_name)
       - Emailed: Y/N - whether rate sheet comes via email
       - PW: Password if auth required, 'none' otherwise
       - Type: Program type (NonQM, Agency, HardMoney)
       - Ratesheet Link: URL to PDF
       """
       
       def __init__(self, csv_path: Path):
           self.csv_path = csv_path
       
       def read_all(self) -> List[LenderRateSheetConfig]:
           """Read all lender configurations."""
           configs = []
           
           with open(self.csv_path, newline='') as f:
               reader = csv.DictReader(f)
               
               for row in reader:
                   config = LenderRateSheetConfig(
                       lender_name=row['Lender'].strip(),
                       url=row['Ratesheet Link'].strip(),
                       program_type=row['Type'].strip(),
                       requires_auth=row['PW'].lower() not in ('none', '', 'n/a'),
                       password=row['PW'] if row['PW'].lower() not in ('none', '', 'n/a') else None,
                       is_emailed=row['Emailed'].upper() == 'Y',
                   )
                   configs.append(config)
           
           return configs
       
       def read_web_sources(self) -> List[LenderRateSheetConfig]:
           """Get only lenders with web-based rate sheets."""
           return [c for c in self.read_all() if not c.is_emailed and c.url]
       
       def read_email_sources(self) -> List[LenderRateSheetConfig]:
           """Get only lenders that email rate sheets."""
           return [c for c in self.read_all() if c.is_emailed]
   
   
   # Usage
   if __name__ == '__main__':
       reader = RateSheetCSVReader(Path('Ratesheet List - Ratesheets.csv'))
       for config in reader.read_web_sources():
           print(f"{config.lender_name}: {config.url}")
   ```

2. **Test with the actual CSV**
   ```bash
   cd ~/code/unified-cmtg
   python -c "
   from unified-platform.backend.ratesheets.ingestion.csv_reader import RateSheetCSVReader
   from pathlib import Path
   
   reader = RateSheetCSVReader(Path('Ratesheet List - Ratesheets.csv'))
   configs = reader.read_all()
   print(f'Found {len(configs)} lenders')
   "
   ```

#### Success Criteria
- [ ] CSV reader parses all rows correctly
- [ ] Handles edge cases (empty values, special characters)
- [ ] Separates web vs email sources
- [ ] Returns typed dataclass objects

---

### Task 4.2: Build PDF Downloader

**Agent**: Rate Sheet Agent  
**Priority**: P0 - Critical  
**Estimated Time**: 2-3 hours

#### Context
Most rate sheets are PDFs hosted on lender websites. Some require authentication. We need a robust downloader that handles both cases.

#### Instructions

1. **Create the PDF downloader**
   ```python
   # ratesheets/ingestion/downloader.py
   
   import httpx
   from pathlib import Path
   from datetime import datetime
   import hashlib
   from typing import Optional
   import logging
   
   logger = logging.getLogger(__name__)
   
   class RateSheetDownloader:
       """
       Download rate sheet PDFs from lender websites.
       
       Features:
       - Handles basic auth and custom headers
       - Caches downloads to avoid duplicates
       - Uses httpx for async support (future)
       """
       
       def __init__(self, cache_dir: Path):
           self.cache_dir = cache_dir
           self.cache_dir.mkdir(parents=True, exist_ok=True)
           self.client = httpx.Client(
               timeout=30.0,
               follow_redirects=True,
               headers={
                   'User-Agent': 'Mozilla/5.0 (compatible; RateSheetBot/1.0)'
               }
           )
       
       def download(
           self,
           url: str,
           lender_name: str,
           password: Optional[str] = None
       ) -> Optional[Path]:
           """
           Download a rate sheet PDF.
           
           Args:
               url: URL to the PDF
               lender_name: For naming the cached file
               password: Optional password for basic auth
           
           Returns:
               Path to downloaded file, or None if failed
           """
           try:
               # Build request
               auth = None
               if password:
                   # Assume basic auth with lender name as username
                   auth = (lender_name.lower().replace(' ', ''), password)
               
               response = self.client.get(url, auth=auth)
               response.raise_for_status()
               
               # Verify it's a PDF
               content_type = response.headers.get('content-type', '')
               if 'pdf' not in content_type.lower() and not url.endswith('.pdf'):
                   logger.warning(f"Not a PDF: {url} ({content_type})")
                   # Continue anyway, might still be valid
               
               # Generate filename
               date_str = datetime.now().strftime('%Y-%m-%d')
               safe_name = lender_name.lower().replace(' ', '_')
               filename = f"{safe_name}_{date_str}.pdf"
               filepath = self.cache_dir / filename
               
               # Check if content has changed (hash comparison)
               content_hash = hashlib.md5(response.content).hexdigest()
               hash_file = filepath.with_suffix('.hash')
               
               if hash_file.exists():
                   existing_hash = hash_file.read_text().strip()
                   if existing_hash == content_hash:
                       logger.info(f"No changes for {lender_name}")
                       return filepath
               
               # Save the PDF
               filepath.write_bytes(response.content)
               hash_file.write_text(content_hash)
               
               logger.info(f"Downloaded: {filepath}")
               return filepath
               
           except httpx.HTTPError as e:
               logger.error(f"Failed to download {url}: {e}")
               return None
       
       def download_all(self, configs: list) -> dict:
           """Download rate sheets for all configured lenders."""
           results = {}
           
           for config in configs:
               path = self.download(
                   url=config.url,
                   lender_name=config.lender_name,
                   password=config.password
               )
               results[config.lender_name] = path
           
           return results
   ```

2. **Test the downloader**
   ```bash
   python -c "
   from ratesheets.ingestion.downloader import RateSheetDownloader
   from pathlib import Path
   
   downloader = RateSheetDownloader(Path('./ratesheet_cache'))
   path = downloader.download(
       'https://acralending.com/wp-content/uploads/2024/01/acra-ws-ratematrix-1stTDs.pdf',
       'Acra Lending'
   )
   print(f'Downloaded to: {path}')
   "
   ```

#### Success Criteria
- [ ] Downloads PDFs successfully
- [ ] Handles authentication
- [ ] Caches to avoid re-downloads
- [ ] Detects when content hasn't changed

---

### Task 4.3: Connect LLM for PDF Extraction

**Agent**: Rate Sheet Agent  
**Priority**: P0 - Critical  
**Estimated Time**: 4-5 hours

#### Context
Rate sheets are complex PDFs with tables, grids, and varying layouts. We'll use Gemini 1.5 Pro with vision capabilities to extract structured data.

#### Instructions

1. **Create the extraction pipeline**
   ```python
   # ratesheets/extraction/llm_extractor.py
   
   import google.generativeai as genai
   from pathlib import Path
   import json
   from typing import Optional
   import logging
   
   logger = logging.getLogger(__name__)
   
   # Configure Gemini
   genai.configure(api_key=os.environ['GEMINI_API_KEY'])
   
   EXTRACTION_PROMPT = '''
   You are a mortgage rate sheet parser. Extract the following data from this rate sheet PDF:
   
   1. **Lender Information**
      - Lender name
      - Effective date
      - Expiration date (if shown)
   
   2. **Base Rate Matrix**
      Extract the rate/price grid. For each rate offered:
      - Interest rate (e.g., 7.000%)
      - Price for 15-day lock
      - Price for 30-day lock
      - Price for 45-day lock
      - Price for 60-day lock
   
   3. **LLPA Adjustments**
      Extract all adjustment grids:
      
      a) FICO × LTV Grid (2D matrix)
         - Row: FICO score range (e.g., 720-739)
         - Column: LTV range (e.g., 70.01-75%)
         - Value: Points adjustment (e.g., -0.625)
      
      b) Loan Purpose Adjustments (1D)
         - Purchase: adjustment
         - Rate/Term Refinance: adjustment
         - Cash-Out Refinance: adjustment
      
      c) Property Type Adjustments (1D)
         - SFR: adjustment
         - Condo: adjustment
         - 2-4 Unit: adjustment
      
      d) Occupancy Adjustments (1D)
         - Owner Occupied: adjustment
         - Second Home: adjustment
         - Investment: adjustment
   
   Return the data as a JSON object with this structure:
   {
     "lender_name": "...",
     "effective_date": "YYYY-MM-DD",
     "expiry_date": "YYYY-MM-DD or null",
     "base_rates": [
       {"rate": 7.000, "price_15": 100.25, "price_30": 100.00, ...}
     ],
     "adjustments": {
       "fico_ltv": [
         {"fico_min": 720, "fico_max": 739, "ltv_min": 70.01, "ltv_max": 75.00, "adjustment": -0.625}
       ],
       "purpose": [
         {"value": "purchase", "adjustment": 0.0},
         {"value": "cash_out", "adjustment": -0.50}
       ],
       "property_type": [...],
       "occupancy": [...]
     }
   }
   
   Be precise with numbers. Use negative values for costs (borrower pays more).
   If a section is not present in the rate sheet, use an empty array.
   '''
   
   class LLMRateSheetExtractor:
       """Extract structured rate data from PDF using Gemini Vision."""
       
       def __init__(self):
           self.model = genai.GenerativeModel('gemini-1.5-pro')
       
       def extract(self, pdf_path: Path) -> Optional[dict]:
           """
           Extract rate data from a PDF.
           
           Args:
               pdf_path: Path to the rate sheet PDF
           
           Returns:
               Parsed rate data as dict, or None if extraction failed
           """
           try:
               # Upload the PDF
               pdf_file = genai.upload_file(str(pdf_path))
               
               # Generate extraction
               response = self.model.generate_content([
                   EXTRACTION_PROMPT,
                   pdf_file
               ])
               
               # Parse JSON from response
               text = response.text
               
               # Find JSON in response (may be wrapped in markdown)
               if '```json' in text:
                   text = text.split('```json')[1].split('```')[0]
               elif '```' in text:
                   text = text.split('```')[1].split('```')[0]
               
               data = json.loads(text.strip())
               
               # Validate structure
               self._validate(data)
               
               return data
               
           except Exception as e:
               logger.error(f"Extraction failed for {pdf_path}: {e}")
               return None
       
       def _validate(self, data: dict):
           """Validate extracted data has required fields."""
           required = ['lender_name', 'base_rates', 'adjustments']
           for field in required:
               if field not in data:
                   raise ValueError(f"Missing required field: {field}")
   ```

2. **Test with sample rate sheets**
   ```bash
   cd ~/code/unified-cmtg
   python -c "
   from ratesheets.extraction.llm_extractor import LLMRateSheetExtractor
   from pathlib import Path
   
   extractor = LLMRateSheetExtractor()
   data = extractor.extract(Path('Ratesheet-samples/acra-ws-ratematrix-1stTDs.pdf'))
   print(json.dumps(data, indent=2))
   "
   ```

#### Success Criteria
- [ ] Gemini extracts base rate matrix
- [ ] FICO × LTV grid extracted correctly
- [ ] All adjustment types captured
- [ ] JSON output validates against schema

---

### Task 4.4: Create Staging Model and Review UI

**Agent**: Rate Sheet Agent  
**Priority**: P1 - High  
**Estimated Time**: 3-4 hours

#### Context
Extracted rate data must be reviewed by a human before going live. We need a staging table and an admin UI to approve changes.

#### Instructions

1. **Create staging models**
   ```python
   # ratesheets/models.py
   
   from django.db import models
   from django.contrib.postgres.fields import JSONField
   
   class RateSheetImport(models.Model):
       """
       Staging table for imported rate sheet data.
       
       Human must approve before data is published to LenderProgramOffering.
       """
       
       STATUS_CHOICES = [
           ('pending', 'Pending Review'),
           ('approved', 'Approved'),
           ('rejected', 'Rejected'),
           ('published', 'Published'),
       ]
       
       lender = models.ForeignKey('pricing.Lender', on_delete=models.CASCADE)
       source_url = models.URLField()
       source_pdf = models.FileField(upload_to='ratesheets/')
       
       # Extracted data
       extracted_data = JSONField()
       effective_date = models.DateField()
       
       # Review workflow
       status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
       reviewed_by = models.ForeignKey(
           'auth.User', on_delete=models.SET_NULL, null=True, blank=True
       )
       reviewed_at = models.DateTimeField(null=True, blank=True)
       review_notes = models.TextField(blank=True)
       
       # Tracking
       created_at = models.DateTimeField(auto_now_add=True)
       
       # Diff from previous version
       previous_import = models.ForeignKey(
           'self', on_delete=models.SET_NULL, null=True, blank=True
       )
       
       class Meta:
           ordering = ['-created_at']
       
       def get_diff(self):
           """Compare to previous import and return changes."""
           if not self.previous_import:
               return {'type': 'new', 'changes': []}
           
           # Compare extracted_data JSON
           old = self.previous_import.extracted_data
           new = self.extracted_data
           
           changes = []
           
           # Compare base rates
           # ... implementation
           
           return {'type': 'update', 'changes': changes}
   ```

2. **Create Django Admin integration**
   ```python
   # ratesheets/admin.py
   
   from django.contrib import admin
   from django.utils.html import format_html
   from .models import RateSheetImport
   
   @admin.register(RateSheetImport)
   class RateSheetImportAdmin(admin.ModelAdmin):
       list_display = ['lender', 'effective_date', 'status', 'created_at', 'review_actions']
       list_filter = ['status', 'lender']
       readonly_fields = ['extracted_data_pretty', 'diff_display']
       actions = ['approve_selected', 'reject_selected']
       
       def extracted_data_pretty(self, obj):
           """Display JSON in readable format."""
           import json
           return format_html(
               '<pre>{}</pre>',
               json.dumps(obj.extracted_data, indent=2)
           )
       
       def diff_display(self, obj):
           """Show what changed from previous version."""
           diff = obj.get_diff()
           if diff['type'] == 'new':
               return format_html('<span style="color:green">New rate sheet</span>')
           
           html = '<ul>'
           for change in diff['changes']:
               html += f'<li>{change}</li>'
           html += '</ul>'
           return format_html(html)
       
       def review_actions(self, obj):
           """Quick approve/reject buttons."""
           if obj.status == 'pending':
               return format_html(
                   '<a href="{}">Approve</a> | <a href="{}">Reject</a>',
                   f'/admin/ratesheets/ratesheetimport/{obj.id}/approve/',
                   f'/admin/ratesheets/ratesheetimport/{obj.id}/reject/'
               )
           return obj.get_status_display()
       
       @admin.action(description='Approve selected rate sheets')
       def approve_selected(self, request, queryset):
           queryset.update(status='approved', reviewed_by=request.user)
   ```

3. **Create publish command**
   ```python
   # ratesheets/management/commands/publish_rates.py
   
   class Command(BaseCommand):
       help = 'Publish approved rate sheet data to LenderProgramOffering'
       
       def handle(self, *args, **options):
           approved = RateSheetImport.objects.filter(status='approved')
           
           for import_obj in approved:
               self._publish(import_obj)
               import_obj.status = 'published'
               import_obj.save()
       
       def _publish(self, import_obj):
           """Update LenderProgramOffering with new rates."""
           data = import_obj.extracted_data
           
           # Update offering rates
           # Update RateAdjustment records
           # ...
   ```

#### Success Criteria
- [ ] Staging model stores extracted data as JSON
- [ ] Admin UI shows diff from previous version
- [ ] Approve/Reject workflow works
- [ ] Published data updates LenderProgramOffering

---

## 📊 Progress Tracking

| Task | Status | Blocker | Notes |
|------|--------|---------|-------|
| 4.1 CSV Reader | ⏳ | - | - |
| 4.2 PDF Downloader | ⏳ | - | - |
| 4.3 LLM Extraction | ⏳ | 4.2 | Needs Gemini API key |
| 4.4 Staging & Review | ⏳ | 4.3 | - |

---

## 🔗 Reference Materials

- [Rate Extraction Field Mapping](file:///home/samalabam/code/unified-cmtg/knowledge-base/rate_extraction_field_mapping.md)
- [Rate Sheet Extraction SOP](file:///home/samalabam/code/unified-cmtg/knowledge-base/ratesheet_extraction_sop.md)
- [Sample Rate Sheets](file:///home/samalabam/code/unified-cmtg/Ratesheet-samples/)

---

*Last Updated: 2026-01-11*
