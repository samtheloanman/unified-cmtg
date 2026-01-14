"""
Test the content extractor on live WordPress pages.

Usage:
    cd backend
    python cms/services/test_extractor.py
"""

import requests
from content_extractor import WordPressContentExtractor, FundedLoanExtractor


def test_program_extraction():
    """Test extraction on a real program page."""
    url = 'https://custommortgageinc.com/loan-programs/super-jumbo-residential-mortgage-loans/'

    print(f"Fetching: {url}")
    print("-" * 70)

    try:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; CMTGBot/1.0)'},
            timeout=30
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch page: {e}")
        return None

    print(f"Received {len(response.content)} bytes")

    extractor = WordPressContentExtractor(response.content)

    # Extract title
    title = extractor.extract_meta_data().get('title', 'No title found')
    print(f"\nPage Title: {title}")
    print("-" * 70)

    # Extract content sections
    print("\n=== Extracting Content Sections ===\n")

    content = extractor.extract_for_model(
        type('ProgramPage', (), {'__name__': 'ProgramPage'})
    )

    if not content:
        print("WARNING: No content extracted!")
        return None

    # Display results
    for field, html in content.items():
        print(f"\n📄 {field}:")
        print("-" * 70)

        # Show preview (first 300 chars)
        preview = html[:300].strip()
        if len(html) > 300:
            preview += "..."

        print(preview)
        print(f"\nLength: {len(html)} chars")

    # Summary
    print("\n" + "=" * 70)
    print(f"✅ SUCCESS: Extracted {len(content)} fields")
    print("=" * 70)

    return content


def test_funded_loan_extraction():
    """Test extraction on a funded loan page."""
    # Note: Update this URL to an actual funded loan page
    url = 'https://custommortgageinc.com/funded-loans/'  # Placeholder

    print(f"\nFetching funded loan: {url}")
    print("-" * 70)

    try:
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; CMTGBot/1.0)'},
            timeout=30
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch page: {e}")
        return None

    extractor = FundedLoanExtractor(response.content)
    details = extractor.extract_loan_details()

    print("\n=== Funded Loan Details ===\n")
    for key, value in details.items():
        print(f"{key}: {value}")

    return details


def test_comparison():
    """Test extraction and show what fields are populated."""
    print("\n" + "=" * 70)
    print("CONTENT EXTRACTION TEST - Field Coverage Report")
    print("=" * 70)

    content = test_program_extraction()

    if not content:
        print("\n❌ FAILED: No content extracted")
        return

    # Expected fields
    expected_fields = [
        'mortgage_program_highlights',
        'what_are',
        'benefits_of',
        'how_to_qualify_for',
        'why_us',
        'program_faq',
        'requirements',
        'details_about_mortgage_loan_program',
    ]

    print("\n=== Field Coverage ===\n")

    extracted_fields = set(content.keys())

    for field in expected_fields:
        if field in extracted_fields:
            length = len(content[field])
            print(f"✅ {field:40} ({length:5} chars)")
        else:
            print(f"❌ {field:40} (missing)")

    coverage = len(extracted_fields) / len(expected_fields) * 100
    print(f"\nCoverage: {coverage:.1f}% ({len(extracted_fields)}/{len(expected_fields)} fields)")


if __name__ == '__main__':
    print("\n🚀 WordPress Content Extractor Test Suite\n")

    # Test program page extraction
    test_comparison()

    # Optionally test funded loan extraction
    # Uncomment when you have a real funded loan URL:
    # test_funded_loan_extraction()

    print("\n✅ Tests complete!\n")
