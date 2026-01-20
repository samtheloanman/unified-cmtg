from rest_framework import viewsets, permissions
from .models import LoanApplication
from .serializers import LoanApplicationSerializer

class LoanApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for Full 1003 Applications.
    """
    queryset = LoanApplication.objects.all().prefetch_related(
        'borrowers', 
        'borrowers__employments', 
        'borrowers__declarations',
        'assets', 
        'liabilities'
    )
    serializer_class = LoanApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['floify_loan_id', 'status', 'property_state']
