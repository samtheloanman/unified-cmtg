from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from cms.services.seo_resolver import SEOResolver
from cms.models.seo import SEOContentCache
from cms.models.programs import ProgramPage
from cms.models.cities import City
from cms.services.location_mapper import LocationMapper
from cms.services.schema_generator import SchemaGenerator

@api_view(['GET'])
def resolve_path(request):
    """
    Resolves a URL path to determining the content type and data.
    Query Param: path (e.g. /jumbo-loans/in-los-angeles-ca/)
    """
    path = request.query_params.get('path')
    if not path:
        return Response({'error': 'Path parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
    # 1. Try SEOResolver (Program + Location)
    program_slug, city_slug, state_code = SEOResolver.resolve_path(path)
    
    if program_slug and city_slug:
        # It's a valid Program Location path
        try:
            # Fetch SEO Cache
            cache = SEOContentCache.objects.filter(url_path=path).first()
            if not cache:
                # Should ideally generate on fly if valid, but for pilot we rely on pre-gen
                return Response({'error': 'Content not generated yet'}, status=status.HTTP_404_NOT_FOUND)
                
            # Fetch Context Data
            program = ProgramPage.objects.get(slug=program_slug)
            city = City.objects.get(slug=city_slug, state=state_code)
            
            # Map Office
            office = LocationMapper.get_closest_office(city)
            office_data = {}
            if office:
                office_data = {
                    'name': office.name,
                    'address': f"{office.city}, {office.state}", # Simplified
                    'phone': getattr(office, 'phone', '555-0123') # fallback
                }

            return Response({
                'type': 'program_location',
                'data': {
                    'title': cache.title_tag,
                    'h1': cache.h1_header,
                    'meta_description': cache.meta_description,
                    'content': cache.content_body,
                    'schema': cache.schema_json,
                    'program': {
                        'title': program.title,
                        'slug': program.slug,
                        'rates': program.interest_rates
                    },
                    'location': {
                        'city': city.name,
                        'state': city.state,
                        'office': office_data
                    }
                }
            })
            
        except (ProgramPage.DoesNotExist, City.DoesNotExist):
             return Response({'error': 'Resource missing'}, status=status.HTTP_404_NOT_FOUND)

    # 2. If not Program Location, returning 404 for now.
    # Frontend will handle standard Wagtail pages via the standard Wagtail API.
    return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
