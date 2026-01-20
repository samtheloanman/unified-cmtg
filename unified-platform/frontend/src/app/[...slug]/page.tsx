import { resolvePath, getPageBySlug, WagtailPage } from '@/lib/wagtail-api';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import Link from 'next/link';

interface Props {
    params: Promise<{ slug: string[] }>;
}

/**
 * Format slug text for display
 */
function formatSlug(slug: string) {
    if (!slug) return '';
    return slug.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

/**
 * Generate Metadata for SEO
 */
export async function generateMetadata({ params }: Props): Promise<Metadata> {
    try {
        const { slug } = await params;
        const path = '/' + slug.join('/') + '/';

        // 1. Try resolving as Programmatic SEO Page
        const result = await resolvePath(path);
        if (result && result.type === 'program_location') {
            const data = result.data as any;
            return {
                title: data.title,
                description: data.meta_description,
            };
        }

        // 2. Try resolving as standard Wagtail Page
        const pageSlug = slug[slug.length - 1];
        const page = await getPageBySlug(pageSlug);
        if (page) {
            return {
                title: `${page.title} | Custom Mortgage`,
            };
        }
    } catch (error) {
        console.error('Metadata resolution failed:', error);
    }

    return { title: 'Custom Mortgage' };
}

export default async function CatchAllPage({ params }: Props) {
    let slug: string[] = [];
    try {
        const resolveParams = await params;
        slug = resolveParams.slug;
    } catch (error) {
        console.error('Failed to resolve params:', error);
        notFound();
    }

    const path = '/' + slug.join('/') + '/';

    // 1. Attempt Dynamic Router Resolution (Programmatic SEO)
    try {
        const result = await resolvePath(path);

        if (result && result.type === 'program_location') {
            const { data } = result as any;
            const { program, location, content, schema } = data;

            return (
                <>
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
                                    <Link href="/" className="text-[#1daed4] hover:underline">Home</Link>
                                    <span className="mx-2 text-gray-400">/</span>
                                    <Link href="/programs" className="text-[#1daed4] hover:underline">Programs</Link>
                                    <span className="mx-2 text-gray-400">/</span>
                                    <span className="text-[#636363]">{program?.title} in {location?.city}</span>
                                </nav>
                            </div>
                        </div>

                        {/* Hero Section */}
                        <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
                            <div className="max-w-7xl mx-auto">
                                <p className="text-[#1daed4] font-semibold mb-2">
                                    {formatSlug(program?.slug)} in {location?.state}
                                </p>
                                <h1 className="text-5xl font-bold text-[#636363] mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                                    {data.h1}
                                </h1>
                                <p className="text-lg text-[#636363] mb-6">
                                    Serving {location?.city} from our {location?.office?.name}
                                </p>
                                <Link href="/quote" className="inline-block bg-[#1daed4] text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-[#17a0c4] transition-colors shadow-lg" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                                    Get {location?.city} Rates
                                </Link>
                            </div>
                        </div>

                        {/* Content Grid */}
                        <div className="max-w-7xl mx-auto py-12 px-6">
                            <div className="grid md:grid-cols-3 gap-12">
                                <div className="md:col-span-2 prose prose-lg max-w-none prose-headings:text-[#636363] prose-p:text-[#636363] prose-li:text-[#636363] prose-a:text-[#1daed4]">
                                    <div dangerouslySetInnerHTML={{ __html: content }} />
                                </div>
                                <div className="md:col-span-1">
                                    {location?.office && (
                                        <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 shadow-sm sticky top-6">
                                            <h3 className="text-xl font-bold text-[#636363] mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>Local Office</h3>
                                            <p className="font-bold text-[#1daed4]">{location.office.name}</p>
                                            <p className="text-gray-600 mb-4">{location.office.address}</p>
                                            <a href={`tel:${location.office.phone}`} className="block w-full text-center py-3 bg-[#636363] text-white font-bold rounded-lg hover:bg-gray-700 transition-colors">Call {location.office.phone}</a>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            );
        }
    } catch (error) {
        console.error('Dynamic route resolution failed:', error);
    }

    // 2. Fallback to Standard Wagtail Page
    try {
        const pageSlug = slug[slug.length - 1];
        const page = await getPageBySlug<any>(pageSlug);

        if (page) {
            return (
                <div className="min-h-screen bg-white">
                    <div className="max-w-4xl mx-auto py-20 px-6">
                        <h1 className="text-5xl font-bold text-[#0f2933] mb-12 uppercase tracking-tighter" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                            {page.title}
                        </h1>
                        <div 
                            className="prose prose-lg max-w-none prose-headings:text-[#0f2933] prose-p:text-gray-600"
                            dangerouslySetInnerHTML={{ __html: page.body || page.content || '<p>No content available.</p>' }} 
                        />
                    </div>
                </div>
            );
        }
    } catch (error) {
        console.error('Wagtail page fetch failed:', error);
    }

    notFound();
}
