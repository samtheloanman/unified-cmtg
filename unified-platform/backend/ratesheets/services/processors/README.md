# Rate Sheet Processors

This directory contains the rate sheet processing pipeline for extracting structured pricing data from lender rate sheet files (PDFs, Excel, etc.).

## Overview

The processor system provides a flexible, extensible architecture for parsing rate sheets from various lenders with different formats. It uses:

- **Abstract base class** (`BaseRateSheetProcessor`) defining the processor interface
- **Multiple processor implementations** for different extraction strategies
- **Factory pattern** for automatic processor selection
- **Ingestion service** for storing extracted data in the database

## Architecture

```
ratesheets/services/processors/
├── base.py              # BaseRateSheetProcessor abstract class
├── pdf_plumber.py       # Basic PDF text/table extraction
├── gemini_ai.py         # AI-powered intelligent extraction
├── factory.py           # Processor registry and selection
└── __init__.py          # Package exports
```

## Available Processors

### 1. PdfPlumberProcessor

**File:** `pdf_plumber.py`
**Dependencies:** `pdfplumber`
**Best for:** Simple rate sheets with predictable table structures

**Features:**
- Extracts text and tables from PDF pages
- Lender-specific parsing logic (e.g., Acra Lending)
- Lightweight and fast
- No external API dependencies

**Usage:**
```python
from ratesheets.services.processors import PdfPlumberProcessor

processor = PdfPlumberProcessor(rate_sheet_instance)
result = processor.process()
```

### 2. GeminiAIProcessor

**File:** `gemini_ai.py`
**Dependencies:** `google-generativeai`, `pdfplumber`
**Best for:** Complex or variable-format rate sheets requiring intelligent parsing

**Features:**
- Uses Google Gemini 1.5 Pro for intelligent extraction
- Handles varying rate sheet formats automatically
- Extracts structured JSON with metadata, programs, and adjustments
- Returns data ready for ingestion service

**Configuration:**
Set `GOOGLE_API_KEY` in Django settings:
```python
# settings.py
GOOGLE_API_KEY = 'your-google-api-key'
```

**Usage:**
```python
from ratesheets.services.processors import GeminiAIProcessor

processor = GeminiAIProcessor(rate_sheet_instance)
result = processor.process()  # Returns structured dict
```

**Output Format:**
```python
{
    "metadata": {
        "effective_date": "2026-01-13",
        "lender_name": "Example Lender",
        "lock_periods": [30, 45, 60],
        "extraction_method": "gemini_ai",
        "model_version": "gemini-1.5-pro"
    },
    "programs": [
        {
            "program_name": "DSCR 30-Year Fixed",
            "program_type": "dscr",
            "base_rate": 7.25,
            "min_fico": 640,
            "max_ltv": 75.0,
            "min_loan_amount": 75000,
            "max_loan_amount": 2000000,
            "property_types": ["residential"],
            "occupancy_types": ["investment"]
        }
    ],
    "adjustments": [
        {
            "adjustment_type": "fico_ltv",
            "description": "FICO 680-699, LTV 70-75",
            "row_label": "fico",
            "row_min": 680,
            "row_max": 699,
            "col_label": "ltv",
            "col_min": 70,
            "col_max": 75,
            "adjustment_points": -0.5
        },
        {
            "adjustment_type": "purpose",
            "description": "Purchase",
            "value_key": "purchase",
            "adjustment_points": 0.0
        }
    ]
}
```

## Using the Factory

The factory provides automatic processor selection based on configuration and file type.

### Basic Usage

```python
from ratesheets.services.processors import get_processor_for_rate_sheet

# Automatic selection (GeminiAI if configured, else PdfPlumber)
processor = get_processor_for_rate_sheet(rate_sheet)
result = processor.process()
```

### Explicit Processor Selection

```python
# Use specific processor
processor = get_processor_for_rate_sheet(
    rate_sheet,
    processor_name='gemini_ai'
)
result = processor.process()
```

### Lender-Specific Processors

```python
# Different processors for different lenders
lender_processor_map = {
    1: 'gemini_ai',      # Lender ID 1 uses AI
    2: 'pdf_plumber',    # Lender ID 2 uses basic extraction
}

processor = get_processor_for_rate_sheet(
    rate_sheet,
    lender_processor_map=lender_processor_map
)
result = processor.process()
```

## Celery Integration

Rate sheet processing runs asynchronously via Celery tasks.

**Task:** `ratesheets.tasks.process_ratesheet`

The task automatically:
1. Checks for `GOOGLE_API_KEY` in settings
2. Uses `GeminiAIProcessor` if configured, else `PdfPlumberProcessor`
3. Calls ingestion service to store extracted data
4. Updates rate sheet status and logs

**Triggering:**
```python
from ratesheets.tasks import process_ratesheet

# Trigger async processing
process_ratesheet.delay(rate_sheet.id)
```

## Data Flow

```
1. Upload Rate Sheet PDF
   ↓
2. Celery Task: process_ratesheet
   ↓
3. Processor Factory: Select appropriate processor
   ↓
4. Processor: Extract structured data
   ↓
5. Ingestion Service: Store in database
   - Create/update ProgramType
   - Create/update LenderProgramOffering
   - Create/update RateAdjustment records
   ↓
6. Rate sheet status updated to PROCESSED
```

## Creating a Custom Processor

To add a new processor:

### 1. Create Processor Class

