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
    Body: {
        "property_state": "CA",
        "loan_amount": 500000,
        "credit_score": 720,
        "property_value": 650000,
        "property_type": "residential" (optional),
        "entity_type": "individual" (optional),
        "loan_purpose": "purchase" (optional),
        "occupancy": "owner occupied" (optional)
    }

    Returns: {
        "quotes": [
            {
                "lender": "Lender Name",
                "program": "Program Type Name",
                "rate_range": "6.500% - 7.250%",
                "points_range": "0.00 - 2.00",
                "min_loan": 75000.00,
                "max_loan": 2000000.00
            }
        ],
        "ltv": 76.92,
        "loan_amount": 500000,
        "property_value": 650000
    }
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

        # Get matching loan programs
        try:
            matches = LoanMatchingService.get_best_rates(
                qualification_data,
                limit=10
            )

            # Format results
            results = []
            for match in matches:
                results.append({
                    'lender': match.lender.company_name,
                    'program': match.program_type.name,
                    'rate_range': match.rate_range,
                    'points_range': match.points_range,
                    'min_loan': float(match.min_loan),
                    'max_loan': float(match.max_loan),
                    'lender_fee': float(match.lender_fee),
                })

            return Response({
                'quotes': results,
                'ltv': round(ltv, 2),
                'loan_amount': loan_amount,
                'property_value': property_value,
                'matches_found': len(results)
            })

        except Exception as e:
            return Response(
                {
                    'error': 'Error matching loan programs',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
