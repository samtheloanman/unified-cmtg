from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from pricing.models import LenderProgramOffering, RateAdjustment

@api_view(['GET'])
def health_check(request):
    return Response({'status': 'healthy'})

class QuoteView(APIView):
    """
    POST /api/v1/quote/

    Calculate loan quotes.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Basic placeholder logic to return seeded data
        # In Phase 2, this will use the full matching engine

        data = request.data
        # Extract basic criteria (unused in this mock, but good for structure)
        # loan_amount = data.get('loan_amount')
        # fico = data.get('credit_score')

        # Return all active offerings
        offerings = LenderProgramOffering.objects.filter(is_active=True)[:10]

        results = []
        for offer in offerings:
            results.append({
                'lender': offer.lender.company_name,
                'program': offer.program_type.name,
                'rate_range': f"{offer.min_rate}% - {offer.max_rate}%",
                'interest_rate': offer.min_rate, # For frontend display
                'points': offer.min_points,
                'apr': offer.min_rate + 0.125, # Mock APR
                'monthly_payment': 0, # Frontend can calc or we add util
                'total_adjustment': 0, # Phase 2 will calc this
            })

        return Response({
            'quotes': results,
            'count': len(results)
        })
