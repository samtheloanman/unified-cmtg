"""
Test Floify API Integration
P0: Critical - Ensures lead submission to Floify works correctly
"""
import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
import httpx

from api.integrations.floify import FloifyClient, FloifyAPIError
from applications.models import Application


@pytest.fixture
def floify_client():
    """Create FloifyClient with mock API key"""
    return FloifyClient(api_key="test-api-key-123")


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx.Client"""
    with patch('api.integrations.floify.httpx.Client') as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.mark.integration
class TestFloifyClient:
    """Test FloifyClient initialization and configuration"""

    def test_client_initialization_with_api_key(self):
        """Test that client initializes with provided API key"""
        client = FloifyClient(api_key="test-key-456")
        assert client.api_key == "test-key-456"

    def test_client_initialization_from_settings(self):
        """Test that client uses settings.FLOIFY_API_KEY if not provided"""
        with patch('api.integrations.floify.settings') as mock_settings:
            mock_settings.FLOIFY_API_KEY = "settings-key-789"
            client = FloifyClient()
            assert client.api_key == "settings-key-789"

    def test_client_initialization_without_api_key_warns(self):
        """Test that client logs warning when API key is missing"""
        with patch('api.integrations.floify.settings') as mock_settings, \
             patch('api.integrations.floify.logger') as mock_logger:
            mock_settings.FLOIFY_API_KEY = None
            client = FloifyClient()
            mock_logger.warning.assert_called_once()
            assert client.api_key is None

    def test_base_url_correct(self, floify_client):
        """Test that BASE_URL is set correctly"""
        assert floify_client.BASE_URL == "https://api.floify.com/v2019-11"


@pytest.mark.integration
class TestCreateProspect:
    """Test prospect creation (lead submission)"""

    def test_create_prospect_success(self, floify_client, mock_httpx_client):
        """Test successful prospect creation with minimal fields"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 'prospect_abc123',
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'status': 'created',
            'createdAt': '2026-01-17T12:00:00Z'
        }
        mock_httpx_client.post.return_value = mock_response

        # Create FloifyClient with mocked httpx.Client
        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="test-key")

            # Call create_prospect
            result = client.create_prospect(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com"
            )

        # Verify API call
        mock_httpx_client.post.assert_called_once()
        call_args = mock_httpx_client.post.call_args
        assert call_args[0][0] == '/prospects'

        # Verify payload
        payload = call_args[1]['json']
        assert payload['firstName'] == 'John'
        assert payload['lastName'] == 'Doe'
        assert payload['email'] == 'john.doe@example.com'

        # Verify result
        assert result['id'] == 'prospect_abc123'
        assert result['status'] == 'created'

    def test_create_prospect_with_all_fields(self, floify_client, mock_httpx_client):
        """Test prospect creation with all optional fields"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            'id': 'prospect_xyz789',
            'firstName': 'Jane',
            'lastName': 'Smith',
            'email': 'jane.smith@example.com',
            'mobilePhoneNumber': '555-123-4567',
            'loanAmount': 500000,
            'subjectPropertyAddress': '123 Main St, Los Angeles, CA 90001',
            'loanPurpose': 'purchase'
        }
        mock_httpx_client.post.return_value = mock_response

        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="test-key")

            result = client.create_prospect(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone="555-123-4567",
                loan_amount=500000,
                property_address="123 Main St, Los Angeles, CA 90001",
                loan_purpose="purchase"
            )

        # Verify payload includes all fields
        payload = mock_httpx_client.post.call_args[1]['json']
        assert payload['mobilePhoneNumber'] == '555-123-4567'
        assert payload['loanAmount'] == 500000
        assert payload['subjectPropertyAddress'] == '123 Main St, Los Angeles, CA 90001'
        assert payload['loanPurpose'] == 'purchase'

    def test_create_prospect_without_api_key_raises_error(self):
        """Test that create_prospect raises error when API key is missing"""
        with patch('api.integrations.floify.settings') as mock_settings:
            # Typechecking mock attribute needs to be handled carefully or just use a new client with empty settings
            mock_settings.FLOIFY_API_KEY = None
            # We must pass empty string or None to override any potential env var, 
            # but since we mocked settings, getattr(settings) will return None if we set it so.
            # But the init logic is: api_key or getattr(...). 
            # So passing None to init + mocking settings to None = None.
            
            client = FloifyClient(api_key=None)

            with pytest.raises(FloifyAPIError, match="FLOIFY_API_KEY is not configured"):
                client.create_prospect(
                    first_name="John",
                    last_name="Doe",
                    email="john@example.com"
                )

    def test_create_prospect_http_error_400(self, mock_httpx_client):
        """Test handling of HTTP 400 Bad Request"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'message': 'Invalid email address format'
        }

        http_error = httpx.HTTPStatusError(
            "Bad Request",
            request=Mock(),
            response=mock_response
        )
        mock_httpx_client.post.side_effect = http_error

        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="test-key")

            with pytest.raises(FloifyAPIError, match="HTTP 400.*Invalid email"):
                client.create_prospect(
                    first_name="John",
                    last_name="Doe",
                    email="invalid-email"
                )

    def test_create_prospect_http_error_401(self, mock_httpx_client):
        """Test handling of HTTP 401 Unauthorized (invalid API key)"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            'message': 'Invalid API key'
        }

        http_error = httpx.HTTPStatusError(
            "Unauthorized",
            request=Mock(),
            response=mock_response
        )
        mock_httpx_client.post.side_effect = http_error

        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="bad-key")

            with pytest.raises(FloifyAPIError, match="HTTP 401.*Invalid API key"):
                client.create_prospect(
                    first_name="John",
                    last_name="Doe",
                    email="john@example.com"
                )

    def test_create_prospect_network_error(self, mock_httpx_client):
        """Test handling of network errors"""
        mock_httpx_client.post.side_effect = httpx.NetworkError("Connection refused")

        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="test-key")

            with pytest.raises(FloifyAPIError, match="Network error.*Connection refused"):
                client.create_prospect(
                    first_name="John",
                    last_name="Doe",
                    email="john@example.com"
                )

    def test_create_prospect_serializes_decimal(self, mock_httpx_client):
        """Test that Decimal values are serialized to float"""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 'prospect_123'}
        mock_httpx_client.post.return_value = mock_response

        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="test-key")

            # Pass Decimal as loan_amount
            client.create_prospect(
                first_name="John",
                last_name="Doe",
                email="john@example.com",
                loan_amount=Decimal("500000.00")
            )

        # Verify Decimal was converted to float
        payload = mock_httpx_client.post.call_args[1]['json']
        assert isinstance(payload['loanAmount'], (int, float))
        assert payload['loanAmount'] == 500000.0


@pytest.mark.integration
class TestGetApplication:
    """Test fetching application data"""

    def test_get_application_success(self, mock_httpx_client):
        """Test successful application fetch"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'loanId': 'loan_456',
            'prospectId': 'prospect_123',
            'status': 'in_progress',
            'borrower': {
                'firstName': 'John',
                'lastName': 'Doe'
            },
            'loanAmount': 500000
        }
        mock_httpx_client.get.return_value = mock_response

        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="test-key")

            result = client.get_application('loan_456')

        mock_httpx_client.get.assert_called_once_with('/loans/loan_456')
        assert result['loanId'] == 'loan_456'
        assert result['status'] == 'in_progress'

    def test_get_application_not_found(self, mock_httpx_client):
        """Test handling of 404 Not Found"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {'message': 'Loan not found'}

        http_error = httpx.HTTPStatusError(
            "Not Found",
            request=Mock(),
            response=mock_response
        )
        mock_httpx_client.get.side_effect = http_error

        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="test-key")

            with pytest.raises(FloifyAPIError, match="HTTP 404.*Loan not found"):
                client.get_application('nonexistent_loan')


@pytest.mark.integration
class TestGet1003JSON:
    """Test fetching 1003 (URLA) application data"""

    def test_get_1003_json_success(self, mock_httpx_client):
        """Test successful 1003 JSON fetch"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'version': '1.7.1',
            'borrower': {
                'firstName': 'John',
                'lastName': 'Doe',
                'ssn': 'xxx-xx-1234'
            },
            'property': {
                'address': '123 Main St',
                'value': 750000
            }
        }
        mock_httpx_client.get.return_value = mock_response

        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="test-key")

            result = client.get_1003_json('loan_789')

        mock_httpx_client.get.assert_called_once_with('/loans/loan_789/1003')
        assert result['version'] == '1.7.1'
        assert result['borrower']['firstName'] == 'John'


