import {
  getProgramPages,
  getProgramBySlug,
  formatProgramType,
  formatLoanAmount,
  CMSProgramPage,
} from '@/lib/wagtail-api';
import { notFound } from 'next/navigation';
import Link from 'next/link';
import { Metadata } from 'next';

interface Props {
  params: Promise<{ slug: string }>;
}

/**
 * Generate static paths for all program pages at build time
 * Returns empty array if API is unavailable (e.g., during Vercel build)
 * Pages will be generated on-demand instead
 */
export async function generateStaticParams() {
  try {
    const programs = await getProgramPages();
    return programs.map((program) => ({
      slug: program.meta.slug,
    }));
  } catch (error) {
    console.warn('Failed to fetch programs for static generation:', error);
    return []; // Return empty array - pages will be generated on-demand
  }
}

/**
 * Generate metadata for SEO
 */
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const { slug } = await params;
    const program = await getProgramBySlug(slug);

    if (!program) {
      return { title: 'Program Not Found | Custom Mortgage' };
    }

    const description =
      program.mortgage_program_highlights?.replace(/<[^>]*>/g, '').slice(0, 160) ||
      `Learn about ${program.title} from Custom Mortgage. Competitive rates and expert service.`;

    return {
      title: `${program.title} | Custom Mortgage`,
      description,
      openGraph: {
        title: `${program.title} | Custom Mortgage`,
        description,
        type: 'website',
      },
    };
  } catch (error) {
    console.error('Failed to fetch program metadata:', error);
    return { title: 'Program | Custom Mortgage' };
  }
}

/**
 * Generate MortgageLoan schema markup for SEO
 */
function generateSchemaMarkup(program: CMSProgramPage) {
  return {
    '@context': 'https://schema.org',
    '@type': 'MortgageLoan',
    name: program.title,
    loanType: formatProgramType(program.program_type),
    ...(program.minimum_loan_amount &&
      program.maximum_loan_amount && {
      amount: {
        '@type': 'MonetaryAmount',
        minValue: parseFloat(program.minimum_loan_amount),
        maxValue: parseFloat(program.maximum_loan_amount),
        currency: 'USD',
      },
    }),
    provider: {
      '@type': 'FinancialService',
      name: 'Custom Mortgage Inc.',
      url: 'https://custommortgageinc.com',
    },
  };
}

/**
 * Render rich text content safely
 */
