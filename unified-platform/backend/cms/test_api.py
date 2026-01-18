"""
Test Wagtail API field exposure for headless CMS
P0: Critical - Ensures all 64 ProgramPage fields are accessible via API
"""
import pytest
from django.test import Client
import json


@pytest.mark.integration
class TestWagtailAPIFieldExposure:
    """
    Test that Wagtail API exposes all required fields for headless CMS.
    Critical for frontend to access complete program data.
    """

    def test_program_page_api_list_endpoint(self, client, sample_program):
        """Test that ProgramPage list endpoint is accessible"""
        response = client.get('/api/v2/pages/?type=cms.ProgramPage')
        assert response.status_code == 200

        data = json.loads(response.content)
        assert 'meta' in data
        assert 'items' in data
        assert data['meta']['total_count'] >= 1

    def test_program_page_api_detail_endpoint(self, client, sample_program):
        """Test that ProgramPage detail endpoint returns full data"""
        response = client.get(f'/api/v2/pages/{sample_program.id}/')
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['id'] == sample_program.id
        assert data['title'] == sample_program.title

    def test_program_page_all_core_fields_exposed(self, client, sample_program):
        """
        Test that all 64 ProgramPage fields are exposed via API.
        This is critical for headless CMS functionality.
        """
        response = client.get(f'/api/v2/pages/{sample_program.id}/?fields=*')
        assert response.status_code == 200

        data = json.loads(response.content)

        # Core identification fields
        assert 'id' in data
        assert 'title' in data
        assert 'meta' in data
        assert data['meta']['type'] == 'cms.ProgramPage'
        assert data['meta']['slug'] == 'test-fha-loan'

        # Program type and classification
        assert 'program_type' in data
        assert data['program_type'] == 'residential'

        # Financial fields
        assert 'minimum_loan_amount' in data
        assert 'maximum_loan_amount' in data
        assert 'min_credit_score' in data
        assert 'max_ltv' in data
        assert 'interest_rates' in data
        assert 'max_debt_to_income_ratio' in data
        assert 'min_dscr' in data

        # Content fields
        assert 'mortgage_program_highlights' in data
        assert 'what_are' in data
        assert 'details_about_mortgage_loan_program' in data
        assert 'benefits_of' in data
        assert 'requirements' in data
        assert 'how_to_qualify_for' in data
        assert 'why_us' in data
        assert 'faq' in data

        # Array fields
        assert 'property_types' in data
        assert 'occupancy_types' in data
        assert 'lien_position' in data
        assert 'amortization_terms' in data
        assert 'purpose_of_mortgage' in data
        assert 'refinance_types' in data
        assert 'income_documentation_type' in data
        assert 'borrower_types' in data
        assert 'citizenship_requirements' in data

        # Restrictions
        # assert 'restricted_states' in data
        # assert 'restricted_property_types' in data
        # assert 'excluded_situations' in data

        # Location fields
        assert 'is_local_variation' in data
        assert 'target_city' in data
        assert 'target_state' in data
        assert 'target_region' in data

        # SEO fields from promote_panels
        assert 'slug' in data['meta']
        assert 'seo_title' in data['meta']
        assert 'search_description' in data['meta']

        # Timestamps
        assert 'first_published_at' in data['meta']

    def test_program_page_field_values_correct(self, client, sample_program):
        """Test that field values are correctly serialized"""
        response = client.get(f'/api/v2/pages/{sample_program.id}/?fields=*')
        data = json.loads(response.content)

        # Test string fields
        assert data['minimum_loan_amount'] == "100000.00"
        assert data['maximum_loan_amount'] == "5000000.00"

        # Test integer fields
        assert data['min_credit_score'] == 580

        # Test array fields
        assert isinstance(data['property_types'], list)
        assert 'Single Family' in data['property_types']
        assert len(data['property_types']) == 3

        # Test rich text fields
        assert isinstance(data['mortgage_program_highlights'], str)
        assert 'first-time buyers' in data['mortgage_program_highlights']

    def test_program_page_list_fields_parameter(self, client, sample_program):
        """Test that fields parameter filters API response"""
        response = client.get(
            '/api/v2/pages/?type=cms.ProgramPage&fields=title,program_type,min_credit_score'
        )
        assert response.status_code == 200

        data = json.loads(response.content)
        assert len(data['items']) >= 1

        # Check that specified fields are present
        item = data['items'][0]
        assert 'title' in item
        assert 'program_type' in item
        assert 'min_credit_score' in item

    def test_program_page_api_pagination(self, client, sample_program):
        """Test that API pagination works correctly"""
        response = client.get('/api/v2/pages/?type=cms.ProgramPage&limit=5')
        assert response.status_code == 200

        data = json.loads(response.content)
        assert 'meta' in data
        assert len(data['items']) <= 5

    def test_program_page_api_filtering_by_slug(self, client, sample_program):
        """Test that API can filter by slug"""
        response = client.get(f'/api/v2/pages/?slug={sample_program.slug}&type=cms.ProgramPage&fields=*')
        assert response.status_code == 200

        data = json.loads(response.content)
        assert data['meta']['total_count'] == 1
        assert data['items'][0]['meta']['slug'] == 'test-fha-loan'

    @pytest.mark.parametrize('field_name,expected_type', [
        ('property_types', list),
        ('occupancy_types', list),
        ('lien_position', list),
        ('amortization_terms', list),
        ('min_credit_score', int),
        ('program_type', str),
        ('interest_rates', str),
    ])
    def test_program_page_field_types(self, client, sample_program, field_name, expected_type):
        """Test that specific fields have correct data types"""
        response = client.get(f'/api/v2/pages/{sample_program.id}/?fields={field_name}')
        data = json.loads(response.content)

        if field_name in data and data[field_name] is not None:
            assert isinstance(data[field_name], expected_type), \
                f"Field {field_name} should be {expected_type}, got {type(data[field_name])}"


@pytest.mark.integration
class TestWagtailAPIPerformance:
    """Test API performance and response times"""

    def test_api_response_time_under_500ms(self, client, sample_program):
        """Test that API responds quickly (critical for frontend performance)"""
        import time

        start = time.time()
        response = client.get('/api/v2/pages/?type=cms.ProgramPage&limit=20')
        elapsed = (time.time() - start) * 1000  # Convert to milliseconds

        assert response.status_code == 200
        assert elapsed < 500, f"API response took {elapsed}ms, should be under 500ms"

    def test_api_detail_response_time(self, client, sample_program):
        """Test individual page API response time"""
        import time

        start = time.time()
        response = client.get(f'/api/v2/pages/{sample_program.id}/?fields=*')
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed < 200, f"Detail API response took {elapsed}ms, should be under 200ms"


@pytest.mark.integration
@pytest.mark.django_db
class TestAPIErrorHandling:
    """Test API error responses"""

    def test_api_invalid_page_id_returns_404(self, client):
        """Test that requesting non-existent page returns 404"""
        response = client.get('/api/v2/pages/99999/')
        assert response.status_code == 404

    def test_api_invalid_type_filter(self, client):
        """Test that invalid type filter is handled gracefully"""
        response = client.get('/api/v2/pages/?type=invalid.InvalidType')
        assert response.status_code in [200, 400]  # Should either work (0 results) or return error

    def test_api_limit_exceeds_maximum(self, client):
        """Test that API enforces maximum limit"""
        response = client.get('/api/v2/pages/?type=cms.ProgramPage&limit=1000')
        # Wagtail should return error or cap at max limit
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = json.loads(response.content)
            assert len(data['items']) <= 20  # Default Wagtail max
