import google.generativeai as genai
import os
import logging

logger = logging.getLogger(__name__)

class GeminiProcessor:
    """
    Uses the Gemini API to extract structured data from a rate sheet.
    """
    
    # Define a strict JSON schema for the expected output.
    # This helps the model return data in a consistent format.
    ADJUSTMENT_JSON_SCHEMA = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "program_name": {
                    "type": "string",
                    "description": "The name of the loan program this adjustment applies to, as listed on the rate sheet.",
                },
                "min_fico": {
                    "type": "number",
                    "description": "The minimum FICO score for this adjustment tier.",
                },
                "max_fico": {
                    "type": "number",
                    "description": "The maximum FICO score for this adjustment tier.",
                },
                "min_ltv": {
                    "type": "number",
                    "description": "The minimum Loan-to-Value (LTV) ratio for this adjustment tier.",
                },
                "max_ltv": {
                    "type": "number",
                    "description": "The maximum Loan-to-Value (LTV) ratio for this adjustment tier.",
                },
                "adjustment": {
                    "type": "number",
                    "description": "The price adjustment in points. A negative number indicates a cost, a positive number indicates a credit.",
                },
            },
            "required": ["program_name", "min_fico", "max_fico", "min_ltv", "max_ltv", "adjustment"],
        },
    }

    def __init__(self, ratesheet):
        self.ratesheet = ratesheet
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            'gemini-1.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )

    def get_system_prompt(self):
        """
        Creates the system prompt with instructions for the LLM.
        """
        return f"""
        You are a mortgage data extraction specialist. Your task is to analyze the provided rate sheet text and extract all pricing adjustments.
        The rate sheet contains grids for Loan Level Price Adjustments (LLPAs), typically based on FICO score ranges and LTV (Loan-to-Value) ranges.

        Analyze the text and return a clean JSON list of all adjustment objects.
        The JSON output must conform to this schema: {self.ADJUSTMENT_JSON_SCHEMA}

        IMPORTANT RULES:
        1.  Accurately capture all FICO and LTV boundaries for each grid cell.
        2.  Pricing adjustments are in points. A value like (1.250) or -1.250 is a cost and should be a negative number. A value like 1.250 is a credit and should be a positive number.
        3.  The 'program_name' should be the title of the specific program the adjustment grid belongs to (e.g., "DSCR Standard", "Investor Flex").
        4.  If a range is open-ended (e.g., "740+ FICO" or "< 65% LTV"), use a reasonable high or low number (e.g., 900 for max FICO, 0 for min LTV).
        5.  Do not include any other text or explanations in your response, only the valid JSON list.
        """

    def process(self):
        """
        Processes the rate sheet file using the Gemini API.
        For MVP, we will pass the text content of the PDF.
        A more advanced implementation would use the File API for multimodal input.
        """
        logger.info(f"Starting Gemini processing for RateSheet: {self.ratesheet.id}")
        
        # In a real scenario, we'd extract text from the PDF here.
        # For now, we assume the text is available or passed in.
        # This part will be completed by the `pdfplumber` integration.
        # For now, we'll create a placeholder text.
        # A more robust solution would be to use a text extraction service first.
        
        # Placeholder text - this would come from a PDF text extractor
        # We need this to pass to the model.
        from ratesheets.services.processors.pdf_plumber import PdfPlumberProcessor
        
        text_processor = PdfPlumberProcessor(self.ratesheet)
        pdf_text = text_processor.get_text()
        
        if not pdf_text or len(pdf_text) < 50:
            logger.warning(f"PDF text for {self.ratesheet.id} is very short or empty. Aborting Gemini call.")
            return {"status": "error", "message": "PDF text content is too short or could not be extracted."}

        prompt = self.get_system_prompt()
        
        try:
            response = self.model.generate_content([prompt, pdf_text])
            logger.info(f"Gemini API call successful for RateSheet: {self.ratesheet.id}")
            # The response will be a JSON string that we can parse
            return {"status": "success", "data": response.text}
        except Exception as e:
            logger.error(f"Gemini API call failed for RateSheet {self.ratesheet.id}: {e}")
            return {"status": "error", "message": str(e)}

