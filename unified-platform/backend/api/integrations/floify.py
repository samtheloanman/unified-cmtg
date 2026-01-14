"""
Floify API Client

Handles integration with Floify's loan origination system (LOS).
Provides methods for creating prospects, fetching application data,
and processing webhook events.

API Documentation: https://api.floify.com/docs
"""

import httpx
import logging
from decimal import Decimal
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class FloifyAPIError(Exception):
    """Raised when Floify API call fails."""
    pass


class FloifyClient:
    """
    Client for Floify API integration.

    Handles:
    - Creating prospects (leads)
    - Fetching application data (1003 format)
    - Processing webhook events

    Usage:
        client = FloifyClient()
        prospect = client.create_prospect(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="555-123-4567",
            loan_amount=500000
        )
    """

    BASE_URL = "https://api.floify.com/v2019-11"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Floify client.

        Args:
            api_key: Floify Integration API key (defaults to settings.FLOIFY_API_KEY)
        """
        self.api_key = api_key or getattr(settings, 'FLOIFY_API_KEY', None)

        if not self.api_key:
            logger.warning("FLOIFY_API_KEY not configured")

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                'X-API-KEY': self.api_key or '',
                'Content-Type': 'application/json',
            },
            timeout=30.0
        )

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """
        Convert Django types to JSON-serializable types.

        Args:
            value: Value to serialize

        Returns:
            JSON-serializable value
        """
        if isinstance(value, Decimal):
            return float(value)
        return value

    def _sanitize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize payload to ensure all values are JSON-serializable.

        Args:
            payload: Dictionary with potential Decimal or other Django types

        Returns:
            Dictionary with JSON-serializable values
        """
        return {key: self._serialize_value(val) for key, val in payload.items()}

    def create_prospect(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: Optional[str] = None,
        loan_amount: Optional[int] = None,
        property_address: Optional[str] = None,
        loan_purpose: Optional[str] = None,
        **extra_fields
    ) -> Dict[str, Any]:
        """
        Create a new prospect in Floify.

        Floify will send the prospect an email invitation to complete
        their loan application on custommortgage.floify.com.

        Args:
            first_name: Borrower's first name
            last_name: Borrower's last name
            email: Email address (required)
            phone: Mobile phone number
            loan_amount: Requested loan amount
            property_address: Subject property address
            loan_purpose: purchase, refinance, cash_out
            **extra_fields: Additional Floify prospect fields

        Returns:
            Floify prospect response with ID and status

        Raises:
            FloifyAPIError: If API call fails

        Example:
            >>> client = FloifyClient()
            >>> prospect = client.create_prospect(
            ...     first_name="Jane",
            ...     last_name="Smith",
            ...     email="jane@example.com",
            ...     loan_amount=350000,
            ...     loan_purpose="purchase"
            ... )
            >>> print(prospect['id'])
            'prospect_abc123'
        """
        payload = {
            'firstName': first_name,
            'lastName': last_name,
            'email': email,
        }

        if phone:
            payload['mobilePhoneNumber'] = phone
        if loan_amount:
            payload['loanAmount'] = loan_amount
        if property_address:
            payload['subjectPropertyAddress'] = property_address
        if loan_purpose:
            payload['loanPurpose'] = loan_purpose

        # Add any extra fields
        payload.update(extra_fields)

        # Sanitize payload to ensure all values are JSON-serializable
        sanitized_payload = self._sanitize_payload(payload)

        # Check if API key is configured
        if not self.api_key:
            raise FloifyAPIError("FLOIFY_API_KEY is not configured. Please set the FLOIFY_API_KEY environment variable.")

        try:
            logger.info(f"Creating Floify prospect: {email}")
            response = self.client.post('/prospects', json=sanitized_payload)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Created Floify prospect: {data.get('id')}")
            return data

        except httpx.HTTPStatusError as e:
            error_detail = self._extract_error_message(e.response)
            logger.error(f"Floify API error: {error_detail}")
            raise FloifyAPIError(f"HTTP {e.response.status_code}: {error_detail}")

        except httpx.HTTPError as e:
            logger.error(f"Floify network error: {e}")
            raise FloifyAPIError(f"Network error: {str(e)}")

    def get_application(self, loan_id: str) -> Dict[str, Any]:
        """
        Fetch full application data for a loan.

        Args:
            loan_id: Floify loan ID

        Returns:
            Complete loan application data

        Raises:
            FloifyAPIError: If API call fails
        """
        try:
            logger.info(f"Fetching Floify application: {loan_id}")
            response = self.client.get(f'/loans/{loan_id}')
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_detail = self._extract_error_message(e.response)
            logger.error(f"Floify API error fetching loan {loan_id}: {error_detail}")
            raise FloifyAPIError(f"HTTP {e.response.status_code}: {error_detail}")

        except httpx.HTTPError as e:
            logger.error(f"Floify network error: {e}")
            raise FloifyAPIError(f"Network error: {str(e)}")

    def get_1003_json(self, loan_id: str) -> Dict[str, Any]:
        """
        Fetch application in URLA (1003) JSON schema format.

        The 1003 format is the Uniform Residential Loan Application
        standard format used by mortgage lenders.

        Args:
            loan_id: Floify loan ID

        Returns:
            Application data in 1003 JSON format

        Raises:
            FloifyAPIError: If API call fails
        """
        try:
            logger.info(f"Fetching Floify 1003 JSON: {loan_id}")
            response = self.client.get(f'/loans/{loan_id}/1003')
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_detail = self._extract_error_message(e.response)
            logger.error(f"Floify API error fetching 1003 {loan_id}: {error_detail}")
            raise FloifyAPIError(f"HTTP {e.response.status_code}: {error_detail}")

        except httpx.HTTPError as e:
            logger.error(f"Floify network error: {e}")
            raise FloifyAPIError(f"Network error: {str(e)}")

    def get_prospect(self, prospect_id: str) -> Dict[str, Any]:
        """
        Fetch prospect details by ID.

        Args:
            prospect_id: Floify prospect ID

        Returns:
            Prospect data

        Raises:
            FloifyAPIError: If API call fails
        """
        try:
            logger.info(f"Fetching Floify prospect: {prospect_id}")
            response = self.client.get(f'/prospects/{prospect_id}')
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_detail = self._extract_error_message(e.response)
            logger.error(f"Floify API error fetching prospect {prospect_id}: {error_detail}")
            raise FloifyAPIError(f"HTTP {e.response.status_code}: {error_detail}")

        except httpx.HTTPError as e:
            logger.error(f"Floify network error: {e}")
            raise FloifyAPIError(f"Network error: {str(e)}")

    def _extract_error_message(self, response: httpx.Response) -> str:
        """
        Extract error message from Floify API response.

        Args:
            response: HTTP response object

        Returns:
            Human-readable error message
        """
        try:
            error_data = response.json()
            return error_data.get('message', str(error_data))
        except Exception:
            return response.text or 'Unknown error'

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes HTTP client."""
        self.client.close()

    def close(self):
        """Close the HTTP client connection."""
        self.client.close()
