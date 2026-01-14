import { notFound } from 'next/navigation'
import { Metadata } from 'next'

interface PageData {
    id: number
    title: string
    meta: {
        type: string
        slug: string
        html_url: string
    }
    program_type?: string
    mortgage_program_highlights?: string
    details_about_mortgage_loan_program?: string
    benefits_of?: string
    requirements?: string
    how_to_qualify_for?: string
    why_us?: string
    program_faq?: string
    interest_rates?: string
    minimum_loan_amount?: number
    maximum_loan_amount?: number
    min_credit_score?: number
    max_ltv?: string
    body?: string
    original_url?: string
    original_title?: string
    intro?: string
}

// For server-side fetching within Docker, use the service name
const API_URL = process.env.INTERNAL_API_URL || 'http://backend:8000'

async function getPageByPath(slug: string[]): Promise<PageData | null> {
    // Validate slug array
    if (!slug || !Array.isArray(slug) || slug.length === 0) {
        console.error('Invalid slug array:', slug)
        return null
    }

    // Get the last segment as the slug to search for
    const lastSlug = slug[slug.length - 1]

    if (!lastSlug || typeof lastSlug !== 'string') {
        console.error('Invalid lastSlug:', lastSlug)
        return null
    }

    try {
        // Build URL with proper encoding
        const url = new URL(`${API_URL}/api/v2/pages/`)
        url.searchParams.set('slug', lastSlug)
        url.searchParams.set('fields', '*')

        console.log(`Fetching: ${url.toString()}`)

        const response = await fetch(url.toString(), {
            cache: 'no-store', // Disable caching for debugging
            headers: {
                'Accept': 'application/json',
            }
        })

        if (!response.ok) {
            console.error(`API returned ${response.status} for slug: ${lastSlug}`)
            // Try without fields parameter
            const simpleUrl = `${API_URL}/api/v2/pages/?slug=${encodeURIComponent(lastSlug)}`
            const simpleResponse = await fetch(simpleUrl, { cache: 'no-store' })
            if (simpleResponse.ok) {
                const data = await simpleResponse.json()
                if (data.items && data.items.length > 0) {
                    // Get full details by ID
                    const detailRes = await fetch(`${API_URL}/api/v2/pages/${data.items[0].id}/`, { cache: 'no-store' })
                    if (detailRes.ok) {
                        return await detailRes.json()
                    }
                    return data.items[0]
                }
            }
            return null
        }

        const data = await response.json()
        if (data.items && data.items.length > 0) {
            return data.items[0]
        }

        return null
    } catch (error) {
        console.error('Error fetching page:', error)
        return null
    }
}