@pytest.mark.integration
class TestGetProspect:
    """Test fetching prospect data"""

    def test_get_prospect_success(self, mock_httpx_client):
        """Test successful prospect fetch"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': 'prospect_123',
            'firstName': 'Jane',
            'lastName': 'Smith',
            'email': 'jane@example.com',
            'status': 'invited'
        }
        mock_httpx_client.get.return_value = mock_response

        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client_class.return_value = mock_httpx_client
            client = FloifyClient(api_key="test-key")

            result = client.get_prospect('prospect_123')

        mock_httpx_client.get.assert_called_once_with('/prospects/prospect_123')
        assert result['id'] == 'prospect_123'
        assert result['email'] == 'jane@example.com'


@pytest.mark.integration
class TestContextManager:
    """Test context manager protocol"""

    def test_context_manager_closes_client(self):
        """Test that client closes when used as context manager"""
        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            with FloifyClient(api_key="test-key") as client:
                pass

            mock_client.close.assert_called_once()

    def test_manual_close(self):
        """Test manual close() method"""
        with patch('api.integrations.floify.httpx.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            client = FloifyClient(api_key="test-key")
            client.close()

            mock_client.close.assert_called_once()


@pytest.mark.integration
class TestApplicationModel:
    """Test Application model integration with Floify"""

    def test_application_creation_from_floify(self, db):
        """Test creating Application from Floify prospect response"""
        floify_data = {
            'id': 'prospect_abc123',
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'mobilePhoneNumber': '555-123-4567',
            'loanAmount': 500000,
            'subjectPropertyAddress': '123 Main St, CA',
            'loanPurpose': 'purchase'
        }

        app = Application.objects.create(
            floify_id=floify_data['id'],
            borrower_email=floify_data['email'],
            borrower_first_name=floify_data['firstName'],
            borrower_last_name=floify_data['lastName'],
            borrower_phone=floify_data['mobilePhoneNumber'],
            loan_amount=Decimal(str(floify_data['loanAmount'])),
            property_address=floify_data['subjectPropertyAddress'],
            loan_purpose=floify_data['loanPurpose'],
            floify_data=floify_data
        )

        assert app.floify_id == 'prospect_abc123'
        assert app.full_name == 'John Doe'
        assert app.loan_amount == Decimal('500000.00')
        assert app.status == 'created'

    def test_application_update_from_floify(self, db):
        """Test updating Application from Floify data"""
        app = Application.objects.create(
            floify_id='prospect_123',
            borrower_email='old@example.com',
            borrower_first_name='Old',
            borrower_last_name='Name'
        )

        updated_data = {
            'id': 'prospect_123',
            'firstName': 'John',
            'lastName': 'Doe',
            'email': 'john.doe@example.com',
            'loanAmount': 600000,
            'loanId': 'loan_456'
        }

        app.update_from_floify(updated_data)
        app.save()

        assert app.borrower_email == 'john.doe@example.com'
        assert app.borrower_first_name == 'John'
        assert app.loan_amount == 600000
        assert app.floify_loan_id == 'loan_456'
        assert app.floify_data == updated_data

    def test_application_status_color_mapping(self, db):
        """Test status color badge mapping"""
        app = Application.objects.create(
            floify_id='prospect_123',
            borrower_email='test@example.com',
            borrower_first_name='Test',
            borrower_last_name='User',
            status='approved'
        )

        assert app.status_display_color == 'success'

        app.status = 'denied'
        assert app.status_display_color == 'danger'

        app.status = 'in_progress'
        assert app.status_display_color == 'primary'