function RichTextContent({ html, className }: { html: string; className?: string }) {
  if (!html) return null;
  return (
    <div
      className={`prose prose-lg max-w-none prose-headings:text-[#636363] prose-p:text-[#636363] prose-li:text-[#636363] prose-a:text-[#1daed4] ${className || ''}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}

export default async function ProgramDetailPage({ params }: Props) {
  let program = null;
  try {
    const { slug } = await params;
    program = await getProgramBySlug(slug);
  } catch (error) {
    console.error('Failed to fetch program detail:', error);
  }

  if (!program) {
    notFound();
  }

  const schemaMarkup = generateSchemaMarkup(program);

  return (
    <>
      {/* Schema Markup for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaMarkup) }}
      />

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
              <span className="text-[#636363]">{program.title}</span>
            </nav>
          </div>
        </div>

        {/* Hero Section */}
        <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
              <div>
                <p className="text-[#1daed4] font-semibold mb-2">
                  {formatProgramType(program.program_type)}
                </p>
                <h2
                  className="text-5xl font-bold text-[#636363] mb-4"
                >
                  {program.title}
                </h2>
                {program.target_city && program.target_state && (
                  <p className="text-lg text-[#636363]">
                    Serving {program.target_city}, {program.target_state}
                  </p>
                )}
              </div>
              <Link
                href="/quote"
                className="inline-block bg-[#1daed4] text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-[#17a0c4] transition-colors shadow-lg text-center font-heading"
              >
                Get Your Quote
              </Link>
            </div>
          </div>
        </div>

        {/* Key Stats */}
        <div className="max-w-7xl mx-auto py-8 px-6">
          <div className="grid md:grid-cols-4 gap-4">
            {program.minimum_loan_amount && (
              <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 text-center">
                <p className="text-sm text-[#a5a5a5] uppercase tracking-wide">Min Loan</p>
                <p className="text-2xl font-bold text-[#636363] mt-2">
                  {formatLoanAmount(program.minimum_loan_amount)}
                </p>
              </div>
            )}
            {program.maximum_loan_amount && (
              <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 text-center">
                <p className="text-sm text-[#a5a5a5] uppercase tracking-wide">Max Loan</p>
                <p className="text-2xl font-bold text-[#636363] mt-2">
                  {formatLoanAmount(program.maximum_loan_amount)}
                </p>
              </div>
            )}
            {program.min_credit_score && (
              <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 text-center">
                <p className="text-sm text-[#a5a5a5] uppercase tracking-wide">Min Credit Score</p>
                <p className="text-2xl font-bold text-[#636363] mt-2">{program.min_credit_score}</p>
              </div>
            )}
            {program.max_ltv && (
              <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 text-center">
                <p className="text-sm text-[#a5a5a5] uppercase tracking-wide">Max LTV</p>
                <p className="text-2xl font-bold text-[#636363] mt-2">{program.max_ltv}</p>
              </div>
            )}
            {program.max_debt_to_income_ratio && (
              <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 text-center">
                <p className="text-sm text-[#a5a5a5] uppercase tracking-wide">Max DTI</p>
                <p className="text-2xl font-bold text-[#636363] mt-2">{program.max_debt_to_income_ratio}%</p>
              </div>
            )}
            {program.min_dscr && (
              <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-6 text-center">
                <p className="text-sm text-[#a5a5a5] uppercase tracking-wide">Min DSCR</p>
                <p className="text-2xl font-bold text-[#636363] mt-2">{program.min_dscr}</p>
              </div>
            )}
          </div>
        </div>

        {/* Detailed Specifications */}
        <div className="max-w-7xl mx-auto pb-8 px-6">
          <div className="bg-white border text-[#636363] border-gray-200 rounded-xl p-8 shadow-sm">
            <h3 className="text-3xl font-bold text-[#636363] mb-8">
              Program Specifications
            </h3>
            <div className="grid md:grid-cols-3 gap-8">
              {/* Property Specs */}
              <div className="space-y-6">
                <h4 className="text-xl font-bold text-[#1daed4] border-b border-gray-100 pb-2">Property Details</h4>

                {program.occupancy_types?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Occupancy</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.occupancy_types.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {program.lien_position?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Lien Position</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.lien_position.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {program.property_types?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Property Types</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.property_types.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}
              </div>

              {/* Loan Terms */}
              <div className="space-y-6">
                <h4 className="text-xl font-bold text-[#1daed4] border-b border-gray-100 pb-2">Loan Terms</h4>

                {program.purpose_of_mortgage?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Purpose</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.purpose_of_mortgage.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {program.amortization_terms?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Amortization</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.amortization_terms.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {program.refinance_types?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Refinance Types</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.refinance_types.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {program.prepayment_penalty && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Prepayment Penalty</h5>
                    <p>{program.prepayment_penalty}</p>
                  </div>
                )}
              </div>

              {/* Borrower & Docs */}
              <div className="space-y-6">
                <h4 className="text-xl font-bold text-[#1daed4] border-b border-gray-100 pb-2">Borrower & Docs</h4>

                {program.borrower_types?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Borrower Types</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.borrower_types.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {program.income_documentation_type?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Income Documentation</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.income_documentation_type.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {program.citizenship_requirements?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Citizenship</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.citizenship_requirements.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {program.credit_events_allowed?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Credit Events</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.credit_events_allowed.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}

                {program.mortgage_lates_allowed?.length > 0 && (
                  <div>
                    <h5 className="font-semibold mb-2 text-sm uppercase tracking-wide text-gray-400">Mortgage Lates</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {program.mortgage_lates_allowed.map(t => <li key={t}>{t}</li>)}
                    </ul>
                  </div>
                )}
              </div>

            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-7xl mx-auto py-8 px-6">
          <div className="grid lg:grid-cols-3 gap-12">
            {/* Content Column */}
            <div className="lg:col-span-2 space-y-10">
              {/* Program Highlights */}
              {program.mortgage_program_highlights && (
                <section>
                  <h3
                    className="text-3xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                  >
                    Program Highlights
                  </h3>
                  <RichTextContent html={program.mortgage_program_highlights} />
                </section>
              )}

              {/* What Are These Loans */}
              {program.what_are && (
                <section>
                  <h3
                    className="text-3xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                  >
                    What Are {program.title}?
                  </h3>
                  <RichTextContent html={program.what_are} />
                </section>
              )}

              {/* Program Details */}
              {program.details_about_mortgage_loan_program && (
                <section>
                  <h3
                    className="text-3xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                  >
                    Program Details
                  </h3>
                  <RichTextContent html={program.details_about_mortgage_loan_program} />
                </section>
              )}

              {/* Benefits */}
              {program.benefits_of && (
                <section>
                  <h3
                    className="text-3xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                  >
                    Benefits
                  </h3>
                  <RichTextContent html={program.benefits_of} />
                </section>
              )}

              {/* Requirements */}
              {program.requirements && (
                <section>
                  <h3
                    className="text-3xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                  >
                    Requirements
                  </h3>
                  <RichTextContent html={program.requirements} />
                </section>
              )}

              {/* How to Qualify */}
              {program.how_to_qualify_for && (
                <section>
                  <h3
                    className="text-3xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                  >
                    How to Qualify
                  </h3>
                  <RichTextContent html={program.how_to_qualify_for} />
                </section>
              )}

              {/* FAQ Section */}
              {program.faq && program.faq.length > 0 && (
                <section className="bg-gray-50 rounded-xl p-8 border border-gray-200">
                  <h3
                    className="text-3xl font-bold text-[#636363] mb-8"
                  >
                    Frequently Asked Questions
                  </h3>
                  <div className="space-y-6">
                    {program.faq.map((item, idx) => (
                      <div key={idx} className="border-b border-gray-200 pb-6 last:border-b-0">
                        <h4 className="text-xl font-bold text-[#636363] mb-3">
                          {item.value.question}
                        </h4>
                        <RichTextContent html={item.value.answer} className="prose-sm" />
                      </div>
                    ))}
                  </div>
                </section>
              )}
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="sticky top-24 space-y-6">
                {/* Contact Card */}
                <div className="bg-[#636363] text-white rounded-xl p-8 shadow-lg">
                  <h4
                    className="text-2xl font-bold mb-4"
                  >
                    Speak with an Expert
                  </h4>
                  <p className="text-white/80 mb-6">
                    Get a personalized quote for {program.title} in minutes.
                  </p>
                  <Link
                    href="/quote"
                    className="block w-full text-center py-4 bg-[#1daed4] text-white font-bold rounded-lg hover:bg-[#17a0c4] transition-colors shadow-md font-heading"
                  >
                    Get Started
                  </Link>
                  <a
                    href="tel:8779765669"
                    className="block w-full text-center py-4 mt-4 bg-transparent border-2 border-white/30 text-white font-bold rounded-lg hover:bg-white/10 transition-colors font-heading"
                  >
                    Call (877) 976-5669
                  </a>
                </div>

                {/* Property Types */}
                {program.property_types && program.property_types.length > 0 && (
                  <div className="bg-white border-2 border-gray-100 rounded-xl p-6 shadow-sm">
                    <h4
                      className="text-xl font-bold text-[#636363] mb-4"
                    >
                      Eligible Properties
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {program.property_types.map((type) => (
                        <span
                          key={type}
                          className="px-3 py-1 bg-gray-100 text-[#636363] text-xs font-bold rounded-full uppercase"
                        >
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Final CTA */}
        <section className="py-20 px-6 bg-[#636363] text-white">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              Nationwide {program.title} Lending
            </h2>
            <p className="text-xl mb-10 opacity-90">
              Custom Mortgage provides flexible financing solutions in 48 states.
              Our technology-driven approach ensures faster approvals and competitive rates.
            </p>
            <Link href="/quote"
              className="inline-block bg-[#1daed4] text-white px-10 py-5 rounded-lg font-bold text-xl hover:bg-[#17a0c4] transition-colors shadow-xl font-heading">
              Get Your Custom Quote
            </Link>
          </div>
        </section>
      </div>
    </>
  );
}
