"""API views for the Unified CMTG Platform."""

import logging

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from pricing.services.matching import LoanMatchingService
from applications.models import Application
from .serializers import LeadSubmitSerializer, ApplicationSerializer
from .integrations.floify import FloifyClient, FloifyAPIError

logger = logging.getLogger(__name__)

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


@method_decorator(csrf_exempt, name='dispatch')
class LeadSubmitView(APIView):
    """
    POST /api/v1/leads/

    Submit a lead to Floify after quote wizard completion.

    When a borrower clicks "Apply Now" after seeing their quotes,
    this endpoint creates a prospect in Floify and sends them
    an email invitation to complete their full loan application.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """Handle lead submission."""
        serializer = LeadSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        # Push to Floify
        try:
            with FloifyClient() as client:
                result = client.create_prospect(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    phone=data.get('phone'),
                    loan_amount=data.get('loan_amount'),
                    property_address=data.get('property_address'),
                    loan_purpose=data.get('loan_purpose'),
                )

                floify_id = result.get('id')

                # Create local Application record
                application = Application.objects.create(
                    floify_id=floify_id,
                    borrower_email=data['email'],
                    borrower_first_name=data['first_name'],
                    borrower_last_name=data['last_name'],
                    borrower_phone=data.get('phone', ''),
                    loan_amount=data.get('loan_amount'),
                    property_address=data.get('property_address', ''),
                    property_state=data.get('property_state', ''),
                    loan_purpose=data.get('loan_purpose', ''),
                    property_type=data.get('property_type', ''),
                    selected_program=data.get('selected_program', ''),
                    selected_lender=data.get('selected_lender', ''),
                    status='created',
                    floify_data=result,
                )

                logger.info(
                    f"Created lead for {data['email']}: "
                    f"Floify ID {floify_id}, App ID {application.id}"
                )

                return Response({
                    'success': True,
                    'floify_id': floify_id,
                    'application_id': application.id,
                    'message': 'Application link sent to your email. '
                               'Please check your inbox to continue.'
                })

        except FloifyAPIError as e:
            logger.error(f"Floify API error: {e}")
            return Response(
                {
                    'success': False,
                    'error': 'Unable to create application',
                    'detail': str(e)
                },
                status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            logger.exception("Unexpected error in lead submission")
            return Response(
                {
                    'success': False,
                    'error': 'Internal server error',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def floify_webhook(request):
    """
    Webhook handler for Floify application events.

    Floify sends webhook events when:
    - application.created: New application submitted
    - application.updated: Application status changed
    - application.submitted: Application submitted to lender
    - document.uploaded: New document received

    Note: Floify webhooks do not use signature verification.
    Access control should be handled via firewall rules or webhook URL secrecy.
    """

    event_type = request.data.get('event')
    payload = request.data.get('payload', {})

    logger.info(f"Floify webhook received: {event_type}")

    if event_type == 'application.created':
        return _handle_application_created(payload)

    elif event_type == 'application.updated':
        return _handle_application_updated(payload)

    elif event_type == 'application.submitted':
        return _handle_application_submitted(payload)

    elif event_type == 'document.uploaded':
        logger.info(f"Document uploaded for loan {payload.get('loanId')}")
        return Response({'received': True})

    else:
        logger.warning(f"Unknown webhook event type: {event_type}")
        return Response({'received': True})


def _handle_application_created(payload):
    """Handle new application from Floify."""
    floify_id = payload.get('id')

    if not floify_id:
        logger.error("Missing floify_id in application.created webhook")
        return Response({'error': 'Missing floify_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch full application data
        with FloifyClient() as client:
            app_data = client.get_application(floify_id)

        # Create or update local record
        application, created = Application.objects.update_or_create(
            floify_id=floify_id,
            defaults={
                'borrower_email': app_data.get('email', ''),
                'borrower_first_name': app_data.get('firstName', ''),
                'borrower_last_name': app_data.get('lastName', ''),
                'borrower_phone': app_data.get('mobilePhoneNumber', ''),
                'loan_amount': app_data.get('loanAmount'),
                'property_address': app_data.get('subjectPropertyAddress', ''),
                'loan_purpose': app_data.get('loanPurpose', ''),
                'floify_loan_id': app_data.get('loanId', ''),
                'status': 'in_progress',
                'floify_data': app_data,
            }
        )

        action = "Created" if created else "Updated"
        logger.info(f"{action} application {application.id} from Floify {floify_id}")

        return Response({'processed': True, 'application_id': application.id})

    except FloifyAPIError as e:
        logger.error(f"Failed to fetch Floify application {floify_id}: {e}")
        return Response(
            {'error': 'Failed to fetch application data'},
            status=status.HTTP_502_BAD_GATEWAY
        )
    except Exception as e:
        logger.exception("Error handling application.created webhook")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _handle_application_updated(payload):
    """Handle application status update."""
    floify_id = payload.get('id')
    new_status = payload.get('status', '').lower()

    if not floify_id:
        logger.error("Missing floify_id in application.updated webhook")
        return Response({'error': 'Missing floify_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        application = Application.objects.get(floify_id=floify_id)

        # Map Floify status to our status
        status_map = {
            'submitted': 'submitted',
            'processing': 'processing',
            'underwriting': 'underwriting',
            'approved': 'approved',
            'clear_to_close': 'clear_to_close',
            'funded': 'funded',
            'denied': 'denied',
            'withdrawn': 'withdrawn',
        }

        if new_status in status_map:
            old_status = application.status
            application.status = status_map[new_status]
            application.save()
            logger.info(
                f"Updated application {application.id} status: "
                f"{old_status} -> {application.status}"
            )

        return Response({'processed': True, 'application_id': application.id})

    except Application.DoesNotExist:
        logger.warning(f"Application not found for Floify ID: {floify_id}")
        # Not an error - webhook may arrive before we create local record
        return Response({'processed': True, 'note': 'Application not yet created locally'})

    except Exception as e:
        logger.exception("Error handling application.updated webhook")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _handle_application_submitted(payload):
    """Handle application submission to lender."""
    floify_id = payload.get('id')

    if not floify_id:
        logger.error("Missing floify_id in application.submitted webhook")
        return Response({'error': 'Missing floify_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        application = Application.objects.get(floify_id=floify_id)
        application.status = 'submitted'
        application.save()

        logger.info(f"Application {application.id} submitted to lender")

        return Response({'processed': True, 'application_id': application.id})

    except Application.DoesNotExist:
        logger.warning(f"Application not found for Floify ID: {floify_id}")
        return Response({'processed': True, 'note': 'Application not yet created locally'})

    except Exception as e:
        logger.exception("Error handling application.submitted webhook")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
