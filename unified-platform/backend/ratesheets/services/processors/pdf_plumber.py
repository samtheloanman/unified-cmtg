import logging
import pdfplumber
from typing import Any, Dict
from django.utils import timezone
from .base import BaseRateSheetProcessor

logger = logging.getLogger(__name__)

class PdfPlumberProcessor(BaseRateSheetProcessor):
    """
    PDF rate sheet processor using pdfplumber.
    Extracts text and tables from PDF files.
    """
    
    def process(self) -> Dict[str, Any]:
        """
        Extract extracts text from the PDF and attempts to parse it.
        For MVP, this logs the first few pages and counts pages.
        """
        try:
            with pdfplumber.open(self.file_path) as pdf:
                full_text = ""
                full_tables = []
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
                    full_tables.extend(page.extract_tables())
            
            # Log preview
            self.log(f"Extracted {len(full_text)} chars and {len(full_tables)} tables.")
            
            # Simple routing based on filename or content
            parsed_data = {}
            if "acra" in self.file_path.lower():
                parsed_data = self._parse_acra(full_text, full_tables)
            
            from ratesheets.services.ingestion import update_pricing_from_extraction
            result = update_pricing_from_extraction(self.rate_sheet.lender, parsed_data)
            
            self.log(f"Ingestion Result: {result}")
            return parsed_data

        except Exception as e:
            self.log(f"CRITICAL ERROR: {str(e)}")
            raise e

    def _parse_acra(self, text, tables):
        """
        Specific logic for Acra Lending rate sheets.
        """
        data = {"lender": "Acra", "programs": []}
        
        # 1. Parse Date
        import re
        date_match = re.search(r"Dated:\s*(\d{2}/\d{2}/\d{4})", text)
        if date_match:
            data["valid_date"] = date_match.group(1)
            self.log(f"Found Date: {data['valid_date']}")

        # 2. Heuristic: Look for tables with FICO columns
        for i, table in enumerate(tables):
            # Check if table has headers that look like LTV or FICO
            # Acra sample has 'FICO & LTV' in header usually
            if not table: continue
            
            # Log first row
            self.log(f"Table {i} Row 0: {table[0]}")
            
            # Flatten rows to string for quick check
            headers = [str(cell).lower() for cell in table[0] if cell]
            header_str = " ".join(headers)
            
            if "fico" in header_str or "ltv" in header_str or "55.01" in header_str:
                self.log(f"Found Potential Pricing Table {i}")
                # Naive extraction of first 5 rows
                data["programs"].append({
                    "table_index": i,
                    "sample_rows": table[1:6] # Skip header
                })
        
        return data
