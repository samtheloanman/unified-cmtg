# CMS Services Package

This package contains utility services for content migration from WordPress to Wagtail CMS.

## Overview

The services in this package handle:
1. **Content Extraction** - Parsing WordPress/Elementor HTML into structured content
2. **Media Management** - Resolving and importing WordPress media files
3. **Location Mapping** - Migrating location data with geographic calculations

## Services

### 1. Content Extractor (`content_extractor.py`)

Extracts structured content from WordPress pages built with Elementor.

#### WordPressContentExtractor

**Purpose**: Parse HTML and map H2 sections to Wagtail RichTextField fields.

**Usage**:
```python
from cms.services import WordPressContentExtractor

# Initialize with HTML content
extractor = WordPressContentExtractor(html_content)

# Extract for specific model
content = extractor.extract_for_model(ProgramPage)
# Returns: {'mortgage_program_highlights': '<p>...</p>', 'what_are': '...', ...}

# Extract metadata
meta = extractor.extract_meta_data()
# Returns: {'title': '...', 'description': '...', ...}
```

**Section Mapping**:
| H2 Heading Pattern | Wagtail Field |
|-------------------|---------------|
| "Key Features" | `mortgage_program_highlights` |
| "What are..." | `what_are` |
| "Benefits" | `benefits_of` |
| "How to Qualify" | `how_to_qualify_for` |
| "Why Choose" | `why_us` |
| "FAQ" | `program_faq` |
| "Requirements" | `requirements` |
| "Details" | `details_about_mortgage_loan_program` |

**Features**:
- Cleans Elementor markup (classes, inline styles, data attributes)
- Preserves semantic HTML (p, ul, ol, h3-h6)
- Removes empty elements
- Returns cleaned HTML ready for RichTextField

#### FundedLoanExtractor

**Purpose**: Extract loan details from funded loan case study pages.

**Usage**:
```python
from cms.services import FundedLoanExtractor

extractor = FundedLoanExtractor(html_content)
details = extractor.extract_loan_details()
# Returns: {
#     'loan_amount': 500000.00,
#     'property_type': 'Single Family',
#     'location': 'Los Angeles, CA',
#     'description': '...'
# }
```

---

### 2. Media Resolver (`media_resolver.py`)

Handles WordPress media URL resolution and import preparation.

#### MediaResolver

**Purpose**: Extract and resolve WordPress image URLs to local paths.

**Usage**:
```python
from cms.services import MediaResolver

resolver = MediaResolver('https://custommortgageinc.com')

# Extract images from HTML
images = resolver.extract_images_from_html(html_content)
# Returns: [
#     {
#         'src': 'https://example.com/wp-content/uploads/2024/01/image.jpg',
#         'alt': 'Alt text',
#         'local_path': 'wp-content/uploads/2024/01/image.jpg',
#         'filename': 'image.jpg'
#     },
#     ...
# ]

# Parse responsive images
srcset_images = resolver.resolve_srcset(srcset_attribute)

# Get image metadata
metadata = resolver.get_image_metadata_from_url(image_url)
# Returns: {'year': 2024, 'month': 1, 'filename': '...', ...}
```

#### MediaImporter

**Purpose**: Coordinate image downloads and Wagtail Image creation.

**Usage**:
```python
from cms.services import MediaImporter

importer = MediaImporter(media_resolver)

# Import images for a page (placeholder - implement download logic)
updated_html, wagtail_images = importer.import_images_for_page(html, page_model)
```

**Features**:
- Extracts all `<img>` tags from HTML
- Resolves WordPress uploads to local paths
- Parses srcset for responsive images
- Provides metadata extraction (year, month, dimensions)
- URL replacement functionality

---

### 3. Location Mapper (`location_mapper.py`)

Handles WordPress location data migration and geographic calculations.

#### LocationMapper

**Purpose**: Parse WordPress location SQL dumps and map to Wagtail Location model.

**Usage**:
```python
from cms.services import LocationMapper

mapper = LocationMapper()

# Parse SQL dump
sql_content = open('wp_cmtg_locations.sql').read()
wp_locations = mapper.parse_sql_insert(sql_content)

# Map to Wagtail format
wagtail_locations = [
    mapper.map_to_wagtail_location(loc) for loc in wp_locations
]

# Create Location pages
for location_data in wagtail_locations:
    Location.objects.create(**location_data)
```

**WordPress Location Schema**:
```sql
CREATE TABLE wp_cmtg_locations (
    id INT,
    city VARCHAR(255),
    state VARCHAR(2),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    target_url VARCHAR(255),
    meta_title TEXT,
    meta_description TEXT
);
```

#### DistanceCalculator

**Purpose**: Calculate distances between geographic coordinates using Haversine formula.

**Usage**:
```python
from cms.services import DistanceCalculator

calc = DistanceCalculator()

# Calculate distance between two points
distance = calc.haversine_distance(
    lat1=34.0522, lon1=-118.2437,  # LA
    lat2=37.7749, lon2=-122.4194,  # SF
    unit='mi'  # or 'km'
)
# Returns: 347.21 (miles)

# Find nearest locations
locations = [...]  # List of dicts with 'latitude' and 'longitude'
nearest = calc.find_nearest_locations(
    origin_lat=35.0,
    origin_lon=-120.0,
    locations=locations,
    max_distance=100,  # Optional: only within 100 miles
    limit=5,           # Return top 5
    unit='mi'
)
# Returns: [(location_dict, distance), ...]
```

**Features**:
- Haversine formula for great-circle distance
- Supports miles and kilometers
- Find nearest N locations
- Filter by maximum distance
- Returns sorted by proximity

---

## Testing

### Test Content Extractor

```bash
# Manual test on live WordPress page
cd backend
python cms/services/test_extractor.py
```

