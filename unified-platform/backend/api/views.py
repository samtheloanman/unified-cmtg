"""API views for the Unified CMTG Platform."""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from pricing.services.matching import LoanMatchingService

@api_view(['GET'])
def health_check(request):
    """Health check endpoint."""
    return Response({'status': 'healthy'})

@method_decorator(csrf_exempt, name='dispatch')
class QuoteView(APIView):
    """
    Loan quote API endpoint.

    POST /api/v1/quote/
    """
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Handle POST request for loan quotes."""
        data = request.data

        # Validate required fields
        required_fields = [
            'property_state',
            'loan_amount',
            'credit_score',
            'property_value'
        ]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return Response(
                {
                    'error': 'Missing required fields',
                    'missing': missing_fields
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate LTV
        try:
            loan_amount = float(data['loan_amount'])
            property_value = float(data['property_value'])
            ltv = (loan_amount / property_value) * 100
        except (ValueError, ZeroDivisionError) as e:
            return Response(
                {'error': f'Invalid numeric values: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Build qualification data
        qualification_data = {
            'state': data['property_state'],
            'property_type': data.get('property_type', 'residential'),
            'entity_type': data.get('entity_type', 'individual'),
            'purpose': data.get('loan_purpose', 'purchase'),
            'occupancy': data.get('occupancy', 'owner occupied'),
            'loan_amount': loan_amount,
            'ltv': ltv,
            'estimated_credit_score': int(data['credit_score'])
        }

        # Get matching loan programs with real pricing adjustments
        try:
            quotes = LoanMatchingService.get_quotes_with_adjustments(
                qualification_data,
                limit=10
            )

            return Response({
                'quotes': quotes,
                'ltv': round(ltv, 2),
                'loan_amount': loan_amount,
                'property_value': property_value,
                'matches_found': len(quotes)
            })

        except Exception as e:
            return Response(
                {
                    'error': 'Error matching loan programs',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
