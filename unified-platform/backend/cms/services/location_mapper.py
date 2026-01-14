"""
WordPress Location Data Mapper

Handles mapping of WordPress location data (wp_cmtg_locations table) to Wagtail Location model.
Includes distance calculation utilities for geographic queries.
"""

import re
import math
from typing import List, Dict, Optional, Tuple
from decimal import Decimal


class LocationMapper:
    """
    Maps WordPress location data to Wagtail Location model.

    WordPress stores locations in wp_cmtg_locations table with structure:
    - city
    - state
    - latitude
    - longitude
    - target_url (slug)
    - meta_title
    - meta_description
    """

    def __init__(self):
        """Initialize location mapper."""
        self.locations = []

    def parse_sql_insert(self, sql: str) -> List[Dict]:
        """
        Parse SQL INSERT statements to extract location data.

        Args:
            sql: SQL dump content containing INSERT statements

        Returns:
            List of location dictionaries

        Example SQL:
            INSERT INTO `wp_cmtg_locations` VALUES
            (1, 'Los Angeles', 'CA', '34.0522', '-118.2437', '/ca/los-angeles', 'Title', 'Desc'),
            (2, 'San Francisco', 'CA', '37.7749', '-122.4194', '/ca/san-francisco', 'Title2', 'Desc2');
        """
        locations = []

        # Find INSERT INTO statements
        insert_pattern = re.compile(
            r"INSERT INTO `wp_cmtg_locations`.*?VALUES\s+(.*?);",
            re.DOTALL | re.IGNORECASE
        )

        for match in insert_pattern.finditer(sql):
            values_block = match.group(1)

            # Parse individual value tuples
            # Pattern: (id, 'city', 'state', 'lat', 'lng', 'url', 'title', 'desc')
            tuple_pattern = re.compile(
                r"\((\d+),\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)',\s*'([^']*)'\)",
                re.MULTILINE
            )

            for tuple_match in tuple_pattern.finditer(values_block):
                location = {
                    'id': int(tuple_match.group(1)),
                    'city': tuple_match.group(2),
                    'state': tuple_match.group(3),
                    'latitude': float(tuple_match.group(4)),
                    'longitude': float(tuple_match.group(5)),
                    'target_url': tuple_match.group(6),
                    'meta_title': tuple_match.group(7),
                    'meta_description': tuple_match.group(8),
                }

                locations.append(location)

        return locations

    def map_to_wagtail_location(self, wp_location: Dict) -> Dict:
        """
        Map WordPress location data to Wagtail Location model fields.

        Args:
            wp_location: Dict with WordPress location data

        Returns:
            Dict ready for Wagtail Location.objects.create()
        """
        # Extract slug from target_url
        slug = wp_location['target_url'].strip('/').split('/')[-1]

        return {
            'title': f"{wp_location['city']}, {wp_location['state']}",
            'slug': slug,
            'city': wp_location['city'],
            'state': wp_location['state'],
            'latitude': Decimal(str(wp_location['latitude'])),
            'longitude': Decimal(str(wp_location['longitude'])),
            'seo_title': wp_location.get('meta_title', ''),
            'search_description': wp_location.get('meta_description', ''),
            # Additional fields can be added as needed
        }

    def import_locations_from_sql(self, sql_file_path: str):
        """
        Import locations from SQL dump file.

        Args:
            sql_file_path: Path to SQL dump file

        Returns:
            List of Wagtail-formatted location dicts
        """
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        wp_locations = self.parse_sql_insert(sql_content)
        wagtail_locations = [
            self.map_to_wagtail_location(loc) for loc in wp_locations
        ]

        return wagtail_locations


class DistanceCalculator:
    """
    Calculate distances between geographic coordinates.

    Uses Haversine formula for great-circle distance calculation.
    """

    # Earth's radius in kilometers
    EARTH_RADIUS_KM = 6371.0
    # Earth's radius in miles
    EARTH_RADIUS_MI = 3958.8

    @staticmethod
    def haversine_distance(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
        unit: str = 'mi'
    ) -> float:
        """
        Calculate distance between two points using Haversine formula.

        Args:
            lat1: Latitude of point 1 (decimal degrees)
            lon1: Longitude of point 1 (decimal degrees)
            lat2: Latitude of point 2 (decimal degrees)
            lon2: Longitude of point 2 (decimal degrees)
            unit: 'mi' for miles or 'km' for kilometers

        Returns:
            Distance in specified unit
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Calculate distance
        radius = (
            DistanceCalculator.EARTH_RADIUS_MI if unit == 'mi'
            else DistanceCalculator.EARTH_RADIUS_KM
        )

        return radius * c

    @staticmethod
    def find_nearest_locations(
        origin_lat: float,
        origin_lon: float,
        locations: List[Dict],
        max_distance: Optional[float] = None,
        limit: int = 10,
        unit: str = 'mi'
    ) -> List[Tuple[Dict, float]]:
        """
        Find nearest locations to a given point.

        Args:
            origin_lat: Origin latitude
            origin_lon: Origin longitude
            locations: List of location dicts with 'latitude' and 'longitude'
            max_distance: Maximum distance to include (optional)
            limit: Maximum number of results
            unit: Distance unit ('mi' or 'km')

        Returns:
            List of tuples: (location_dict, distance) sorted by distance
        """
        # Calculate distance for each location
        locations_with_distance = []

        for location in locations:
            distance = DistanceCalculator.haversine_distance(
                origin_lat,
                origin_lon,
                float(location['latitude']),
                float(location['longitude']),
                unit
            )

            # Filter by max distance if specified
            if max_distance is None or distance <= max_distance:
                locations_with_distance.append((location, distance))

        # Sort by distance
        locations_with_distance.sort(key=lambda x: x[1])

        # Return limited results
        return locations_with_distance[:limit]


# Example usage
if __name__ == '__main__':
    # Test SQL parsing
    sample_sql = """
    INSERT INTO `wp_cmtg_locations` VALUES
    (1, 'Los Angeles', 'CA', '34.0522', '-118.2437', '/ca/los-angeles', 'Mortgage Lender Los Angeles', 'Best rates in LA'),
    (2, 'San Francisco', 'CA', '37.7749', '-122.4194', '/ca/san-francisco', 'SF Mortgage Lender', 'Great SF rates');
    """

    mapper = LocationMapper()
    locations = mapper.parse_sql_insert(sample_sql)

    print("Parsed locations:")
    for loc in locations:
        print(f"  - {loc['city']}, {loc['state']} ({loc['latitude']}, {loc['longitude']})")

    # Test distance calculation
    print("\nDistance calculation:")
    calc = DistanceCalculator()

    # Distance from LA to SF
    distance = calc.haversine_distance(
        34.0522, -118.2437,  # LA
        37.7749, -122.4194,  # SF
        unit='mi'
    )
    print(f"  LA to SF: {distance:.2f} miles")

    # Find nearest to a point
    user_lat, user_lon = 35.0, -120.0  # Central CA

    nearest = calc.find_nearest_locations(
        user_lat, user_lon,
        locations,
        limit=2,
        unit='mi'
    )

    print(f"\nNearest locations to ({user_lat}, {user_lon}):")
    for loc, dist in nearest:
        print(f"  - {loc['city']}: {dist:.2f} miles")