export default async function DynamicPage({
    params
}: {
    params: Promise<{ slug?: string[] }>
}) {
    let page: PageData | null = null

    try {
        const resolvedParams = await params
        const slugArray = resolvedParams?.slug
        const slug = Array.isArray(slugArray) ? slugArray : []

        if (slug.length === 0) {
            console.log('Empty slug array, returning 404')
            notFound()
        }

        page = await getPageByPath(slug)

        if (!page) {
            console.log('Page not found for slug:', slug)
            notFound()
        }
    } catch (error) {
        console.error('Error in DynamicPage:', error)
        notFound()
    }

    // This should never happen due to notFound() calls above, but TypeScript needs it
    if (!page) {
        notFound()
    }

    // Render based on page type
    const pageType = page.meta?.type

    return (
        <main className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-gradient-to-r from-blue-900 to-blue-700 text-white py-16">
                <div className="container mx-auto px-4">
                    <h1 className="text-4xl md:text-5xl font-bold mb-4">{page.title}</h1>
                    {pageType === 'cms.ProgramPage' && page.program_type && (
                        <span className="inline-block px-4 py-2 bg-white/20 rounded-full text-sm font-medium">
                            {page.program_type.replace('_', ' ').toUpperCase()}
                        </span>
                    )}
                </div>
            </header>

            <div className="container mx-auto px-4 py-12">
                {/* Program Page */}
                {pageType === 'cms.ProgramPage' && (
                    <div className="grid md:grid-cols-3 gap-8">
                        {/* Main Content */}
                        <div className="md:col-span-2 space-y-8">
                            {page.mortgage_program_highlights && (
                                <section className="bg-white rounded-lg shadow-md p-6">
                                    <h2 className="text-2xl font-bold text-blue-900 mb-4">Program Highlights</h2>
                                    <div
                                        className="prose max-w-none"
                                        dangerouslySetInnerHTML={{ __html: page.mortgage_program_highlights }}
                                    />
                                </section>
                            )}

                            {page.details_about_mortgage_loan_program && (
                                <section className="bg-white rounded-lg shadow-md p-6">
                                    <h2 className="text-2xl font-bold text-blue-900 mb-4">Program Details</h2>
                                    <div
                                        className="prose max-w-none"
                                        dangerouslySetInnerHTML={{ __html: page.details_about_mortgage_loan_program }}
                                    />
                                </section>
                            )}

                            {page.benefits_of && (
                                <section className="bg-white rounded-lg shadow-md p-6">
                                    <h2 className="text-2xl font-bold text-blue-900 mb-4">Benefits</h2>
                                    <div
                                        className="prose max-w-none"
                                        dangerouslySetInnerHTML={{ __html: page.benefits_of }}
                                    />
                                </section>
                            )}

                            {page.requirements && (
                                <section className="bg-white rounded-lg shadow-md p-6">
                                    <h2 className="text-2xl font-bold text-blue-900 mb-4">Requirements</h2>
                                    <div
                                        className="prose max-w-none"
                                        dangerouslySetInnerHTML={{ __html: page.requirements }}
                                    />
                                </section>
                            )}

                            {page.how_to_qualify_for && (
                                <section className="bg-white rounded-lg shadow-md p-6">
                                    <h2 className="text-2xl font-bold text-blue-900 mb-4">How to Qualify</h2>
                                    <div
                                        className="prose max-w-none"
                                        dangerouslySetInnerHTML={{ __html: page.how_to_qualify_for }}
                                    />
                                </section>
                            )}

                            {page.program_faq && (
                                <section className="bg-white rounded-lg shadow-md p-6">
                                    <h2 className="text-2xl font-bold text-blue-900 mb-4">FAQs</h2>
                                    <div
                                        className="prose max-w-none"
                                        dangerouslySetInnerHTML={{ __html: page.program_faq }}
                                    />
                                </section>
                            )}
                        </div>

                        {/* Sidebar */}
                        <div className="md:col-span-1">
                            <div className="bg-white rounded-lg shadow-md p-6 sticky top-8">
                                <h3 className="text-xl font-bold text-blue-900 mb-4">Quick Facts</h3>
                                <dl className="space-y-3">
                                    {page.interest_rates && (
                                        <>
                                            <dt className="text-sm text-gray-500">Interest Rates</dt>
                                            <dd className="text-lg font-semibold">{page.interest_rates}</dd>
                                        </>
                                    )}
                                    {page.min_credit_score && (
                                        <>
                                            <dt className="text-sm text-gray-500">Min Credit Score</dt>
                                            <dd className="text-lg font-semibold">{page.min_credit_score}</dd>
                                        </>
                                    )}
                                    {page.max_ltv && (
                                        <>
                                            <dt className="text-sm text-gray-500">Max LTV</dt>
                                            <dd className="text-lg font-semibold">{page.max_ltv}</dd>
                                        </>
                                    )}
                                    {page.minimum_loan_amount && (
                                        <>
                                            <dt className="text-sm text-gray-500">Min Loan Amount</dt>
                                            <dd className="text-lg font-semibold">
                                                ${page.minimum_loan_amount.toLocaleString()}
                                            </dd>
                                        </>
                                    )}
                                    {page.maximum_loan_amount && (
                                        <>
                                            <dt className="text-sm text-gray-500">Max Loan Amount</dt>
                                            <dd className="text-lg font-semibold">
                                                ${page.maximum_loan_amount.toLocaleString()}
                                            </dd>
                                        </>
                                    )}
                                </dl>

                                <div className="mt-6 pt-6 border-t">
                                    <a
                                        href="/quote"
                                        className="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition"
                                    >
                                        Get Your Quote
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Index Pages */}
                {(pageType === 'cms.ProgramIndexPage' || pageType === 'cms.FundedLoanIndexPage' || pageType === 'cms.LegacyIndexPage') && (
                    <div className="bg-white rounded-lg shadow-md p-6">
                        {page.intro && (
                            <div
                                className="prose max-w-none mb-8"
                                dangerouslySetInnerHTML={{ __html: page.intro }}
                            />
                        )}
                        <p className="text-gray-600">
                            Browse the pages in this section using the navigation or search.
                        </p>
                    </div>
                )}

                {/* Standard Page / Legacy Page */}
                {(pageType === 'cms.StandardPage' || pageType === 'cms.LegacyRecreatedPage') && (
                    <div className="bg-white rounded-lg shadow-md p-6">
                        {pageType === 'cms.LegacyRecreatedPage' && page.original_url && (
                            <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
                                <p className="text-sm text-yellow-800">
                                    <strong>Legacy Page:</strong> This is a recreated version of the original page at{' '}
                                    <a href={page.original_url} className="underline" target="_blank" rel="noopener noreferrer">
                                        {page.original_url}
                                    </a>
                                </p>
                            </div>
                        )}
                        {page.body && (
                            <div
                                className="prose max-w-none"
                                dangerouslySetInnerHTML={{ __html: page.body }}
                            />
                        )}
                    </div>
                )}

                {/* Funded Loan Page */}
                {pageType === 'cms.FundedLoanPage' && (
                    <div className="bg-white rounded-lg shadow-md p-6">
                        <div className="grid md:grid-cols-2 gap-6">
                            <div>
                                <h2 className="text-2xl font-bold text-blue-900 mb-4">Loan Details</h2>
                                {/* Add funded loan specific fields here when populated */}
                            </div>
                        </div>
                    </div>
                )}

                {/* CTA Section */}
                <section className="mt-12 bg-gradient-to-r from-blue-900 to-blue-700 text-white rounded-lg p-8 text-center">
                    <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
                    <p className="text-lg mb-6 opacity-90">
                        Get a personalized quote in minutes with our easy online calculator.
                    </p>
                    <a
                        href="/quote"
                        className="inline-block bg-white text-blue-900 font-bold py-3 px-8 rounded-lg hover:bg-gray-100 transition"
                    >
                        Get Your Quote Now
                    </a>
                </section>
            </div>
        </main>
    )
}

export async function generateMetadata({
    params
}: {
    params: Promise<{ slug?: string[] }>
}): Promise<Metadata> {
    try {
        const resolvedParams = await params
        const slugArray = resolvedParams?.slug
        const slug = Array.isArray(slugArray) ? slugArray : []

        if (slug.length === 0) {
            return { title: 'Page Not Found' }
        }

        const page = await getPageByPath(slug)

        if (!page) {
            return { title: 'Page Not Found' }
        }

        // Strip HTML tags for description
        const stripHtml = (html: string) => html.replace(/<[^>]*>/g, '').substring(0, 160)

        return {
            title: `${page.title} | Custom Mortgage Inc`,
            description: page.mortgage_program_highlights
                ? stripHtml(page.mortgage_program_highlights)
                : `Learn about ${page.title} from Custom Mortgage Inc, a nationwide mortgage lender.`
        }
    } catch (error) {
        console.error('Error in generateMetadata:', error)
        return { title: 'Page Not Found' }
    }
}
