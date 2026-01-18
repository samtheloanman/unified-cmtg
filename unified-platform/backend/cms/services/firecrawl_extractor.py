"""
Firecrawl Content Extractor

AI-powered content extraction using self-hosted Firecrawl instance.
Falls back to BeautifulSoup extractor if Firecrawl is unavailable.

Usage:
    extractor = FirecrawlExtractor()
    content = extractor.extract_program_page("https://custommortgage.com/loan-program")
"""

import logging
import requests
from typing import Dict, Optional, Type, Any
from pydantic import BaseModel, Field

# Import fallback extractor
from cms.services.content_extractor import WordPressContentExtractor

logger = logging.getLogger(__name__)

# Firecrawl self-hosted instance
FIRECRAWL_API_URL = "http://localhost:3002"


# --- Pydantic Schemas for Structured Extraction ---

class ProgramPageSchema(BaseModel):
    """Schema for extracting Program page content."""
    mortgage_program_highlights: str = Field(
        default="",
        description="Key features and highlights of the mortgage program, including bullet points"
    )
    what_are: str = Field(
        default="",
        description="Explanation of what this loan type is and how it works"
    )
    benefits_of: str = Field(
        default="",
        description="Benefits and advantages of choosing this program"
    )
    how_to_qualify_for: str = Field(
        default="",
        description="Qualification requirements, eligibility criteria, and what you need"
    )
    why_us: str = Field(
        default="",
        description="Why choose Custom Mortgage for this program"
    )
    program_faq: str = Field(
        default="",
        description="Frequently asked questions about the program"
    )
    details_about_mortgage_loan_program: str = Field(
        default="",
        description="Additional program details, rates, and specifics"
    )


class FundedLoanSchema(BaseModel):
    """Schema for extracting Funded Loan case study content."""
    description: str = Field(
        default="",
        description="The main case study content describing the funded loan"
    )
    loan_amount: Optional[str] = Field(
        default=None,
        description="The loan amount (e.g., '$500,000' or '$1.2M')"
    )
    loan_type: Optional[str] = Field(
        default=None,
        description="Type of loan (e.g., 'FHA', 'Conventional', 'DSCR')"
    )
    property_type: Optional[str] = Field(
        default=None,
        description="Type of property (e.g., 'Single Family', 'Multi-Family')"
    )
    location: Optional[str] = Field(
        default=None,
        description="Property location (City, State)"
    )


class BlogPostSchema(BaseModel):
    """Schema for extracting Blog content."""
    body: str = Field(
        default="",
        description="The main blog article content"
    )
    excerpt: Optional[str] = Field(
        default=None,
        description="A short summary or excerpt of the blog post"
    )


