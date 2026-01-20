import json
from wagtail.models import Page

class SchemaGenerator:
    """
    Generates JSON-LD schema for Program pages.
    """
    
    @staticmethod
    def generate_loan_product_schema(program_page, base_url="https://cmtg.com"):
        """
        Generates Schema.org FinancialProduct JSON-LD.
        """
        # Base FinancialProduct schema
        schema = {
            "@context": "https://schema.org",
            "@type": "FinancialProduct",
            "name": program_page.title,
            "description": program_page.search_description or program_page.title,
            "url": f"{base_url}{program_page.url}",
            "provider": {
                "@type": "Organization",
                "name": "Custom Mortgage",
                "url": base_url
            },
            "feesAndCommissionsSpecification": "Contact for details",
        }
        
        # Interest Rate (if present)
        if hasattr(program_page, 'interest_rates') and program_page.interest_rates:
            schema["interestRate"] = {
                "@type": "QuantitativeValue",
                "name": "Interest Rate",
                "value": program_page.interest_rates # Assuming string range or value
            }
            
        # Loan amounts
        if hasattr(program_page, 'minimum_loan_amount') and program_page.minimum_loan_amount:
             schema["amount"] = {
                "@type": "MonetaryAmount",
                "minValue": float(program_page.minimum_loan_amount),
                "currency": "USD"
            }
            
        if hasattr(program_page, 'maximum_loan_amount') and program_page.maximum_loan_amount:
             if "amount" not in schema:
                 schema["amount"] = {"@type": "MonetaryAmount", "currency": "USD"}
             schema["amount"]["maxValue"] = float(program_page.maximum_loan_amount)

        # FAQ Schema (if FAQ streamfield exists)
        faq_items = []
        if hasattr(program_page, 'faq'):
            for block in program_page.faq:
                if block.block_type == 'faq_item':
                    faq_items.append({
                        "@type": "Question",
                        "name": block.value.get('question'),
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": str(block.value.get('answer')) # RichText to string
                        }
                    })
        
        if faq_items:
            # If FAQs exist, wrap FinancialProduct in an FAQPage or append to it?
            # Usually better to have separate entities or a graph.
            # Let's return a list of schemas (Graph)
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": faq_items
            }
            return [schema, faq_schema]

        return [schema]
