"""
Rate sheet processors package.

This package provides various processors for extracting data from rate sheet files.

Available processors:
- BaseRateSheetProcessor: Abstract base class for all processors
- PdfPlumberProcessor: Basic PDF text and table extraction
- GeminiAIProcessor: AI-powered intelligent extraction (requires google-generativeai)

Usage:
    from ratesheets.services.processors import get_processor_for_rate_sheet

    # Get default processor for rate sheet
    processor = get_processor_for_rate_sheet(rate_sheet)
    result = processor.process()

    # Use specific processor
    processor = get_processor_for_rate_sheet(rate_sheet, processor_name='gemini_ai')
    result = processor.process()
"""

from .base import BaseRateSheetProcessor, RateSheetProcessingError
from .factory import (
    ProcessorRegistry,
    get_processor_for_rate_sheet,
    registry,
)
from .pdf_plumber import PdfPlumberProcessor

# Conditionally import GeminiAIProcessor
try:
    from .gemini_ai import GeminiAIProcessor
    __all__ = [
        'BaseRateSheetProcessor',
        'RateSheetProcessingError',
        'PdfPlumberProcessor',
        'GeminiAIProcessor',
        'ProcessorRegistry',
        'get_processor_for_rate_sheet',
        'registry',
    ]
except ImportError:
    __all__ = [
        'BaseRateSheetProcessor',
        'RateSheetProcessingError',
        'PdfPlumberProcessor',
        'ProcessorRegistry',
        'get_processor_for_rate_sheet',
        'registry',
    ]
