import {
    getFundedLoanPages,
    getFundedLoanBySlug,
    formatLoanAmount,
    FundedLoanPage,
} from '@/lib/wagtail-api';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { Metadata } from 'next';

interface Props {
    params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
    try {
        const loans = await getFundedLoanPages();
        return loans.map((loan) => ({
            slug: loan.meta.slug,
        }));
    } catch (error) {
        console.warn('Failed to fetch funded loans for static generation:', error);
        return []; // Return empty array - pages will be generated on-demand
    }
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    try {
        const { slug } = await params;
        const loan = await getFundedLoanBySlug(slug);

        if (!loan) {
            return { title: 'Loan Not Found | Custom Mortgage' };
        }

        const description =
            loan.description?.replace(/<[^>]*>/g, '').slice(0, 160) ||
            `Funded loan case study: ${loan.title} in ${loan.location || 'US'}.`;

        return {
            title: `${loan.title} | Funded Loans`,
            description,
            openGraph: {
                title: `${loan.title} | Funded Loans`,
                description,
                type: 'article',
            },
        };
    } catch (error) {
        console.error('Failed to fetch funded loan metadata:', error);
        return { title: 'Funded Loan | Custom Mortgage' };
    }
}

function RichTextContent({ html, className }: { html: string; className?: string }) {
    if (!html) return null;
    return (
        <div
            className={`prose prose-lg max-w-none prose-headings:text-[#636363] prose-p:text-[#636363] prose-li:text-[#636363] prose-a:text-[#1daed4] ${className || ''}`}
            dangerouslySetInnerHTML={{ __html: html }}
        />
    );
}

export default async function FundedLoanDetailPage({ params }: Props) {
    const { slug } = await params;
    const loan = await getFundedLoanBySlug(slug);

    if (!loan) {
        notFound();
    }

    return (
        <div className="min-h-screen bg-white">
            {/* Breadcrumb */}
            <div className="bg-gray-50 border-b border-gray-200 py-3 px-6">
                <div className="max-w-7xl mx-auto">
                    <nav className="text-sm">
                        <Link href="/" className="text-[#1daed4] hover:underline">
                            Home
                        </Link>
                        <span className="mx-2 text-gray-400">/</span>
                        <Link href="/funded-loans" className="text-[#1daed4] hover:underline">
                            Funded Loans
                        </Link>
                        <span className="mx-2 text-gray-400">/</span>
                        <span className="text-[#636363]">{loan.title}</span>
                    </nav>
                </div>
            </div>

            {/* Hero Section */}
            <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
                <div className="max-w-7xl mx-auto">
                    <p className="text-[#1daed4] font-semibold mb-2 uppercase tracking-wide">
                        Funded Loan Case Study
                    </p>
                    <h1
                        className="text-4xl md:text-5xl font-bold text-[#636363] mb-4"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        {loan.title}
                    </h1>
                    {loan.location && (
                        <p className="text-xl text-[#636363] flex items-center gap-2">
                            📍 {loan.location}
                        </p>
                    )}
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto py-12 px-6">
                <div className="grid lg:grid-cols-3 gap-12">
                    {/* Sidebar Stats (Left on Desktop) */}
                    <div className="lg:col-span-1 order-2 lg:order-1">
                        <div className="bg-gray-50 border-2 border-gray-200 rounded-xl p-6 sticky top-6 space-y-6">
                            <div>
                                <p className="text-sm text-[#a5a5a5] uppercase tracking-wide">Loan Amount</p>
                                <p className="text-3xl font-bold text-[#636363] mt-1">
                                    {formatLoanAmount(loan.loan_amount)}
                                </p>
                            </div>

                            <div className="border-t border-gray-200 pt-4">
                                <p className="text-sm text-[#a5a5a5] uppercase tracking-wide">Loan Type</p>
                                <p className="text-xl font-bold text-[#636363] mt-1">
                                    {loan.loan_type || 'N/A'}
                                </p>
                            </div>

                            <div className="border-t border-gray-200 pt-4">
                                <p className="text-sm text-[#a5a5a5] uppercase tracking-wide">Property Type</p>
                                <p className="text-xl font-bold text-[#636363] mt-1">
                                    {loan.property_type || 'N/A'}
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Content (Right on Desktop) */}
                    <div className="lg:col-span-2 order-1 lg:order-2">
                        <div className="prose prose-lg max-w-none">
                            <h3
                                className="text-2xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                                style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                            >
                                Deal Highlights
                            </h3>
                            <RichTextContent html={loan.description} />
                        </div>
                    </div>
                </div>
            </div>

            {/* CTA Section */}
            <div className="bg-[#1daed4] py-12 px-6">
                <div className="max-w-4xl mx-auto text-center text-white">
                    <h3
                        className="text-4xl font-bold mb-4"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Have a Similar Scenario?
                    </h3>
                    <p className="text-lg mb-8 text-white/90">
                        We specialize in complex loan scenarios. Get a quote today.
                    </p>
                    <Link
                        href="/quote"
                        className="inline-block bg-white text-[#636363] px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors shadow-lg"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Get a Quote
                    </Link>
                </div>
            </div>
        </div>
    );
}