**Output**:
```
🚀 WordPress Content Extractor Test Suite

Fetching: https://custommortgageinc.com/loan-programs/super-jumbo-residential-mortgage-loans/
----------------------------------------------------------------------
Received 45821 bytes

Page Title: Super Jumbo Residential Mortgage Loans | Custom Mortgage Inc
----------------------------------------------------------------------

=== Extracting Content Sections ===

📄 mortgage_program_highlights:
----------------------------------------------------------------------
<p>Loan amounts from $1,000,000 to $20,000,000+...</p>
...

Coverage: 87.5% (7/8 fields)
✅ Tests complete!
```

### Test Media Resolver

```python
from cms.services import MediaResolver

resolver = MediaResolver('https://custommortgageinc.com')
html = '<img src="/wp-content/uploads/2024/01/sample.jpg" alt="Sample">'
images = resolver.extract_images_from_html(html)
print(images[0]['local_path'])
# Output: wp-content/uploads/2024/01/sample.jpg
```

### Test Location Mapper

```python
from cms.services import LocationMapper, DistanceCalculator

mapper = LocationMapper()
calc = DistanceCalculator()

# Parse SQL
locations = mapper.parse_sql_insert(sql_dump)

# Calculate distance
distance = calc.haversine_distance(34.0522, -118.2437, 37.7749, -122.4194)
print(f"LA to SF: {distance:.2f} miles")
# Output: LA to SF: 347.21 miles
```

---

## Integration with Scraper

Jules' scraper (`scrape_content.py`) uses these services:

```python
from cms.services import WordPressContentExtractor

# In scrape_content.py
response = requests.get(page.source_url)
extractor = WordPressContentExtractor(response.content)
content = extractor.extract_for_model(page.__class__)

# Update page fields
for field_name, value in content.items():
    setattr(page, field_name, value)

page.save_revision().publish()
```

---

## File Structure

```
cms/services/
├── __init__.py                 # Package exports
├── content_extractor.py        # WordPressContentExtractor, FundedLoanExtractor
├── media_resolver.py           # MediaResolver, MediaImporter
├── location_mapper.py          # LocationMapper, DistanceCalculator
├── test_extractor.py           # Manual testing script
└── README.md                   # This file
```

---

## Dependencies

**Python Packages**:
- `beautifulsoup4` - HTML parsing
- `lxml` - Fast HTML parser backend
- `requests` - HTTP client for fetching pages

**Install**:
```bash
pip install beautifulsoup4 lxml requests
```

---

## Common Patterns

### Extract and Save Content

```python
from cms.services import WordPressContentExtractor
from cms.models import ProgramPage

# Fetch HTML
response = requests.get(url)

# Extract content
extractor = WordPressContentExtractor(response.content)
content = extractor.extract_for_model(ProgramPage)

# Update page
page = ProgramPage.objects.get(slug='super-jumbo')
for field, html in content.items():
    setattr(page, field, html)

page.save_revision().publish()
```

### Import Images

```python
from cms.services import MediaResolver, MediaImporter

resolver = MediaResolver('https://custommortgageinc.com')
importer = MediaImporter(resolver)

# Extract images from content
images = resolver.extract_images_from_html(html_content)

# Download and import (implement download logic)
for image in images:
    # Download from image['src']
    # Create Wagtail Image
    # Update image references in HTML
    pass
```

### Find Nearby Locations

```python
from cms.services import LocationMapper, DistanceCalculator

# User's location
user_lat, user_lon = 34.0522, -118.2437  # LA

# All locations
all_locations = Location.objects.all().values('city', 'state', 'latitude', 'longitude')

# Find nearest 5
calc = DistanceCalculator()
nearest = calc.find_nearest_locations(
    user_lat, user_lon,
    list(all_locations),
    max_distance=50,  # Within 50 miles
    limit=5
)

for location, distance in nearest:
    print(f"{location['city']}, {location['state']}: {distance:.1f} miles")
```

---

## Future Enhancements

- [ ] Implement actual image download in `MediaImporter`
- [ ] Add video embed extraction
- [ ] Add schema.org markup extraction
- [ ] Add automatic alt text generation for images
- [ ] Add content versioning/comparison
- [ ] Add bulk location import management command
- [ ] Add location search by city/state name
- [ ] Add location clustering for map display

---

## Troubleshooting

### Content Not Extracted

**Problem**: `extract_program_content()` returns empty dict

**Solutions**:
1. Check if page has H2 headings
2. Verify heading text matches patterns in `SECTION_PATTERNS`
3. Run test script to see raw HTML structure
4. Check for Elementor wrapper divs hiding content

### Images Not Found

**Problem**: `extract_images_from_html()` returns empty list

**Solutions**:
1. Verify images are from `wp-content/uploads` path
2. Check if `<img>` tags have `src` attribute
3. Ensure URLs are absolute or properly relative
4. Check for lazy-loading data attributes instead of src

### Location Import Fails

**Problem**: SQL parsing returns no locations

**Solutions**:
1. Verify SQL dump format matches expected pattern
2. Check for escaped quotes in city/state names
3. Ensure INSERT statement has correct column order
4. Try parsing sample SQL first

---

## Performance Considerations

### Content Extraction
- Uses lxml parser (fastest BeautifulSoup backend)
- In-memory HTML processing (no file I/O)
- Regex compilation happens once per class

### Media Resolution
- Image extraction is O(n) where n = number of images
- No network calls in extraction (deferred to import)
- URL parsing is lightweight

### Location Calculations
- Haversine formula is O(1) per calculation
- Finding nearest is O(n) where n = total locations
- Consider database-level geo queries for large datasets

---

**Last Updated**: 2026-01-13
**Maintained By**: Claude (L2 Agent)
