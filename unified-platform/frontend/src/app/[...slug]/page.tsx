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
                    {/* Hero Section - Matching Programs Page */}
                    <div className="relative bg-[#0f2933] text-white py-24 px-6 border-b-8 border-[#1daed4] overflow-hidden">
                        <div className="absolute top-0 right-0 w-1/2 h-full bg-[#1daed4]/5 -skew-x-12 transform translate-x-32" />

                        <div className="max-w-7xl mx-auto relative z-10">
                            <div className="flex items-center gap-2 text-[#1daed4] font-bold tracking-widest uppercase mb-4 text-sm animate-fade-in-up">
                                <Link href="/programs" className="hover:text-white transition-colors">Programs</Link>
                                <span>/</span>
                                <span>{formatProgramType(program.slug)}</span>
                            </div>

                            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-none max-w-4xl"
                                style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                                {data.h1}
                            </h1>

                            <div className="flex items-center gap-4 text-gray-300 text-lg font-light">
                                <span className="w-12 h-1 bg-[#1daed4]" />
                                <p>Serving {location.city}, {location.state} from {location.office.name}</p>
                            </div>
                        </div>
                    </div>

                    {/* Main Content */}
                    <div className="max-w-7xl mx-auto py-16 px-6">
                        <div className="grid md:grid-cols-12 gap-12">
                            {/* Content Column */}
                            <div className="md:col-span-8">
                                <article className="prose prose-lg max-w-none 
                                    prose-headings:font-bold prose-headings:text-[#0f2933] prose-headings:font-heading
                                    prose-h2:text-4xl prose-h2:mt-12 prose-h2:mb-6
                                    prose-h3:text-2xl prose-h3:text-[#1daed4]
                                    prose-p:text-gray-600 prose-p:leading-relaxed
                                    prose-li:text-gray-600
                                    prose-strong:text-[#0f2933]
                                    prose-a:text-[#1daed4] prose-a:no-underline hover:prose-a:text-[#0f8aab]
                                    prose-blockquote:border-l-4 prose-blockquote:border-[#1daed4] prose-blockquote:bg-gray-50 prose-blockquote:px-6 prose-blockquote:py-4 prose-blockquote:not-italic
                                ">
                                    <div dangerouslySetInnerHTML={{ __html: content }} />
                                </article>
                            </div>

                            {/* Sidebar Column */}
                            <div className="md:col-span-4 space-y-8">
                                {/* Local Office Card */}
                                <div className="bg-[#f8f9fa] border-l-4 border-[#0f2933] p-8 shadow-sm">
                                    <h3 className="text-3xl font-bold text-[#0f2933] mb-6" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                                        YOUR LOCAL EXPERTS
                                    </h3>
                                    <div className="space-y-4 mb-8">
                                        <div>
                                            <p className="text-xs text-gray-400 uppercase tracking-widest font-bold">Office</p>
                                            <p className="font-bold text-lg text-[#0f2933]">{location.office.name}</p>
                                        </div>
                                        <div>
                                            <p className="text-xs text-gray-400 uppercase tracking-widest font-bold">Address</p>
                                            <p className="text-gray-600">{location.office.address}</p>
                                        </div>
                                    </div>

                                    <a
                                        href={`tel:${location.office.phone}`}
                                        className="block w-full text-center py-4 bg-[#0f2933] text-white font-bold text-lg hover:bg-[#1daed4] transition-colors uppercase tracking-wide"
                                        style={{ fontFamily: 'Bebas Neue, sans-serif' }}
                                    >
                                        Call {location.office.phone}
                                    </a>
                                </div>

                                {/* CTA Card */}
                                <div className="bg-[#1daed4] p-8 text-white relative overflow-hidden group">
                                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -mr-16 -mt-16 transition-transform group-hover:scale-150 duration-700" />
                                    <h3 className="text-3xl font-bold mb-4 relative z-10" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                                        GET A QUOTE TODAY
                                    </h3>
                                    <p className="text-white/90 mb-6 relative z-10 leading-relaxed">
                                        Rates change daily. Lock in your rate for {location.city} properties now.
                                    </p>
                                    <Link
                                        href="/quote"
                                        className="block w-full text-center py-4 bg-white text-[#0f2933] font-bold text-lg hover:bg-[#0f2933] hover:text-white transition-all uppercase tracking-wide relative z-10 shadow-lg"
                                        style={{ fontFamily: 'Bebas Neue, sans-serif' }}
                                    >
                                        Start Quote Request
                                    </Link>
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
