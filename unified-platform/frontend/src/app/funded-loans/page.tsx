import { getFundedLoanPages, formatLoanAmount } from '@/lib/wagtail-api';
import Link from 'next/link';
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Funded Loans | Custom Mortgage',
    description:
        'Explore our recent funded loan case studies. We provide financing for residential, commercial, and investment properties nationwide.',
    openGraph: {
        title: 'Funded Loans | Custom Mortgage',
        description:
            'Explore our recent funded loan case studies. We provide financing for residential, commercial, and investment properties nationwide.',
        type: 'website',
    },
};

export default async function FundedLoansIndexPage() {
    const loans = await getFundedLoanPages();

    return (
        <div className="bg-white">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
                <div className="max-w-7xl mx-auto">
                    <h1
                        className="text-5xl font-bold text-[#636363] mb-4"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Recent Funded Loans
                    </h1>
                    <p className="text-lg text-[#636363] max-w-2xl">
                        See real examples of loans we've closed for our clients. From complex non-QM scenarios to standard residential purchases.
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto py-12 px-6">
                {loans.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-[#636363] text-lg">No funded loans available to display.</p>
                    </div>
                ) : (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {loans.map((loan) => (
                            <Link key={loan.id} href={`/funded-loans/${loan.meta.slug}`} className="block group h-full">
                                <div className="bg-white border-2 border-gray-200 rounded-xl overflow-hidden hover:border-[#1daed4] transition-all h-full shadow-sm hover:shadow-md flex flex-col">
                                    {/* Image Placeholder - handled by Next.js or generic if no image */}
                                    <div className="h-48 bg-gray-100 flex items-center justify-center">
                                        <span className="text-[#a5a5a5] font-bold">
                                            {formatLoanAmount(loan.loan_amount || '0')}
                                        </span>
                                    </div>

                                    <div className="p-6 flex-1 flex flex-col">
                                        <div className="mb-4">
                                            <span className="inline-block px-3 py-1 bg-[#1daed4]/10 text-[#1daed4] text-xs font-bold rounded-full uppercase tracking-wide">
                                                {loan.loan_type || 'Mortgage'}
                                            </span>
                                        </div>

                                        <h3
                                            className="text-xl font-bold text-[#636363] mb-2 group-hover:text-[#1daed4] transition-colors"
                                            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                                        >
                                            {loan.title}
                                        </h3>

                                        {loan.location && (
                                            <p className="text-[#636363] text-sm mb-4 flex items-center gap-1">
                                                📍 {loan.location}
                                            </p>
                                        )}

                                        <div className="mt-auto pt-4 border-t border-gray-100 grid grid-cols-2 gap-4">
                                            <div>
                                                <p className="text-xs text-[#a5a5a5] uppercase">Amount</p>
                                                <p className="font-bold text-[#636363]">{formatLoanAmount(loan.loan_amount)}</p>
                                            </div>
                                            {loan.property_type && (
                                                <div className="text-right">
                                                    <p className="text-xs text-[#a5a5a5] uppercase">Property</p>
                                                    <p className="font-bold text-[#636363]">{loan.property_type}</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>

            {/* CTA Section */}
            <div className="bg-[#1daed4] py-12 px-6">
                <div className="max-w-4xl mx-auto text-center text-white">
                    <h3
                        className="text-4xl font-bold mb-4"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Want Results Like These?
                    </h3>
                    <p className="text-lg mb-8 text-white/90">
                        Get a personalized mortgage quote in minutes.
                    </p>
                    <Link
                        href="/quote"
                        className="inline-block bg-white text-[#636363] px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors shadow-lg"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Get Your Quote
                    </Link>
                </div>
            </div>
        </div>
    );
}