class FirecrawlExtractor:
    """
    AI-powered content extraction using self-hosted Firecrawl.
    
    Features:
    - Uses Pydantic schemas for structured extraction
    - Falls back to BeautifulSoup if Firecrawl unavailable
    - Connects to local Firecrawl instance on localhost:3002
    """
    
    def __init__(self, api_url: str = FIRECRAWL_API_URL, timeout: int = 60):
        self.api_url = api_url.rstrip('/')
        self.timeout = timeout
        self._is_available = None
    
    def is_available(self) -> bool:
        """Check if Firecrawl service is available."""
        if self._is_available is not None:
            return self._is_available
        
        try:
            response = requests.get(
                f"{self.api_url}/v1/scrape",
                timeout=5
            )
            # Even a 401/405 means the service is running
            self._is_available = response.status_code != 404
        except requests.RequestException:
            self._is_available = False
            logger.warning("Firecrawl not available, will use fallback extractor")
        
        return self._is_available
    
    def extract_with_schema(
        self, 
        url: str, 
        schema: Type[BaseModel],
        actions: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Extract structured content from URL using Firecrawl with schema.
        
        Args:
            url: The URL to scrape and extract from
            schema: Pydantic model defining extraction schema
            actions: Optional browser actions before extraction
            
        Returns:
            Dictionary of extracted content matching schema fields
        """
        if not self.is_available():
            logger.info(f"Firecrawl unavailable, using fallback for {url}")
            return self._fallback_extract(url, schema)
        
        try:
            payload = {
                "url": url,
                "formats": ["extract"],
                "extract": {
                    "schema": schema.model_json_schema()
                }
            }
            
            if actions:
                payload["actions"] = actions
            
            response = requests.post(
                f"{self.api_url}/v1/scrape",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the data from Firecrawl response
            if result.get("success") and result.get("data", {}).get("extract"):
                extracted = result["data"]["extract"]
                logger.info(f"Successfully extracted {len(extracted)} fields from {url}")
                return extracted
            else:
                logger.warning(f"Firecrawl returned empty extraction for {url}")
                return self._fallback_extract(url, schema)
                
        except requests.RequestException as e:
            logger.error(f"Firecrawl request failed: {e}")
            return self._fallback_extract(url, schema)
    
    def extract_from_html(
        self,
        html_content: str,
        schema: Type[BaseModel]
    ) -> Dict[str, Any]:
        """
        Extract content from raw HTML using schema.
        For offline/cached HTML, uses BeautifulSoup fallback.
        
        Args:
            html_content: Raw HTML string
            schema: Pydantic model defining extraction schema
            
        Returns:
            Dictionary of extracted content
        """
        # For raw HTML, we use the BeautifulSoup extractor
        return self._fallback_extract_html(html_content, schema)
    
    def _fallback_extract(self, url: str, schema: Type[BaseModel]) -> Dict[str, Any]:
        """Fallback extraction using BeautifulSoup after fetching URL."""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return self._fallback_extract_html(response.text, schema)
        except Exception as e:
            logger.error(f"Fallback extraction failed for {url}: {e}")
            return {}
    
    def _fallback_extract_html(self, html_content: str, schema: Type[BaseModel]) -> Dict[str, Any]:
        """Fallback extraction from HTML using BeautifulSoup."""
        try:
            extractor = WordPressContentExtractor(html_content)
            
            schema_name = schema.__name__
            
            if schema_name == "ProgramPageSchema":
                return extractor._extract_program_page()
            elif schema_name == "FundedLoanSchema":
                result = extractor._extract_funded_loan_page()
                # Try to extract loan details too
                if hasattr(extractor, 'extract_loan_details'):
                    from cms.services.content_extractor import FundedLoanExtractor
                    loan_extractor = FundedLoanExtractor(html_content)
                    result.update(loan_extractor.extract_loan_details())
                return result
            elif schema_name == "BlogPostSchema":
                return {"body": extractor._extract_main_content()}
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Fallback HTML extraction failed: {e}")
            return {}
    
    # --- Convenience methods for specific page types ---
    
    def extract_program_page(self, url: str) -> Dict[str, str]:
        """Extract content for a ProgramPage."""
        return self.extract_with_schema(url, ProgramPageSchema)
    
    def extract_funded_loan(self, url: str) -> Dict[str, Any]:
        """Extract content for a FundedLoanPage."""
        return self.extract_with_schema(url, FundedLoanSchema)
    
    def extract_blog_post(self, url: str) -> Dict[str, str]:
        """Extract content for a BlogPage."""
        return self.extract_with_schema(url, BlogPostSchema)
    
    def scrape_to_markdown(self, url: str) -> str:
        """
        Scrape URL and return clean markdown content.
        Useful for LLM-ready content.
        
        Args:
            url: URL to scrape
            
        Returns:
            Markdown-formatted content
        """
        if not self.is_available():
            logger.warning("Firecrawl unavailable for markdown scrape")
            return ""
        
        try:
            response = requests.post(
                f"{self.api_url}/v1/scrape",
                json={
                    "url": url,
                    "formats": ["markdown"]
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("success"):
                return result.get("data", {}).get("markdown", "")
            return ""
            
        except requests.RequestException as e:
            logger.error(f"Markdown scrape failed: {e}")
            return ""


# --- Convenience function ---
def extract_content(url: str, page_type: str = "program") -> Dict[str, Any]:
    """
    Extract content from a URL based on page type.
    
    Args:
        url: The URL to extract from
        page_type: One of 'program', 'funded_loan', 'blog'
        
    Returns:
        Dictionary of extracted content
    """
    extractor = FirecrawlExtractor()
    
    if page_type == "program":
        return extractor.extract_program_page(url)
    elif page_type == "funded_loan":
        return extractor.extract_funded_loan(url)
    elif page_type == "blog":
        return extractor.extract_blog_post(url)
    else:
        raise ValueError(f"Unknown page_type: {page_type}")


if __name__ == "__main__":
    # Quick test
    extractor = FirecrawlExtractor()
    
    print(f"Firecrawl available: {extractor.is_available()}")
    
    if extractor.is_available():
        # Test extraction
        result = extractor.scrape_to_markdown("https://custommortgage.com")
        print(f"Scraped {len(result)} chars of markdown")
