import { Metadata } from 'next';
import Link from 'next/link';
import { getLocations, getStateName } from '@/lib/locations-api';

export const metadata: Metadata = {
    title: 'Locations | Custom Mortgage',
    description: 'Find a Custom Mortgage location near you. We serve over 100 cities across the United States.',
};

export default async function LocationsPage() {
    const locations = await getLocations({ limit: 200 });

    // Group locations by state
    const byState: Record<string, typeof locations> = {};
    for (const loc of locations) {
        if (!byState[loc.state]) {
            byState[loc.state] = [];
        }
        byState[loc.state].push(loc);
    }

    // Sort states alphabetically
    const sortedStates = Object.keys(byState).sort();

    return (
        <main className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
            {/* Hero Section */}
            <section className="relative py-20 px-4 text-center">
                <div className="max-w-4xl mx-auto">
                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
                        Find a Location Near You
                    </h1>
                    <p className="text-xl text-gray-300 mb-8">
                        {locations.length} locations across {sortedStates.length} states
                    </p>

                    {/* Search Box */}
                    <div className="max-w-xl mx-auto">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                placeholder="Search by city or state..."
                                className="flex-1 px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500"
                            />
                            <button className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-semibold transition-colors">
                                Search
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            {/* Locations Grid by State */}
            <section className="max-w-7xl mx-auto px-4 pb-20">
                {sortedStates.map((state) => (
                    <div key={state} className="mb-12">
                        <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                            <span className="text-cyan-400">{getStateName(state)}</span>
                            <span className="text-gray-500 text-sm font-normal">
                                ({byState[state].length} {byState[state].length === 1 ? 'location' : 'locations'})
                            </span>
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            {byState[state].map((location) => (
                                <Link
                                    key={location.id}
                                    href={`/locations/${location.slug}`}
                                    className="group p-4 bg-gray-800/50 hover:bg-gray-800 border border-gray-700 hover:border-cyan-600 rounded-lg transition-all duration-200"
                                >
                                    <h3 className="text-lg font-semibold text-white group-hover:text-cyan-400 transition-colors">
                                        {location.city}
                                    </h3>
                                    <p className="text-sm text-gray-400 mt-1 line-clamp-1">
                                        {location.address}
                                    </p>
                                    <p className="text-sm text-gray-500 mt-2">
                                        📞 {location.phone}
                                    </p>
                                </Link>
                            ))}
                        </div>
                    </div>
                ))}
            </section>

            {/* CTA Section */}
            <section className="bg-gradient-to-r from-cyan-600 to-blue-600 py-16 px-4">
                <div className="max-w-4xl mx-auto text-center">
                    <h2 className="text-3xl font-bold text-white mb-4">
                        Ready to Get Started?
                    </h2>
                    <p className="text-xl text-cyan-100 mb-8">
                        Contact your nearest location or get a quick quote online.
                    </p>
                    <Link
                        href="/quote"
                        className="inline-block px-8 py-4 bg-white text-cyan-600 font-bold rounded-lg hover:bg-gray-100 transition-colors"
                    >
                        Get Your Free Quote
                    </Link>
                </div>
            </section>
        </main>
    );
}
