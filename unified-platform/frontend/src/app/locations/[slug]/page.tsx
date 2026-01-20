import { Metadata } from 'next';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getLocationBySlug, getLocations, getStateName } from '@/lib/locations-api';

interface Props {
    params: { slug: string };
}

export async function generateStaticParams() {
    try {
        const locations = await getLocations({ limit: 200 });
        return locations.map((location) => ({
            slug: location.slug,
        }));
    } catch (error) {
        console.warn('Failed to fetch locations for static generation:', error);
        return []; // Return empty array - pages will be generated on-demand
    }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const location = await getLocationBySlug(params.slug);

    if (!location) {
        return { title: 'Location Not Found' };
    }

    return {
        title: `${location.city}, ${location.state} | Custom Mortgage`,
        description: `Contact Custom Mortgage in ${location.city}, ${getStateName(location.state)}. Address: ${location.address}. Phone: ${location.phone}`,
    };
}

export default async function LocationDetailPage({ params }: Props) {
    const location = await getLocationBySlug(params.slug);

    if (!location) {
        notFound();
    }

    return (
        <main className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
            {/* Breadcrumb */}
            <nav className="max-w-7xl mx-auto px-4 py-4">
                <ol className="flex items-center gap-2 text-sm text-gray-400">
                    <li><Link href="/" className="hover:text-white">Home</Link></li>
                    <li>/</li>
                    <li><Link href="/locations" className="hover:text-white">Locations</Link></li>
                    <li>/</li>
                    <li className="text-cyan-400">{location.city}, {location.state}</li>
                </ol>
            </nav>

            {/* Location Hero */}
            <section className="max-w-7xl mx-auto px-4 py-12">
                <div className="grid lg:grid-cols-2 gap-12">
                    {/* Left: Location Info */}
                    <div>
                        <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
                            {location.city}
                        </h1>
                        <p className="text-2xl text-cyan-400 mb-8">
                            {getStateName(location.state)}
                        </p>

                        {/* Address Card */}
                        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
                            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                📍 Address
                            </h2>
                            <p className="text-gray-300 text-lg">
                                {location.address}
                            </p>
                            {location.second_address && (
                                <p className="text-gray-400">{location.second_address}</p>
                            )}
                            <p className="text-gray-400">
                                {location.city}, {location.state} {location.zipcode}
                            </p>

                            <a
                                href={location.google_maps_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-2 mt-4 text-cyan-400 hover:text-cyan-300"
                            >
                                🗺️ Get Directions →
                            </a>
                        </div>

                        {/* Contact Card */}
                        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 mb-6">
                            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                📞 Contact
                            </h2>
                            <a
                                href={`tel:${location.phone}`}
                                className="text-2xl text-cyan-400 hover:text-cyan-300 font-semibold"
                            >
                                {location.phone}
                            </a>
                        </div>

                        {/* CTA Buttons */}
                        <div className="flex flex-col sm:flex-row gap-4">
                            <Link
                                href="/quote"
                                className="flex-1 text-center px-6 py-4 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-semibold transition-colors"
                            >
                                Get a Quote
                            </Link>
                            <a
                                href={`tel:${location.phone}`}
                                className="flex-1 text-center px-6 py-4 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition-colors"
                            >
                                Call Now
                            </a>
                        </div>
                    </div>

                    {/* Right: Map Placeholder */}
                    <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden h-[400px] lg:h-full min-h-[400px] flex items-center justify-center">
                        {location.latitude && location.longitude ? (
                            <iframe
                                width="100%"
                                height="100%"
                                style={{ border: 0 }}
                                loading="lazy"
                                allowFullScreen
                                referrerPolicy="no-referrer-when-downgrade"
                                src={`https://www.google.com/maps/embed/v1/place?key=${process.env.NEXT_PUBLIC_GOOGLE_MAPS_KEY || 'YOUR_KEY'}&q=${encodeURIComponent(location.address + ', ' + location.city + ', ' + location.state)}`}
                            />
                        ) : (
                            <div className="text-center text-gray-400">
                                <div className="text-6xl mb-4">🗺️</div>
                                <p>Map loading...</p>
                            </div>
                        )}
                    </div>
                </div>
            </section>

            {/* Services Section */}
            <section className="bg-gray-800/50 py-16 px-4">
                <div className="max-w-7xl mx-auto">
                    <h2 className="text-3xl font-bold text-white mb-8 text-center">
                        Mortgage Services in {location.city}
                    </h2>
                    <div className="grid md:grid-cols-3 gap-6">
                        {[
                            { icon: '🏠', title: 'Residential Mortgages', desc: 'FHA, VA, Conventional and more' },
                            { icon: '🏢', title: 'Commercial Loans', desc: 'Investment property financing' },
                            { icon: '💰', title: 'Hard Money Loans', desc: 'Fast funding for investors' },
                        ].map((service) => (
                            <div key={service.title} className="bg-gray-800 border border-gray-700 rounded-xl p-6 text-center">
                                <div className="text-4xl mb-4">{service.icon}</div>
                                <h3 className="text-xl font-semibold text-white mb-2">{service.title}</h3>
                                <p className="text-gray-400">{service.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Schema.org JSON-LD */}
            {location.schema_org && (
                <script
                    type="application/ld+json"
                    dangerouslySetInnerHTML={{ __html: JSON.stringify(location.schema_org) }}
                />
            )}
        </main>
    );
}
