import re
from cms.models.cities import City
from cms.models.programs import ProgramPage
from django.utils.text import slugify

class SEOResolver:
    """
    Resolves URL paths to determine Program + Location intent.
    Pattern: /{program-slug}/in-{city}-{state}/
    """
    
    # Regex to capture program slug and location part
    # Matches /something/in-city-name-st/
    # Group 1: program_slug
    # Group 2: remainder (city-name-st)
    PATH_PATTERN = re.compile(r'^/([\w-]+)/in-([\w-]+)/?$')

    @classmethod
    def resolve_path(cls, path_string):
        """
        Parses a path string and attempts to resolve it to a ProgramPage and a City.
        Returns: (program_slug, city_slug, state_code) or (None, None, None)
        """
        match = cls.PATH_PATTERN.match(path_string)
        if not match:
            return None, None, None
            
        program_slug = match.group(1)
        location_part = match.group(2) # e.g. "los-angeles-ca"
        
        # Extract state (last 2 chars)
        parts = location_part.split('-')
        if len(parts) < 2:
            return None, None, None
            
        state_code = parts[-1].upper()
        city_slug = "-".join(parts[:-1]) # Reconstruct city slug
        
        # Validate existence
        # 1. Check if Program exists
        if not ProgramPage.objects.filter(slug=program_slug).exists():
            return None, None, None
            
        # 2. Check if City exists (optional, could be strict or loose)
        # For this resolver, we want to know if it matches our data
        if not City.objects.filter(slug=city_slug, state=state_code).exists():
             # Try loosen parsing if slugs don't match exactly?
             # For now strict.
             return None, None, None
             
        return program_slug, city_slug, state_code