```python
# my_custom_processor.py
from .base import BaseRateSheetProcessor

class MyCustomProcessor(BaseRateSheetProcessor):
    """Custom processor for specific rate sheet format."""

    def process(self):
        """
        Process the rate sheet and return structured data.

        Returns:
            Dictionary matching ingestion service format
        """
        self.log("Starting custom processing")

        # Your extraction logic here
        data = self._extract_data()

        self.log("Processing complete")
        return data

    def _extract_data(self):
        """Custom extraction logic."""
        # Read file
        with open(self.file_path, 'rb') as f:
            content = f.read()

        # Parse and structure data
        return {
            'metadata': {...},
            'programs': [...],
            'adjustments': [...]
        }
```

### 2. Register with Factory

```python
from ratesheets.services.processors import registry
from .my_custom_processor import MyCustomProcessor

# Register processor
registry.register('my_custom', MyCustomProcessor)

# Now usable via factory
processor = get_processor_for_rate_sheet(
    rate_sheet,
    processor_name='my_custom'
)
```

### 3. Add to Lender Mapping

```python
# In your task or view
lender_processor_map = {
    5: 'my_custom',  # Lender ID 5 uses custom processor
}

processor = get_processor_for_rate_sheet(
    rate_sheet,
    lender_processor_map=lender_processor_map
)
```

## Testing

### Unit Tests

```python
from django.test import TestCase
from ratesheets.models import RateSheet, Lender
from ratesheets.services.processors import PdfPlumberProcessor

class ProcessorTestCase(TestCase):
    def setUp(self):
        self.lender = Lender.objects.create(company_name="Test Lender")
        self.rate_sheet = RateSheet.objects.create(
            lender=self.lender,
            file='test_rate_sheet.pdf'
        )

    def test_pdf_plumber_processor(self):
        processor = PdfPlumberProcessor(self.rate_sheet)
        result = processor.process()

        self.assertIn('programs', result)
        self.assertIsInstance(result['programs'], list)
```

### Integration Tests

```python
from ratesheets.tasks import process_ratesheet

def test_celery_task():
    rate_sheet = RateSheet.objects.create(...)

    # Run task
    process_ratesheet(rate_sheet.id)

    # Verify results
    rate_sheet.refresh_from_db()
    assert rate_sheet.status == RateSheet.STATUS_PROCESSED
    assert rate_sheet.lender.program_offerings.count() > 0
```

## Troubleshooting

### GeminiAIProcessor Not Available

**Error:** `GeminiAIProcessor not available - missing dependencies`

**Solution:** Install dependencies:
```bash
pip install google-generativeai pdfplumber
```

### Google API Key Not Found

**Error:** `GOOGLE_API_KEY not found in settings`

**Solution:** Add to Django settings:
```python
# settings.py or .env
GOOGLE_API_KEY = 'your-api-key-here'
```

### JSON Parse Error from AI

**Error:** `Failed to parse AI response as JSON`

**Possible causes:**
- AI returned explanation text instead of pure JSON
- Rate sheet format too complex
- Content truncated due to token limits

**Solutions:**
1. Check rate sheet file is valid PDF
2. Verify PDF is not too large (>30,000 chars after extraction)
3. Fall back to PdfPlumberProcessor for this lender
4. Add lender-specific parsing logic

### Processing Fails

**Check logs:**
```python
rate_sheet = RateSheet.objects.get(id=123)
print(rate_sheet.log)  # View processing log
```

**Common issues:**
- File path invalid
- PDF corrupted or password-protected
- Missing required fields in extracted data
- Database constraints violated during ingestion

## Performance Considerations

### PdfPlumberProcessor
- **Speed:** Fast (~1-2 seconds per PDF)
- **Cost:** Free
- **Accuracy:** Depends on parsing logic quality

### GeminiAIProcessor
- **Speed:** Moderate (~5-10 seconds per PDF)
- **Cost:** Gemini API usage charges
- **Accuracy:** High for complex/variable formats

### Recommendations
1. Use GeminiAI for new/unknown lenders
2. Use PdfPlumber for high-volume, known formats
3. Implement lender-specific mapping for best performance/cost balance
4. Process asynchronously via Celery to avoid blocking

## API Reference

### BaseRateSheetProcessor

**File:** `ratesheets/services/processors/base.py:16`

Abstract base class for all processors.

**Methods:**
- `__init__(rate_sheet_instance)` - Initialize with RateSheet instance
- `process() -> Dict[str, Any]` - Abstract method to process rate sheet
- `validate_file_exists() -> bool` - Check if file exists
- `log(message: str)` - Append message to rate sheet log

### Ingestion Service

**File:** `ratesheets/services/ingestion.py:31`

**Function:** `update_pricing_from_extraction(lender, extracted_data)`

Ingests extracted data into database models.

**Args:**
- `lender` - Lender model instance
- `extracted_data` - Dictionary or JSON string with programs and adjustments

**Returns:**
- Dictionary with statistics: `{'programs_created': 2, 'adjustments_created': 15, ...}`
- Or legacy string summary

**Supports:**
- New format: Dict with `metadata`, `programs`, `adjustments` keys
- Legacy format: JSON string with adjustment list

## See Also

- [Pricing Models Documentation](/home/samalabam/code/unified-cmtg/unified-platform/backend/pricing/models/)
- [RateSheet Models](/home/samalabam/code/unified-cmtg/unified-platform/backend/ratesheets/models.py)
- [Celery Tasks](/home/samalabam/code/unified-cmtg/unified-platform/backend/ratesheets/tasks.py)
