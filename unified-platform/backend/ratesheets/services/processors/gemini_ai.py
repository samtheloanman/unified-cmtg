"""
AI-powered rate sheet processor using Google Gemini.

This processor uses Google's Gemini AI to intelligently parse and extract
structured data from rate sheet PDFs, handling varying formats automatically.
"""

import json
import logging
from typing import Any, Dict, List, Optional
import os

try:
    from google import genai
    from google.genai import types
    from google.genai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

from django.conf import settings

from .base import BaseRateSheetProcessor, RateSheetProcessingError

logger = logging.getLogger(__name__)


class GeminiAIProcessor(BaseRateSheetProcessor):
    """
    AI-powered rate sheet processor using Google Gemini.

    Uses Gemini Pro to understand and extract structured pricing data
    from rate sheets regardless of format variations.
    """

    EXTRACTION_PROMPT = """You are a mortgage rate sheet data extraction expert.
Analyze the provided rate sheet text and tables, then extract structured pricing information.

IMPORTANT: Return ONLY valid JSON. Do not include any explanation, markdown, or additional text.

Extract the following information:

1. **Metadata**:
   - effective_date: Date when rates are effective (YYYY-MM-DD format)
   - lender_name: Name of the lender
   - lock_periods: List of available rate lock periods in days (e.g., [30, 45, 60])

2. **Programs**: List of loan programs with:
   - program_name: Name of the program (e.g., "DSCR 30-Year Fixed")
   - program_type: Type (conventional, dscr, bank_statement, fha, va, etc.)
   - base_rate: Base interest rate as a float (e.g., 7.25)
   - min_fico: Minimum FICO score required
   - max_ltv: Maximum loan-to-value ratio as percentage (e.g., 75.0)
   - min_loan_amount: Minimum loan amount
   - max_loan_amount: Maximum loan amount
   - property_types: List of allowed property types
   - occupancy_types: List of allowed occupancy types

3. **Adjustments**: List of pricing adjustments with:
   - adjustment_type: Type of adjustment (fico_ltv, purpose, occupancy, property_type, loan_amount, lock_period, state)
   - description: Human-readable description

   For 2D grid adjustments (FICO × LTV):
   - row_label: "fico" or "ltv"
   - row_min: Minimum value for row dimension
   - row_max: Maximum value for row dimension
   - col_label: "ltv" or "fico" (opposite of row)
   - col_min: Minimum value for column dimension
   - col_max: Maximum value for column dimension
   - adjustment_points: Adjustment in points (negative = cost, positive = credit)

   For 1D adjustments:
   - value_key: The lookup key (e.g., "purchase", "CA", "investment")
   - adjustment_points: Adjustment in points

Return ONLY this JSON structure:
{
  "metadata": {
    "effective_date": "YYYY-MM-DD",
    "lender_name": "Lender Name",
    "lock_periods": [30, 45, 60]
  },
  "programs": [
    {
      "program_name": "Program Name",
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
}"""

    def __init__(self, rate_sheet_instance):
        """Initialize Gemini AI processor."""
        super().__init__(rate_sheet_instance)

        if not GEMINI_AVAILABLE:
            raise RateSheetProcessingError(
                "google-genai library not installed. "
                "Install with: pip install google-genai"
            )

        if not PDFPLUMBER_AVAILABLE:
            raise RateSheetProcessingError(
                "pdfplumber library not installed. "
                "Install with: pip install pdfplumber"
            )

        # Initialize Gemini
        api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise RateSheetProcessingError(
                "GOOGLE_API_KEY not found in settings or environment"
            )

        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-1.5-pro'

    def validate_file_exists(self) -> bool:
        """Check if the rate sheet file exists."""
        return os.path.exists(self.file_path)

    def process(self) -> Dict[str, Any]:
        """
        Process rate sheet using AI extraction.

        Returns:
            Dictionary with extracted programs, adjustments, and metadata

        Raises:
            RateSheetProcessingError: If processing fails
        """
        self.log(f"Starting AI-powered PDF processing with Gemini")

        if not self.validate_file_exists():
            raise RateSheetProcessingError(
                f"Rate sheet file not found: {self.file_path}"
            )

        try:
            # Step 1: Extract text and tables from PDF
            pdf_content = self._extract_pdf_content()

            # Step 2: Use Gemini to parse the content
            self.log(f"Sending to Gemini AI for structured extraction")
            structured_data = self._ai_extract_data(pdf_content)

            # Step 3: Validate and enrich the data
            validated_data = self._validate_extraction(structured_data)

            self.log(f"AI extraction completed successfully")
            return validated_data

        except Exception as e:
            error_msg = f"Error in AI processing: {str(e)}"
            self.log(f"CRITICAL ERROR: {error_msg}")
            raise RateSheetProcessingError(error_msg) from e

    def _extract_pdf_content(self) -> str:
        """
        Extract text and tables from PDF.

        Returns:
            Formatted string with PDF content for AI processing
        """
        content_parts = []

        with pdfplumber.open(self.file_path) as pdf:
            self.log(f"Extracting from {len(pdf.pages)} pages")

            # Extract text from each page
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    content_parts.append(f"=== Page {page_num} Text ===\n{page_text}")

                # Extract tables
                tables = page.extract_tables()
                for table_num, table in enumerate(tables, start=1):
                    if table:
                        table_str = self._format_table(table)
                        content_parts.append(
                            f"\n=== Page {page_num} Table {table_num} ===\n{table_str}"
                        )

        full_content = "\n\n".join(content_parts)

        # Log content size
        self.log(f"Extracted {len(full_content)} characters")

        # Truncate if too large (Gemini has token limits)
        max_chars = 100000  # Increased limit for Gemini 1.5 Pro
        if len(full_content) > max_chars:
            self.log(f"Content truncated from {len(full_content)} to {max_chars} chars")
            full_content = full_content[:max_chars]

        return full_content

    def _format_table(self, table: List[List[str]]) -> str:
        """
        Format table as readable text for AI.

        Args:
            table: Table data as list of lists

        Returns:
            Formatted table string
        """
        lines = []
        for row in table:
            # Join cells with | separator, handling None values
            cells = [str(cell) if cell is not None else '' for cell in row]
            lines.append(' | '.join(cells))
        return '\n'.join(lines)

    def _ai_extract_data(self, pdf_content: str) -> Dict[str, Any]:
        """
        Use Gemini AI to extract structured data.

        Args:
            pdf_content: Extracted PDF content

        Returns:
            Parsed JSON data from AI

        Raises:
            RateSheetProcessingError: If AI extraction fails
        """
        try:
            # Combine prompt with content
            full_prompt = f"{self.EXTRACTION_PROMPT}\n\nRATE SHEET CONTENT:\n\n{pdf_content}"

            # Generate with safety settings
            # Note: google-genai uses config objects, not dicts for safety settings
            # We'll use defaults for now as they are reasonable
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[full_prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            # Extract text from response
            response_text = response.text.strip()

            # Log response for debugging
            self.log(f"AI Response (first 500 chars): {response_text[:500]}")

            # Parse JSON from response
            # Response should be clean JSON due to response_mime_type
            
            # Defensive cleaning just in case
            if response_text.startswith('```json'):
                response_text = response_text[7:] 
            if response_text.startswith('```'):
                response_text = response_text[3:] 
            if response_text.endswith('```'):
                response_text = response_text[:-3]

            response_text = response_text.strip()

            # Parse JSON
            data = json.loads(response_text)

            self.log(f"Successfully parsed AI response")
            return data

        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse AI response as JSON: {str(e)}"
            self.log(error_msg)
            if 'response_text' in locals():
                self.log(f"Raw response: {response_text[:1000]}")
            raise RateSheetProcessingError(error_msg) from e

        except Exception as e:
            error_msg = f"AI extraction failed: {str(e)}"
            self.log(error_msg)
            raise RateSheetProcessingError(error_msg) from e

    def _validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and enrich extracted data.

        Args:
            data: Extracted data from AI

        Returns:
            Validated and enriched data
        """
        # Ensure required keys exist
        if 'metadata' not in data:
            data['metadata'] = {}

        if 'programs' not in data:
            data['programs'] = []

        if 'adjustments' not in data:
            data['adjustments'] = []

        # Log statistics
        self.log(
            f"Extracted: {len(data['programs'])} programs, "
            f"{len(data['adjustments'])} adjustments"
        )

        # Add extraction metadata
        data['metadata']['extraction_method'] = 'gemini_ai'
        data['metadata']['model_version'] = self.model_name

        return data
