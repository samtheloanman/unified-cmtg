import json

class SchemaGenerator:
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
            "description": program.program_description[:160] if program.program_description else f"{program.title} available in {city.name}.",
            "amount": {
                "@type": "MonetaryAmount",
                "currency": "USD",
                "minValue": str(program.min_loan_amount) if program.min_loan_amount else "0",
                "maxValue": str(program.max_loan_amount) if program.max_loan_amount else "0"
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
