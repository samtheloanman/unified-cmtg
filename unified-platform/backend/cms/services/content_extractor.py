"""
WordPress/Elementor Content Extractor

This module provides utilities for extracting structured content from
WordPress pages built with Elementor or other page builders.

The extractor:
- Parses HTML using BeautifulSoup
- Identifies content sections based on H2 headings
- Cleans Elementor markup (classes, inline styles)
- Maps sections to Wagtail model fields
- Returns cleaned HTML ready for RichTextField storage
"""

import re
import logging
from typing import Dict, Optional, Type
from bs4 import BeautifulSoup, Tag


logger = logging.getLogger(__name__)


class WordPressContentExtractor:
    """
    Extracts structured content from WordPress/Elementor pages.

    Usage:
        extractor = WordPressContentExtractor(html_content)
        content = extractor.extract_for_model(ProgramPage)
        # Returns: {'mortgage_program_highlights': '<p>...</p>', ...}
    """

    # Map H2 heading text patterns to Wagtail field names
    PROGRAM_PAGE_SECTION_MAP = {
        'key features': 'mortgage_program_highlights',
        'program highlights': 'mortgage_program_highlights',
        'highlights': 'mortgage_program_highlights',
        'what are': 'what_are',
        'what is': 'what_are',
        'about': 'what_are',
        'benefits': 'benefits_of',
        'advantages': 'benefits_of',
        'how to qualify': 'how_to_qualify_for',
        'qualifying': 'how_to_qualify_for',
        'qualification': 'how_to_qualify_for',
        'eligibility': 'how_to_qualify_for',
        'why choose': 'why_us',
        'why us': 'why_us',
        'why work with': 'why_us',
        'faq': 'program_faq',
        'frequently asked': 'program_faq',
        'questions': 'program_faq',
        'requirements': 'requirements',
        'details': 'details_about_mortgage_loan_program',
        'program details': 'details_about_mortgage_loan_program',
        'loan details': 'details_about_mortgage_loan_program',
    }

    # Tags to extract content from
    CONTENT_TAGS = ['p', 'ul', 'ol', 'div', 'section', 'article', 'h3', 'h4', 'h5', 'h6']

    # Elementor classes to remove
    ELEMENTOR_CLASSES = [
        'elementor',
        'elementor-element',
        'elementor-widget',
        'elementor-section',
        'elementor-column',
        'elementor-container',
        'e-con',
        'e-flex',
    ]

    def __init__(self, html_content: str):
        """
        Initialize extractor with HTML content.

        Args:
            html_content: Raw HTML string or bytes from WordPress page
        """
        # Handle both string and bytes
        if isinstance(html_content, bytes):
            html_content = html_content.decode('utf-8', errors='ignore')

        self.soup = BeautifulSoup(html_content, 'lxml')
        self._extracted_sections = None

    def extract_for_model(self, model_class: Type) -> Dict[str, str]:
        """
        Extract content based on model type.

        Args:
            model_class: Wagtail Page model class (ProgramPage, FundedLoanPage, etc.)

        Returns:
            Dictionary mapping field names to cleaned HTML content
        """
        model_name = model_class.__name__

        if model_name == 'ProgramPage':
            return self._extract_program_page()
        elif model_name == 'FundedLoanPage':
            return self._extract_funded_loan_page()
        elif model_name == 'LegacyRecreatedPage':
            return self._extract_legacy_page()
        else:
            logger.warning(f"Unknown model type: {model_name}, returning empty dict")
            return {}

    def _extract_program_page(self) -> Dict[str, str]:
        """
        Extract content for ProgramPage model.

        Returns:
            Dict with keys: mortgage_program_highlights, what_are, benefits_of, etc.
        """
        if self._extracted_sections is None:
            self._extracted_sections = self._extract_sections_by_headings(
                self.PROGRAM_PAGE_SECTION_MAP
            )

        return self._extracted_sections

    def _extract_funded_loan_page(self) -> Dict[str, str]:
        """
        Extract content for FundedLoanPage model.

        Returns:
            Dict with key: description (main body content)
        """
        # For funded loans, extract all content into description field
        content = self._extract_main_content()

        return {
            'description': content if content else ''
        }

    def _extract_legacy_page(self) -> Dict[str, str]:
        """
        Extract content for LegacyRecreatedPage model.

        Returns:
            Dict with key: body (all page content)
        """
        content = self._extract_main_content()

        return {
            'body': content if content else ''
        }

    def _extract_sections_by_headings(
        self,
        section_map: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Extract content sections based on H2 headings.

        Args:
            section_map: Dictionary mapping heading patterns to field names

        Returns:
            Dictionary of field_name: cleaned_html_content
        """
        content = {}

        # Find all H2 elements
        h2_elements = self.soup.find_all('h2')

        logger.debug(f"Found {len(h2_elements)} H2 headings")

        for h2 in h2_elements:
            heading_text = h2.get_text(strip=True).lower()

            # Match heading to field
            matched_field = None
            for pattern, field_name in section_map.items():
                if pattern in heading_text:
                    matched_field = field_name
                    logger.debug(f"Matched H2 '{heading_text}' to field '{field_name}'")
                    break

            if not matched_field:
                logger.debug(f"No match for H2: '{heading_text}'")
                continue

            # Get content following this H2 until next H2
            section_content = self._extract_section_content(h2)

            if section_content:
                # If field already has content, append to it
                if matched_field in content:
                    content[matched_field] += '\n' + section_content
                else:
                    content[matched_field] = section_content

                logger.debug(
                    f"Extracted {len(section_content)} chars for '{matched_field}'"
                )

        return content

    def _extract_section_content(self, heading: Tag) -> str:
        """
        Extract content following a heading until next heading of same level.

        Args:
            heading: BeautifulSoup Tag for the heading element

        Returns:
            Cleaned HTML content as string
        """
        section_parts = []
        sibling = heading.find_next_sibling()

        while sibling:
            # Stop at next H2
            if sibling.name == 'h2':
                break

            # Extract content from relevant tags
            if sibling.name in self.CONTENT_TAGS:
                cleaned_html = self._clean_element(sibling)
                if cleaned_html.strip():
                    section_parts.append(cleaned_html)

            sibling = sibling.find_next_sibling()

        return '\n'.join(section_parts)

    def _extract_main_content(self) -> str:
        """
        Extract all main content from the page.

        Returns:
            Cleaned HTML content as string
        """
        # Try to find main content area (common WordPress/Elementor selectors)
        main_content = None

        # Try various content container selectors
        for selector in [
            '.entry-content',
            '.post-content',
            '.content-area',
            'main',
            'article',
            '.elementor-widget-theme-post-content',
        ]:
            main_content = self.soup.select_one(selector)
            if main_content:
                logger.debug(f"Found main content using selector: {selector}")
                break

        # If no container found, use body
        if not main_content:
            main_content = self.soup.find('body')
            logger.debug("Using <body> as content container")

        if not main_content:
            return ''

        # Extract and clean all content elements
        content_parts = []
        for element in main_content.find_all(self.CONTENT_TAGS):
            cleaned = self._clean_element(element)
            if cleaned.strip():
                content_parts.append(cleaned)

        return '\n'.join(content_parts)

    def _clean_element(self, element: Tag) -> str:
        """
        Clean an HTML element by removing Elementor classes and inline styles.

        Args:
            element: BeautifulSoup Tag to clean

        Returns:
            Cleaned HTML as string
        """
        # Create a copy to avoid modifying original
        element_copy = element.__copy__()

        # Remove Elementor classes and clean attributes
        for tag in element_copy.find_all(True):
            # Remove class attribute if it contains Elementor classes
            if 'class' in tag.attrs:
                classes = tag.attrs['class']
                # Filter out Elementor classes
                cleaned_classes = [
                    c for c in classes
                    if not any(ec in c for ec in self.ELEMENTOR_CLASSES)
                ]

                if cleaned_classes:
                    tag.attrs['class'] = cleaned_classes
                else:
                    del tag.attrs['class']

            # Remove inline styles
            if 'style' in tag.attrs:
                del tag.attrs['style']

            # Remove data attributes
            attrs_to_remove = [
                attr for attr in tag.attrs.keys()
                if attr.startswith('data-')
            ]
            for attr in attrs_to_remove:
                del tag.attrs[attr]

            # Remove IDs (usually Elementor-generated)
            if 'id' in tag.attrs:
                # Keep IDs that might be useful (anchors)
                if not tag.attrs['id'].startswith('elementor-'):
                    pass  # Keep it
                else:
                    del tag.attrs['id']

        # Convert to string
        html_string = str(element_copy)

        # Remove empty paragraphs and divs
        html_string = re.sub(r'<p>\s*</p>', '', html_string)
        html_string = re.sub(r'<div>\s*</div>', '', html_string)

        # Remove excessive whitespace
        html_string = re.sub(r'\n\s*\n', '\n', html_string)

        return html_string.strip()

    def extract_meta_data(self) -> Dict[str, any]:
        """
        Extract metadata from the page (title, SEO, etc.).

        Returns:
            Dictionary with metadata fields
        """
        meta = {}

        # Extract title
        title_tag = self.soup.find('title')
        if title_tag:
            meta['title'] = title_tag.get_text(strip=True)

        # Extract meta description
        desc_tag = self.soup.find('meta', attrs={'name': 'description'})
        if desc_tag and desc_tag.get('content'):
            meta['description'] = desc_tag['content']

        # Extract Open Graph title
        og_title = self.soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            meta['og_title'] = og_title['content']

        # Extract canonical URL
        canonical = self.soup.find('link', rel='canonical')
        if canonical and canonical.get('href'):
            meta['canonical_url'] = canonical['href']

        return meta


class FundedLoanExtractor(WordPressContentExtractor):
    """
    Specialized extractor for Funded Loan case study pages.

    Extends WordPressContentExtractor with additional logic
    for extracting loan-specific details.
    """

    def extract_loan_details(self) -> Dict[str, any]:
        """
        Extract structured loan details from the page.

        Returns:
            Dictionary with loan_amount, loan_type, property_type, location, etc.
        """
        details = {}

        # Try to extract loan amount from common patterns
        text_content = self.soup.get_text()

        # Pattern: $XXX,XXX or $X.XM
        amount_match = re.search(r'\$([0-9,]+(?:\.[0-9]+)?(?:M|K)?)', text_content)
        if amount_match:
            amount_str = amount_match.group(1).replace(',', '')
            if amount_str.endswith('M'):
                amount = float(amount_str[:-1]) * 1_000_000
            elif amount_str.endswith('K'):
                amount = float(amount_str[:-1]) * 1_000
            else:
                amount = float(amount_str)
            details['loan_amount'] = amount

        # Try to extract property type
        property_patterns = [
            'single family', 'multi-family', 'multifamily', 'commercial',
            'residential', 'condo', 'townhouse', 'investment property'
        ]
        for pattern in property_patterns:
            if pattern.lower() in text_content.lower():
                details['property_type'] = pattern.title()
                break

        # Try to extract location (city, state)
        # Pattern: City, STATE or City, State
        location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)', text_content)
        if location_match:
            details['location'] = f"{location_match.group(1)}, {location_match.group(2)}"

        return details
