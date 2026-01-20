"""API views for the Unified CMTG Platform."""

import logging
from math import radians, sin, cos, sqrt, asin

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.db.models import Q

from pricing.services.matching import LoanMatchingService
from applications.models import Application
from cms.models import LocationPage
from decimal import Decimal
from django.db import connection
from loans.models import LoanProgram, Lender
from .serializers import (
    LeadSubmitSerializer, 
    ApplicationSerializer, 
    QualificationRequestSerializer, 
    QualificationResultSerializer
)
from .integrations.floify import FloifyClient, FloifyAPIError
from open_los.services import Ingest1003Service

logger = logging.getLogger(__name__)


# ============================================================================
# Location API Endpoints
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def location_list(request):
    """
    GET /api/v1/locations/
    
    List all locations with optional search filtering.
    Query params:
        - q: Search query (city or state)
        - state: Filter by state code (e.g., CA)
        - limit: Max results (default 50)
    """
    queryset = LocationPage.objects.live().order_by('city', 'state')
    
    # Search query
    q = request.query_params.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(city__icontains=q) | 
            Q(state__icontains=q) |
            Q(title__icontains=q)
        )
    
    # State filter
    state = request.query_params.get('state', '').strip().upper()
    if state:
        queryset = queryset.filter(state=state)
    
    # Limit
    limit = min(int(request.query_params.get('limit', 50)), 200)
    queryset = queryset[:limit]
    
    locations = []
    for loc in queryset:
        locations.append({
            'id': loc.id,
            'title': loc.title,
            'slug': loc.slug,
            'city': loc.city,
            'state': loc.state,
            'address': loc.address,
            'zipcode': loc.zipcode,
            'phone': loc.phone,
            'url': loc.url,
            'latitude': float(loc.latitude) if loc.latitude else None,
            'longitude': float(loc.longitude) if loc.longitude else None,
        })
    
    return Response({
        'count': len(locations),
        'locations': locations
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def location_detail(request, slug):
    """
    GET /api/v1/locations/<slug>/
    
    Get a single location by slug.
    """
    try:
        loc = LocationPage.objects.live().get(slug=slug)
        
        return Response({
            'id': loc.id,
            'title': loc.title,
            'slug': loc.slug,
            'city': loc.city,
            'state': loc.state,
            'address': loc.address,
            'second_address': loc.second_address,
            'zipcode': loc.zipcode,
            'country': loc.country,
            'phone': loc.phone,
            'url': loc.url,
            'full_url': loc.full_url,
            'latitude': float(loc.latitude) if loc.latitude else None,
            'longitude': float(loc.longitude) if loc.longitude else None,
            'google_maps_url': loc.google_maps_url,
            'schema_org': loc.get_schema_org(),
        })
    except LocationPage.DoesNotExist:
        return Response(
            {'error': 'Location not found'},
            status=status.HTTP_404_NOT_FOUND
        )


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in miles."""
    EARTH_RADIUS_MILES = 3959
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return EARTH_RADIUS_MILES * c


@api_view(['GET'])
@permission_classes([AllowAny])
def location_nearest(request):
    """
    GET /api/v1/locations/nearest/?lat=<lat>&lng=<lng>
    
    Find nearest locations to given coordinates.
    Query params:
        - lat: Latitude (required)
        - lng: Longitude (required)
        - limit: Max results (default 5)
        - max_distance: Max distance in miles (optional)
    """
    lat = request.query_params.get('lat')
    lng = request.query_params.get('lng')
    
    if not lat or not lng:
        return Response(
            {'error': 'lat and lng query parameters are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user_lat = float(lat)
        user_lng = float(lng)
    except ValueError:
        return Response(
            {'error': 'Invalid lat/lng values'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    limit = min(int(request.query_params.get('limit', 5)), 20)
    max_distance = request.query_params.get('max_distance')
    
    # Get all locations with coordinates
    locations = LocationPage.objects.live().exclude(
        latitude__isnull=True
    ).exclude(longitude__isnull=True)
    
    # Calculate distances
    results = []
    for loc in locations:
        distance = haversine_distance(
            user_lat, user_lng,
            float(loc.latitude), float(loc.longitude)
        )
        
        if max_distance and distance > float(max_distance):
            continue
        
        results.append({
            'id': loc.id,
            'title': loc.title,
            'slug': loc.slug,
            'city': loc.city,
            'state': loc.state,
            'address': loc.address,
            'phone': loc.phone,
            'url': loc.url,
            'distance_miles': round(distance, 1),
        })
    
    # Sort by distance and limit
    results.sort(key=lambda x: x['distance_miles'])
    results = results[:limit]
    
    return Response({
        'user_location': {'lat': user_lat, 'lng': user_lng},
        'count': len(results),
        'locations': results
    })


# ============================================================================
# Health Check
# ============================================================================

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


        # NEW: Open LOS Ingestion
        try:
            # Re-use the existing client context if possible, but here we opened a new one
            # The previous context manager closed, so we open a new one or should have kept it open.
            # actually `with FloifyClient() as client:` block ended above at line 442. 
            # We need to fetch 1003 data.
            with FloifyClient() as client:
                logger.info(f"Fetching 1003 data for {floify_id}")
                # Note: get_1003_json takes loan_id, not prospect_id (floify_id).
                # The app_data from get_application usually has 'loanId' if it's converted.
                # If it's just a prospect, get_1003_json might fail or return partial.
                # But `application.floify_loan_id` should be populated if available.
                
                target_id = application.floify_loan_id or application.floify_id
                # Only try if we have a target, though for prospects 1003 might not exist yet.
                # Floify docs say 1003 export is for Loans. Let's try only if we have loanId.
                
                if application.floify_loan_id:
                     json_1003 = client.get_1003_json(application.floify_loan_id)
                     if json_1003:
                         Ingest1003Service.ingest_floify_json(application.floify_loan_id, json_1003)
                         logger.info(f"Open LOS Ingested 1003 for {application.floify_loan_id}")
                else:
                    logger.info(f"Skipping 1003 ingest for {floify_id} - No Loan ID yet")

        except Exception as e:
            # Swallow error so we don't fail the webhook response
            logger.error(f"Open LOS Ingestion failed for {floify_id}: {e}")

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


        # Open LOS Ingestion on Update
        try:
             # Reload app to get latest IDs
            app_refresh = Application.objects.get(id=application.id)
            if app_refresh.floify_loan_id:
                with FloifyClient() as client:
                    json_1003 = client.get_1003_json(app_refresh.floify_loan_id)
                    if json_1003:
                        Ingest1003Service.ingest_floify_json(app_refresh.floify_loan_id, json_1003)
                        logger.info(f"Open LOS Ingested 1003 update for {app_refresh.floify_loan_id}")
        except Exception as e:
             logger.error(f"Open LOS Ingestion failed (update) for {floify_id}: {e}")

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


class QualifyView(APIView):
    """
    Pre-qualification endpoint for borrowers.
    POST /api/v1/qualify/
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = QualificationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Find matching programs
        # Note: property_state needs to be upper case for matching.
        # Also, using 'contains' for ChoiceArrayFields.
        if connection.vendor == 'sqlite':
            # SQLite fallback: Filter strictly by scalar fields first, then filter array fields in Python
            initial_programs = LoanProgram.objects.select_related('lender').filter(
                min_loan_amount__lte=data['loan_amount'],
                max_loan_amount__gte=data['loan_amount'],
                min_credit__lte=data['credit_score'],
                max_loan_to_value__gte=data['calculated_ltv'],
            )
            programs = []
            for p in initial_programs:
                if data['property_state'].upper() not in p.lender.include_states: continue
                if data['property_type'] not in p.property_types: continue
                if data['loan_purpose'] not in p.purpose: continue
                if data['occupancy'] not in p.occupancy: continue
                programs.append(p)
        else:
            programs = LoanProgram.objects.select_related('lender').filter(
                lender__include_states__contains=[data['property_state'].upper()],
                min_loan_amount__lte=data['loan_amount'],
                max_loan_amount__gte=data['loan_amount'],
                min_credit__lte=data['credit_score'],
                max_loan_to_value__gte=data['calculated_ltv'],
                property_types__contains=[data['property_type']],
                purpose__contains=[data['loan_purpose']],
                occupancy__contains=[data['occupancy']],
            )
        
        matched_programs = []
        for program in programs[:10]:
            match_score = self._calculate_match_score(program, data)
            matched_programs.append({
                'program_id': program.id,
                'program_name': program.name,
                'lender_name': program.lender.company_name,
                'estimated_rate_range': f"{program.potential_rate_min:.2f}% - {program.potential_rate_max:.2f}%",
                'match_score': match_score,
                'notes': self._get_program_notes(program, data),
            })
        
        matched_programs.sort(key=lambda x: x['match_score'], reverse=True)
        
        result = {
            'matched_programs': matched_programs,
            'total_matches': len(matched_programs),
            'calculated_ltv': data['calculated_ltv'],
        }
        return Response(QualificationResultSerializer(result).data)
    
        if program.potential_rate_min < 7.0: score += 15
        elif program.potential_rate_min < 8.0: score += 10
        
        return min(score, 100)
    
    def _get_program_notes(self, program, data):
        from loans.services.matching import MatchingService
        return MatchingService.get_program_notes(program, data)
        
    def _calculate_match_score(self, program, data):
        from loans.services.matching import MatchingService
        return MatchingService.calculate_match_score(program, data)


# ============================================================================
# CMS / Snippets
# ============================================================================
from cms.models import NavigationMenu, SiteConfiguration
from .serializers import NavigationMenuSerializer, SiteConfigurationSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def navigation_menu_detail(request, name):
    """
    GET /api/v1/navigation/<name>/
    Retrieve a navigation menu by name (e.g. 'Main Header').
    """
    try:
        # Case insensitive match
        menu = NavigationMenu.objects.get(name__iexact=name)
        return Response(NavigationMenuSerializer(menu).data)
    except NavigationMenu.DoesNotExist:
        return Response({'error': 'Menu not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def site_configuration(request):
    """
    GET /api/v1/site-config/
    Retrieve the singleton site configuration.
    """
    # Assuming one config, or get the first one
    config = SiteConfiguration.objects.first()
    if not config:
        return Response({})
    return Response(SiteConfigurationSerializer(config).data)
