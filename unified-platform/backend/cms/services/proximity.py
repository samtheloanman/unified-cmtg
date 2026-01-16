from math import radians, sin, cos, sqrt, asin
from cms.models import City, Office

class ProximityService:
    EARTH_RADIUS_MILES = 3959
    
    @staticmethod
    def haversine_distance(lat1, lon1, lat2, lon2):
        """
        Calculate distance between two GPS points in miles.
        """
        try:
            lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        except (ValueError, TypeError):
             return float('inf')

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        return ProximityService.EARTH_RADIUS_MILES * c
    
    @classmethod
    def find_nearest_office(cls, city: City) -> Office:
        """
        Find nearest office to city using Haversine.
        Fallback to HQ if distance > 500 miles.
        """
        offices = Office.objects.filter(is_active=True)
        # Try to find HQ, fallback to first active if not found
        try:
             hq = Office.objects.get(is_headquarters=True)
        except Office.DoesNotExist:
             hq = offices.first()

        nearest = None
        min_distance = float('inf')
        
        # Performance note: For thousands of cities, doing this in Python is slow.
        # But for 1 lookup per page generation, it's fine.
        # If bulk generating, might want to cache or use GeoDjango.
        
        for office in offices:
            if office.latitude is None or office.longitude is None:
                continue
                
            distance = cls.haversine_distance(
                city.latitude, city.longitude,
                office.latitude, office.longitude
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest = office
        
        # Fallback rule: if > 500 miles, use HQ
        if min_distance > 500 and hq:
            return hq
        
        return nearest or hq
