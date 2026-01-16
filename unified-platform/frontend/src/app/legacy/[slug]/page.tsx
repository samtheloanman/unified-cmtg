
import { getPageBySlug } from '@/lib/wagtail-api';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import Link from 'next/link';
import { WagtailPage } from '@/lib/wagtail-api';

interface LegacyRecreatedPage extends WagtailPage {
    original_url: string;
    original_title: string;
    body: string;
}

interface Props {
    params: Promise<{ slug: string }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { slug } = await params;
    const page = await getPageBySlug<LegacyRecreatedPage>(slug, 'cms.LegacyRecreatedPage');

    if (!page) {
        return { title: 'Legacy Page Not Found' };
    }

    return {
        title: `${page.title} (Archived) | Custom Mortgage`,
        description: `Archived version of ${page.original_title}`,
    };
}

export default async function LegacySubPage({ params }: Props) {
    const { slug } = await params;
    const page = await getPageBySlug<LegacyRecreatedPage>(slug, 'cms.LegacyRecreatedPage');

    if (!page) {
        notFound();
    }

    return (
        <div className="min-h-screen bg-gray-50 font-sans">
            {/* Disclaimer Banner */}
            <div className="bg-yellow-100 border-b border-yellow-200 p-2 text-center text-sm text-yellow-800">
                You are viewing an archived page. <Link href="/legacy" className="underline font-bold">Return to Archive Index</Link>
            </div>

            <div className="max-w-5xl mx-auto py-12 px-6">
                <div className="bg-white shadow-lg rounded-lg overflow-hidden border border-gray-200">

                    {/* Header */}
                    <div className="bg-gray-100 border-b border-gray-200 px-8 py-6 flex justify-between items-center">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-800">{page.title}</h1>
                            <p className="text-sm text-gray-500 mt-1">
                                Original Source: <a href={page.original_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{page.original_url}</a>
                            </p>
                        </div>
                        <span className="bg-yellow-100 text-yellow-800 text-xs px-3 py-1 rounded-full font-bold uppercase tracking-wide">
                            Legacy Content
                        </span>
                    </div>

                    {/* Content Body */}
                    <div className="p-8">
                        <div
                            className="prose max-w-none prose-a:text-blue-600 prose-headings:font-bold prose-h1:text-3xl"
                            dangerouslySetInnerHTML={{ __html: page.body }}
                        />
                    </div>

                    {/* Footer */}
                    <div className="bg-gray-50 border-t border-gray-200 px-8 py-4 text-center text-sm text-gray-400">
                        Recreated content from custommortgageinc.com
                    </div>
                </div>
            </div>
        </div>
    );
}
