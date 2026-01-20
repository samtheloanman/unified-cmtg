import { getProgramPages, formatProgramType, formatLoanAmount, CMSProgramPage } from '@/lib/wagtail-api';
import Link from 'next/link';
import { Metadata } from 'next';

export const metadata: Metadata = {
    title: 'Loan Programs | Custom Mortgage',
    description:
        'Explore our comprehensive range of mortgage loan programs including DSCR, FHA, VA, Conventional, Non-QM, and more. Nationwide lending with competitive rates.',
    openGraph: {
        title: 'Loan Programs | Custom Mortgage',
        description:
            'Explore our comprehensive range of mortgage loan programs including DSCR, FHA, VA, Conventional, Non-QM, and more.',
        type: 'website',
    },
};

/**
 * Group programs by program type for organized display
 */
function groupByProgramType(programs: CMSProgramPage[]): Record<string, CMSProgramPage[]> {
    return programs.reduce(
        (acc, program) => {
            const type = program.program_type || 'other';
            if (!acc[type]) {
                acc[type] = [];
            }
            acc[type].push(program);
            return acc;
        },
        {} as Record<string, CMSProgramPage[]>
    );
}

export default async function ProgramsIndexPage() {
    let programs: CMSProgramPage[] = [];

    try {
        programs = await getProgramPages();
    } catch (error) {
        console.error('Failed to fetch programs:', error);
        // programs remains empty array
    }

    const groupedPrograms = groupByProgramType(programs);

    // Order of program type display
    const typeOrder = ['residential', 'commercial', 'nonqm', 'hard_money', 'reverse_mortgage'];
    const sortedTypes = typeOrder.filter((type) => groupedPrograms[type]?.length > 0);

    return (
        <div className="bg-white">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
                <div className="max-w-7xl mx-auto">
                    <h1
                        className="text-5xl font-bold text-[#636363] mb-4"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Loan Programs
                    </h1>
                    <p className="text-lg text-[#636363] max-w-2xl">
                        Explore our comprehensive range of financing solutions. We specialize in unique mortgage
                        requirements with expert, client-focused service across all 50 states.
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto py-12 px-6">
                {programs.length === 0 ? (
                    <div className="text-center py-12">
                        <p className="text-[#636363] text-lg">
                            No programs available at this time. Please check back later.
                        </p>
                    </div>
                ) : (
                    <div className="space-y-12">
                        {sortedTypes.map((type) => (
                            <section key={type}>
                                <h3
                                    className="text-3xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                                >
                                    {formatProgramType(type)} Programs
                                </h3>

                                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                                    {groupedPrograms[type].map((program) => (
                                        <Link
                                            key={program.id}
                                            href={`/programs/${program.meta.slug}`}
                                            className="block bg-white border-2 border-[#a5a5a5] rounded-lg shadow-lg hover:border-[#1daed4] hover:shadow-xl transition-all overflow-hidden group"
                                        >
                                            {/* Card Header */}
                                            <div className="bg-[#636363] group-hover:bg-[#1daed4] text-white px-6 py-4 transition-colors">
                                                <h4
                                                    className="text-xl font-bold"
                                                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                                                >
                                                    {program.title}
                                                </h4>
                                                <p className="text-white/80 text-sm mt-1">
                                                    {formatProgramType(program.program_type)}
                                                </p>
                                            </div>

                                            {/* Card Body */}
                                            <div className="p-6 space-y-4">
                                                {/* Quick Stats */}
                                                <div className="grid grid-cols-2 gap-4 text-sm">
                                                    {program.minimum_loan_amount && (
                                                        <div>
                                                            <p className="text-[#a5a5a5]">Min Loan</p>
                                                            <p className="text-[#636363] font-semibold">
                                                                {formatLoanAmount(program.minimum_loan_amount)}
                                                            </p>
                                                        </div>
                                                    )}
                                                    {program.maximum_loan_amount && (
                                                        <div>
                                                            <p className="text-[#a5a5a5]">Max Loan</p>
                                                            <p className="text-[#636363] font-semibold">
                                                                {formatLoanAmount(program.maximum_loan_amount)}
                                                            </p>
                                                        </div>
                                                    )}
                                                    {program.min_credit_score && (
                                                        <div>
                                                            <p className="text-[#a5a5a5]">Min Credit</p>
                                                            <p className="text-[#636363] font-semibold">
                                                                {program.min_credit_score}
                                                            </p>
                                                        </div>
                                                    )}
                                                    {program.max_ltv && (
                                                        <div>
                                                            <p className="text-[#a5a5a5]">Max LTV</p>
                                                            <p className="text-[#636363] font-semibold">{program.max_ltv}</p>
                                                        </div>
                                                    )}
                                                </div>

                                                {/* Interest Rates */}
                                                {program.interest_rates && (
                                                    <div className="pt-4 border-t border-[#a5a5a5]/30">
                                                        <p className="text-xs text-[#a5a5a5] uppercase tracking-wide">
                                                            Interest Rates
                                                        </p>
                                                        <p className="text-xl font-bold text-[#1daed4] mt-1">
                                                            {program.interest_rates}
                                                        </p>
                                                    </div>
                                                )}

                                                {/* Property Types Tags */}
                                                {program.property_types && program.property_types.length > 0 && (
                                                    <div className="pt-4 border-t border-[#a5a5a5]/30">
                                                        <div className="flex flex-wrap gap-2">
                                                            {program.property_types.slice(0, 3).map((type) => (
                                                                <span
                                                                    key={type}
                                                                    className="px-3 py-1 bg-[#1daed4]/10 text-[#1daed4] text-xs font-semibold rounded-full"
                                                                >
                                                                    {type}
                                                                </span>
                                                            ))}
                                                            {program.property_types.length > 3 && (
                                                                <span className="px-3 py-1 bg-[#636363]/10 text-[#636363] text-xs font-semibold rounded-full">
                                                                    +{program.property_types.length - 3} more
                                                                </span>
                                                            )}
                                                        </div>
                                                    </div>
                                                )}

                                                {/* CTA */}
                                                <div className="pt-4">
                                                    <span
                                                        className="inline-block w-full text-center py-3 bg-[#1daed4] text-white font-bold rounded-lg group-hover:bg-[#17a0c4] transition-colors"
                                                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                                                    >
                                                        Learn More
                                                    </span>
                                                </div>
                                            </div>
                                        </Link>
                                    ))}
                                </div>
                            </section>
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
                        Ready to Get Started?
                    </h3>
                    <p className="text-lg mb-8 text-white/90">
                        Get a personalized quote in minutes. Our expert team is ready to help you find the
                        perfect financing solution.
                    </p>
                    <Link
                        href="/quote"
                        className="inline-block bg-white text-[#636363] px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors shadow-lg"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Get Your Quote Now
                    </Link>
                </div>
            </div>
        </div>
    );
}
