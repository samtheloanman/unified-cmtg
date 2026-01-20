import json
from wagtail.models import Page

class SchemaGenerator:
    """
    Generates JSON-LD schema for Program and Local Program pages.
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
            faq_schema = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": faq_items
            }
            return [schema, faq_schema]

        return [schema]

    @staticmethod
    def generate_local_schema(program, city, office):
        """
        Generate JSON-LD schema for a local program page.
        Combines MortgageLoan and LocalBusiness.
        """
        if not (program and city and office):
            return ""

        url = f"https://cmre.c-mtg.com/{program.slug}-{city.slug}-{city.state.lower()}/" # Approximate URL
        
        # 1. Financial Product Schema
        product_schema = {
            "@type": "MortgageLoan",
            "name": f"{program.title} in {city.name}, {city.state}",
            "description": program.search_description[:160] if program.search_description else f"{program.title} available in {city.name}.",
            "amount": {
                "@type": "MonetaryAmount",
                "currency": "USD",
                "minValue": str(program.minimum_loan_amount) if getattr(program, 'minimum_loan_amount', None) else "0",
                "maxValue": str(program.maximum_loan_amount) if getattr(program, 'maximum_loan_amount', None) else "0"
            },
            "interestRate": {
                "@type": "QuantitativeValue",
                 "minValue": str(program.interest_rate_min) if getattr(program, 'interest_rate_min', None) else "0",
                 "maxValue": str(program.interest_rate_max) if getattr(program, 'interest_rate_max', None) else "0",
                 "unitText": "PERCENT"
            }
        }

        # 2. Local Business Schema (Office)
        business_schema = {
            "@type": "ProfessionalService",
            "name": f"Custom Mortgage - {city.name} Serving Office",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": office.address,
                "addressLocality": office.city,
                "addressRegion": office.state,
                "postalCode": office.zipcode,
                "addressCountry": "US"
            },
            "telephone": office.phone,
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": str(office.latitude),
                "longitude": str(office.longitude)
            },
            "url": "https://custommortgageinc.com" # Brand URL
        }

        graph = {
            "@context": "https://schema.org",
            "@graph": [product_schema, business_schema]
        }
        
        return json.dumps(graph, indent=2)
