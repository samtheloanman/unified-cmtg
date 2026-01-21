from django.http import Http404
from django.db.models.functions import Length
from cms.models.cities import City
from cms.models.programs import ProgramPage

class SEOResolver:
    """
    Resolves SEO URL slugs to Program + City combinations.
    Pattern: /{program-slug}-{city-slug}-{state}/
    
    Uses "Suffix Match" strategy to handle multi-hyphen cities safely.
    Example: /dscr-loan-salt-lake-city-ut/ -> Program: dscr-loan, City: salt-lake-city
    """
    
    @classmethod
    def resolve_slug(cls, slug):
        """
        Parse slug and return (program, city) tuple.
        
        Args:
            slug: URL slug like "dscr-loan-los-angeles-ca"
            
        Returns:
            tuple: (ProgramPage, City) objects
            
        Raises:
            Http404: If parsing fails or resources not found
        """
        # 1. Extract state (last element after splitting)
        parts = slug.split('-')
        if len(parts) < 3:  # Minimum: program-city-state
            raise Http404("Invalid SEO URL format")
            
        state = parts[-1].upper()
        
        # 2. Get all cities in this state, ordered by slug length (longest first)
        # This ensures we match "salt-lake-city" before "city"
        cities = City.objects.filter(state=state).order_by(Length('slug').desc())
        
        if not cities.exists():
            raise Http404(f"No cities found for state: {state}")
        
        # 3. Find the longest matching city suffix
        for city in cities:
            suffix = f"-{city.slug}-{state.lower()}"
            if slug.endswith(suffix):
                # Found match! Extract program slug
                program_slug = slug[:-len(suffix)]
                
                # Validate program exists and is live
                try:
                    program = ProgramPage.objects.live().get(slug=program_slug)
                except ProgramPage.DoesNotExist:
                    raise Http404(f"Program not found: {program_slug}")
                
                # Check if city is launched
                if not city.launched_at:
                    raise Http404(f"City not yet launched: {city.name}")
                
                return (program, city)
        
        # No matching city found
        raise Http404(f"Could not parse city from URL: {slug}")

    @classmethod
    def resolve_path(cls, path):
        """
        Parse a full URL path and return (program_slug, city_slug, state_code).
        Expected Pattern: /program-slug/in-city-slug-state/
        Example: /jumbo-loans/in-los-angeles-ca/
        """
        import re
        # Normalize: strip slashes and convert to lowercase
        normalized_path = path.strip('/').lower()
        
        # Pattern match: {program_slug}/in-{city_slug}-{state_code}
        # city_slug can contain hyphens, state_code is exactly 2 letters
        pattern = r'^([^/]+)/in-([a-z0-9-]+)-([a-z]{2})$'
        match = re.match(pattern, normalized_path)
        
        if match:
            program_slug = match.group(1)
            city_slug = match.group(2)
            state_code = match.group(3).upper()
            
            # Validation (required by tests)
            if ProgramPage.objects.live().filter(slug=program_slug).exists() and \
               City.objects.filter(slug=city_slug, state=state_code).exists():
                return program_slug, city_slug, state_code
            
        return None, None, None
