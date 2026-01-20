
export interface Territory {
    state: string;
    city: string;
    county: string;
}

// Data matching the production screenshot instructions
export const TERRITORY_DATA: Territory[] = [
    { state: 'AL', city: 'BIRMINGHAM', county: 'JEFFERSON' },
    { state: 'AL', city: 'HUNTSVILLE', county: 'MADISON' },
    { state: 'AL', city: 'MOBILE', county: 'MOBILE' },
    { state: 'AL', city: 'MONTGOMERY', county: 'MONTGOMERY' },
    { state: 'AL', city: 'TUSCALOOSA', county: 'TUSCALOOSA' },
    { state: 'AK', city: 'ANCHORAGE', county: 'ANCHORAGE BOROUGH' },
    { state: 'AK', city: 'FAIRBANKS', county: 'FAIRBANKS NORTH STAR' },
    { state: 'AZ', city: 'CHANDLER', county: 'MARICOPA' },
    { state: 'AZ', city: 'GILBERT', county: 'MARICOPA' },
    { state: 'AZ', city: 'GLENDALE', county: 'MARICOPA' },
    { state: 'AZ', city: 'MESA', county: 'MARICOPA' },
    { state: 'AZ', city: 'PEORIA', county: 'MARICOPA' },
    { state: 'AZ', city: 'PHOENIX', county: 'MARICOPA' },
    { state: 'AZ', city: 'SCOTTSDALE', county: 'MARICOPA' },
    { state: 'AZ', city: 'SURPRISE', county: 'MARICOPA' },
    { state: 'AZ', city: 'TEMPE', county: 'MARICOPA' },
    { state: 'AZ', city: 'TUCSON', county: 'PIMA' },
    { state: 'AZ', city: 'YUMA', county: 'YUMA' },
    { state: 'AR', city: 'FORT SMITH', county: 'SEBASTIAN' },
    // Truncated list for MVP - In real implementation, we would need the full CSV or API
    // Adding a few more to show variety
    { state: 'CA', city: 'LOS ANGELES', county: 'LOS ANGELES' },
    { state: 'CA', city: 'SAN DIEGO', county: 'SAN DIEGO' },
    { state: 'CA', city: 'SAN FRANCISCO', county: 'SAN FRANCISCO' },
];
