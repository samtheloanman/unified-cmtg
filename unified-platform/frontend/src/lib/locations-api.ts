/**
 * Location API Client
 * 
 * Fetches location data from the backend API.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export interface Location {
  id: number;
  title: string;
  slug: string;
  city: string;
  state: string;
  address: string;
  second_address?: string;
  zipcode: string;
  country?: string;
  phone: string;
  url: string;
  full_url?: string;
  latitude: number | null;
  longitude: number | null;
  distance_miles?: number;
  google_maps_url?: string;
  schema_org?: Record<string, unknown>;
}

export interface LocationsResponse {
  count: number;
  locations: Location[];
}

export interface NearestResponse {
  user_location: { lat: number; lng: number };
  count: number;
  locations: Location[];
}

/**
 * Fetch all locations with optional search/filter
 */
export async function getLocations(params?: {
  q?: string;
  state?: string;
  limit?: number;
}): Promise<Location[]> {
  const searchParams = new URLSearchParams();
  
  if (params?.q) searchParams.set('q', params.q);
  if (params?.state) searchParams.set('state', params.state);
  if (params?.limit) searchParams.set('limit', params.limit.toString());
  
  const url = `${API_BASE}/locations/?${searchParams}`;
  
  try {
    const response = await fetch(url, { 
      next: { revalidate: 60 } 
    });
    
    if (!response.ok) {
      console.error(`Failed to fetch locations: ${response.status}`);
      return [];
    }
    
    const data: LocationsResponse = await response.json();
    return data.locations;
  } catch (error) {
    console.error('Error fetching locations:', error);
    return [];
  }
}

/**
 * Fetch a single location by slug
 */
export async function getLocationBySlug(slug: string): Promise<Location | null> {
  const url = `${API_BASE}/locations/${slug}/`;
  
  try {
    const response = await fetch(url, { 
      next: { revalidate: 60 } 
    });
    
    if (!response.ok) {
      return null;
    }
    
    return response.json();
  } catch (error) {
    console.error('Error fetching location:', error);
    return null;
  }
}

/**
 * Find nearest locations to given coordinates
 */
export async function getNearestLocations(
  lat: number,
  lng: number,
  limit: number = 5
): Promise<Location[]> {
  const url = `${API_BASE}/locations/nearest/?lat=${lat}&lng=${lng}&limit=${limit}`;
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      console.error(`Failed to fetch nearest locations: ${response.status}`);
      return [];
    }
    
    const data: NearestResponse = await response.json();
    return data.locations;
  } catch (error) {
    console.error('Error fetching nearest locations:', error);
    return [];
  }
}

/**
 * Get user's current location via browser geolocation
 */
export function getUserLocation(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation not supported'));
      return;
    }
    
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: false,
      timeout: 10000,
      maximumAge: 300000, // Cache for 5 minutes
    });
  });
}

/**
 * Format state code to full name
 */
export const STATE_NAMES: Record<string, string> = {
  AL: 'Alabama', AK: 'Alaska', AZ: 'Arizona', AR: 'Arkansas', CA: 'California',
  CO: 'Colorado', CT: 'Connecticut', DE: 'Delaware', DC: 'District of Columbia',
  FL: 'Florida', GA: 'Georgia', HI: 'Hawaii', ID: 'Idaho', IL: 'Illinois',
  IN: 'Indiana', IA: 'Iowa', KS: 'Kansas', KY: 'Kentucky', LA: 'Louisiana',
  ME: 'Maine', MD: 'Maryland', MA: 'Massachusetts', MI: 'Michigan', MN: 'Minnesota',
  MS: 'Mississippi', MO: 'Missouri', MT: 'Montana', NE: 'Nebraska', NV: 'Nevada',
  NH: 'New Hampshire', NJ: 'New Jersey', NM: 'New Mexico', NY: 'New York',
  NC: 'North Carolina', ND: 'North Dakota', OH: 'Ohio', OK: 'Oklahoma', OR: 'Oregon',
  PA: 'Pennsylvania', RI: 'Rhode Island', SC: 'South Carolina', SD: 'South Dakota',
  TN: 'Tennessee', TX: 'Texas', UT: 'Utah', VT: 'Vermont', VA: 'Virginia',
  WA: 'Washington', WV: 'West Virginia', WI: 'Wisconsin', WY: 'Wyoming',
  PR: 'Puerto Rico', GU: 'Guam', AS: 'American Samoa',
};

export function getStateName(code: string): string {
  return STATE_NAMES[code.toUpperCase()] || code;
}
