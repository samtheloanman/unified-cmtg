import { resolvePath } from '@/lib/wagtail-api';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import Link from 'next/link';

interface Props {
    params: Promise<{ slug: string[] }>;
}

/**
 * Generate Metadata for SEO
 */
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { slug } = await params;
    const path = '/' + slug.join('/') + '/';

    const result = await resolvePath(path);
    if (!result || result.type !== 'program_location') {
        return {};
    }

    const data = result.data;
    return {
        title: data.title,
        description: data.meta_description,
    };
}

export default async function DynamicSEOPage({ params }: Props) {
    const { slug } = await params;
    const path = '/' + slug.join('/') + '/'; // Construct path: /program/in-city-state/

    const result = await resolvePath(path);

    if (!result) {
        notFound();
    }

    // Handle Program + Location Page
    if (result.type === 'program_location') {
        const { data } = result;
        const { program, location, content, schema } = data;

        return (
            <>
                {/* Schema Markup */}
                {schema && (
                    <script
                        type="application/ld+json"
                        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
                    />
                )}

                <div className="min-h-screen bg-white">
                    {/* Breadcrumb */}
                    <div className="bg-gray-50 border-b border-gray-200 py-3 px-6">
                        <div className="max-w-7xl mx-auto">
                            <nav className="text-sm">
                                <Link href="/" className="text-[#1daed4] hover:underline">
                                    Home
                                </Link>
                                <span className="mx-2 text-gray-400">/</span>
                                <Link href="/programs" className="text-[#1daed4] hover:underline">
                                    Programs
                                </Link>
                                <span className="mx-2 text-gray-400">/</span>
                                <span className="text-[#636363]">{program.title} in {location.city}</span>
                            </nav>
                        </div>
                    </div>

                    {/* Hero */}
                    <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
                        <div className="max-w-7xl mx-auto">
                            <p className="text-[#1daed4] font-semibold mb-2">
                                {formatProgramType(program.slug)} in {location.state}
                            </p>
                            <h1 className="text-5xl font-bold text-[#636363] mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                                {data.h1}
                            </h1>
                            <p className="text-lg text-[#636363] mb-6">
                                Serving {location.city} from our {location.office.name}
                            </p>
                            <Link
                                href="/quote"
                                className="inline-block bg-[#1daed4] text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-[#17a0c4] transition-colors shadow-lg"
                                style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                            >
                                Get {location.city} Rates
                            </Link>
                        </div>
                    </div>

                    {/* Main Content */}
                    <div className="max-w-7xl mx-auto py-12 px-6">
                        <div className="grid md:grid-cols-3 gap-12">
                            <div className="md:col-span-2 prose prose-lg max-w-none prose-headings:text-[#636363] prose-p:text-[#636363] prose-li:text-[#636363] prose-a:text-[#1daed4]">
                                <div dangerouslySetInnerHTML={{ __html: content }} />
                            </div>

                            {/* Sidebar */}
                            <div className="md:col-span-1">
                                <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 shadow-sm sticky top-6">
                                    <h3 className="text-xl font-bold text-[#636363] mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                                        Local Office
                                    </h3>
                                    <p className="font-bold text-[#1daed4]">{location.office.name}</p>
                                    <p className="text-gray-600 mb-4">{location.office.address}</p>

                                    <a
                                        href={`tel:${location.office.phone}`}
                                        className="block w-full text-center py-3 bg-[#636363] text-white font-bold rounded-lg hover:bg-gray-700 transition-colors"
                                    >
                                        Call {location.office.phone}
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </>
        );
    }

    // Fallback
    notFound();
}

function formatProgramType(slug: string) {
    return slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}
