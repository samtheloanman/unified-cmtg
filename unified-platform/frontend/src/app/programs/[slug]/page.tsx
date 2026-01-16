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
 */
export async function generateStaticParams() {
  const programs = await getProgramPages();
  return programs.map((program) => ({
    slug: program.meta.slug,
  }));
}

/**
 * Generate metadata for SEO
 */
export async function generateMetadata({ params }: Props): Promise<Metadata> {
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
  const { slug } = await params;
  const program = await getProgramBySlug(slug);

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
        {/* Header */}
        <div className="bg-[#636363] text-white py-4 px-6">
          <div className="max-w-7xl mx-auto flex justify-between items-center">
            <Link href="/">
              <h1
                className="text-3xl font-bold tracking-wide"
                style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
              >
                CUSTOM MORTGAGE
              </h1>
            </Link>
            <span
              className="text-sm tracking-widest"
              style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
            >
              NATIONWIDE LENDER
            </span>
          </div>
        </div>

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
                  style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
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
                className="inline-block bg-[#1daed4] text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-[#17a0c4] transition-colors shadow-lg text-center"
                style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
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
            {program.interest_rates && (
              <div className="bg-[#1daed4]/10 border-2 border-[#1daed4] rounded-lg p-6 text-center">
                <p className="text-sm text-[#1daed4] uppercase tracking-wide">Interest Rates</p>
                <p className="text-2xl font-bold text-[#1daed4] mt-2">{program.interest_rates}</p>
              </div>
            )}
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
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
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
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
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
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
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
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
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
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
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
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                  >
                    How to Qualify
                  </h3>
                  <RichTextContent html={program.how_to_qualify_for} />
                </section>
              )}

              {/* Why Choose Us */}
              {program.why_us && (
                <section>
                  <h3
                    className="text-3xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                  >
                    Why Choose Custom Mortgage
                  </h3>
                  <RichTextContent html={program.why_us} />
                </section>
              )}

              {/* FAQ */}
              {program.program_faq && (
                <section>
                  <h3
                    className="text-3xl font-bold text-[#636363] mb-6 border-l-4 border-[#1daed4] pl-4"
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                  >
                    Frequently Asked Questions
                  </h3>
                  <RichTextContent html={program.program_faq} />
                </section>
              )}
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="sticky top-6 space-y-6">
                {/* Quick Apply Card */}
                <div className="bg-[#636363] text-white rounded-xl p-6">
                  <h4
                    className="text-2xl font-bold mb-4"
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                  >
                    Ready to Apply?
                  </h4>
                  <p className="text-white/80 mb-6">
                    Get a personalized quote in minutes. Our expert loan officers are ready to help.
                  </p>
                  <Link
                    href="/quote"
                    className="block w-full text-center py-3 bg-[#1daed4] text-white font-bold rounded-lg hover:bg-[#17a0c4] transition-colors"
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                  >
                    Get Your Quote
                  </Link>
                </div>

                {/* Property Types */}
                {program.property_types && program.property_types.length > 0 && (
                  <div className="bg-gray-50 border-2 border-gray-200 rounded-xl p-6">
                    <h4
                      className="text-xl font-bold text-[#636363] mb-4"
                      style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                      Eligible Property Types
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {program.property_types.map((type) => (
                        <span
                          key={type}
                          className="px-3 py-1 bg-[#1daed4]/10 text-[#1daed4] text-sm font-semibold rounded-full"
                        >
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Contact Info */}
                <div className="bg-gray-50 border-2 border-gray-200 rounded-xl p-6">
                  <h4
                    className="text-xl font-bold text-[#636363] mb-4"
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                  >
                    Need Help?
                  </h4>
                  <p className="text-[#636363] mb-4">
                    Our loan experts are available to answer your questions.
                  </p>
                  <a
                    href="tel:1-800-555-0123"
                    className="block w-full text-center py-3 bg-white border-2 border-[#1daed4] text-[#1daed4] font-bold rounded-lg hover:bg-[#1daed4] hover:text-white transition-colors"
                    style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                  >
                    Call Us Today
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-[#1daed4] py-12 px-6 mt-12">
          <div className="max-w-4xl mx-auto text-center text-white">
            <h3
              className="text-4xl font-bold mb-4"
              style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
            >
              Start Your {program.title} Application
            </h3>
            <p className="text-lg mb-8 text-white/90">
              Get pre-qualified in minutes with our easy online application process.
            </p>
            <Link
              href="/quote"
              className="inline-block bg-white text-[#636363] px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors shadow-lg"
              style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
            >
              Get Started Now
            </Link>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-[#636363] text-white py-8 px-6">
          <div className="max-w-7xl mx-auto text-center">
            <p className="text-sm">
              © {new Date().getFullYear()} Custom Mortgage Inc. | Nationwide Lender | FinTech
              Financing Solutions
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
