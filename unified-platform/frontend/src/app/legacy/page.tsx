
import { getPages, type LegacyIndexPage, type LegacyRecreatedPage } from '@/lib/wagtail-api';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
    title: 'Legacy Site Archive | Custom Mortgage',
    description: 'Archive of pages from the previous version of the Custom Mortgage website.',
};

export default async function LegacyIndexPage() {
    // Fetch the Legacy Index Page to get intro content
    const pages = await getPages<LegacyIndexPage>('cms.LegacyIndexPage');
    const indexPage = pages[0];

    // Fetch all legacy recreated pages
    const legacyPages = await getPages<LegacyRecreatedPage>('cms.LegacyRecreatedPage');

    return (
        <div className="min-h-screen bg-white">
            {/* Header */}
            <div className="bg-[#636363] text-white py-4 px-6 md:px-12">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <Link href="/">
                        <h1 className="text-3xl font-bold tracking-wide font-heading">
                            CUSTOM MORTGAGE
                        </h1>
                    </Link>
                    <span className="text-sm tracking-widest hidden sm:block font-heading">
                        LEGACY ARCHIVE
                    </span>
                </div>
            </div>

            <main className="max-w-7xl mx-auto py-12 px-6">
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <p className="text-sm text-yellow-700">
                                This section contains strict recreations of pages from our previous website. Content formatting may vary from the new design system.
                            </p>
                        </div>
                    </div>
                </div>

                <h1 className="text-4xl font-bold text-[#636363] mb-8 font-heading">
                    Legacy Content Archive
                </h1>

                {indexPage?.intro && (
                    <div className="prose max-w-none mb-12" dangerouslySetInnerHTML={{ __html: indexPage.intro }} />
                )}

                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                    {legacyPages.map((page) => (
                        <Link
                            key={page.id}
                            href={`/legacy/${page.meta.slug}`}
                            className="block bg-white border border-gray-200 rounded-lg hover:shadow-lg transition-shadow p-6"
                        >
                            <h2 className="text-xl font-bold text-[#1daed4] mb-2">{page.title}</h2>
                            <p className="text-sm text-gray-500 mb-4">Original URL: {page.original_url || 'N/A'}</p>
                            <span className="text-sm font-medium text-[#636363] hover:text-[#1daed4]">
                                View Archived Page &rarr;
                            </span>
                        </Link>
                    ))}
                </div>

                {legacyPages.length === 0 && (
                    <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                        <p className="text-gray-500">No legacy pages have been archived yet.</p>
                        <p className="text-sm text-gray-400 mt-2">Jules is currently extracting content...</p>
                    </div>
                )}
            </main>
        </div>
    );
}
