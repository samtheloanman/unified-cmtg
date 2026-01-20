import Link from "next/link";
import { Metadata } from 'next';
import { getFundedLoanPages, getProgramPages, getHomePage, FundedLoanPage, CMSProgramPage, HomePage } from '@/lib/wagtail-api';

// Program type cards matching production site
const programTypes = [
  { name: "Stated Income", description: "No tax return verification needed for self-employed", href: "/programs/stated-income-loans", icon: "📄" },
  { name: "Hard Money", description: "Fast closing with equity-based lending decisions", href: "/programs/hard-money-mortgage-loans", icon: "💰" },
  { name: "Reverse Mortgage", description: "Access home equity with no monthly payments", href: "/programs/reverse-mortgages-loan-programs", icon: "🏠" },
  { name: "Construction", description: "Ground-up and renovation financing", href: "/programs/construction-loans-2", icon: "🏗️" },
  { name: "Vacant Land", description: "Raw land and lot financing solutions", href: "/programs/land-loans", icon: "🌲" },
  { name: "Commercial", description: "Office, retail, and multi-family loans", href: "/programs/commercial-mortgage-loans", icon: "🏢" },
  { name: "Fix and Flip", description: "Short-term rehab and investment loans", href: "/programs/fix-flip-rehab-loan-rehab-mortgage-loans", icon: "🔨" },
  { name: "Super Jumbo", description: "High-value residential mortgages", href: "/programs/super-jumbo-residential-mortgage-loans", icon: "💎" },
];

export default async function Home() {
  // Parallel Data Fetching with error handling
  let fundedLoans: FundedLoanPage[] = [];
  let programs: CMSProgramPage[] = [];
  let homePage: HomePage | null = null;

  try {
    [fundedLoans, programs, homePage] = await Promise.all([
      getFundedLoanPages(),
      getProgramPages(),
      getHomePage()
    ]);
  } catch (error) {
    console.error('Failed to fetch home page data:', error);
    // Continue with empty data - page will still render with fallback content
  }

  return (
    <div className="bg-white">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-[#1daed4] to-[#17a0c4] text-white py-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-4 font-heading">
            {homePage?.hero_title || "Custom Mortgage – Nationwide Lender"}
          </h1>

          <div className="text-xl md:text-2xl mb-8 opacity-90 prose prose-invert max-w-none text-white [&>p]:text-white"
            dangerouslySetInnerHTML={{ __html: homePage?.hero_subtitle || "<p>FinTech Financing Solutions Tailored for Your Unique Needs</p>" }} />

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href={homePage?.hero_cta_url || "/quote"}
              className="inline-block bg-white text-[#1daed4] px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors shadow-lg font-heading">
              {homePage?.hero_cta_text || "Get Your Quote"}
            </Link>
            <a href="https://custommortgage.floify.com/" target="_blank" rel="noopener noreferrer"
              className="inline-block border-2 border-white text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-white/10 transition-colors font-heading">
              Start Application
            </a>
          </div>
        </div>
      </section>

      {/* Program Type Cards */}
      <section className="py-16 px-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center text-[#636363] mb-12">
            Loan Programs
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {programTypes.map((program) => (
              <Link key={program.name} href={program.href}
                className="bg-white rounded-xl p-6 shadow-md hover:shadow-xl transition-shadow border border-gray-100 text-center group">
                <div className="text-4xl mb-3">{program.icon}</div>
                <h3 className="text-lg font-bold text-[#636363] group-hover:text-[#1daed4] transition-colors">
                  {program.name}
                </h3>
                <p className="text-sm text-gray-500 mt-2">{program.description}</p>
              </Link>
            ))}
          </div>
          <div className="text-center mt-8">
            <Link href="/programs" className="text-[#1daed4] font-bold hover:underline">
              View All Programs →
            </Link>
          </div>
        </div>
      </section>

      {/* CMS Programs (if available) */}
      {programs.length > 0 && (
        <section className="py-16 px-6 bg-white">
          <div className="max-w-7xl mx-auto">
            <h2 className="text-3xl md:text-4xl font-bold text-center text-[#636363] mb-8">
              Featured Loan Programs
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {programs.map((program) => (
                <Link key={program.id} href={`/programs/${program.meta.slug}`}
                  className="block bg-gray-50 rounded-lg p-6 hover:bg-[#1daed4]/10 transition-colors border border-gray-200">
                  <h3 className="text-lg font-bold text-[#636363]">
                    {program.title}
                  </h3>
                  <span className="text-[#1daed4] text-sm mt-2 inline-block">Learn More →</span>
                </Link>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Recently Funded Section */}
      <section className="py-16 px-6 bg-[#636363] text-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            Recently Funded
          </h2>
          {fundedLoans.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {fundedLoans.map((loan) => (
                <Link key={loan.id} href={`/funded-loans/${loan.meta.slug}`}
                  className="block bg-white/10 rounded-lg p-4 hover:bg-white/20 transition-colors">
                  <h3 className="text-sm font-medium line-clamp-2">{loan.title}</h3>
                  <span className="text-[#1daed4] text-xs mt-2 inline-block">View Details →</span>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-center opacity-75">Loading funded loans...</p>
          )}
          <div className="text-center mt-8">
            <Link href="/funded-loans" className="inline-block border-2 border-white text-white px-6 py-3 rounded-lg font-bold hover:bg-white/10 transition-colors">
              View All Funded Loans
            </Link>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-16 px-6 bg-white">
        <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h2 className="text-3xl md:text-4xl font-bold text-[#636363] mb-6">
              A FinTech Real Estate and Finance Agency
            </h2>
            <p className="text-gray-600 mb-4">
              We combine industry expertise with a FinTech approach to meet all your real estate and financial needs.
              Whether you&apos;re looking to secure the perfect mortgage, invest in a new property, or refinance an existing loan,
              our team of professionals is here to guide you every step of the way.
            </p>
            <a href="tel:8779765669" className="inline-block bg-[#1daed4] text-white px-6 py-3 rounded-lg font-bold hover:bg-[#17a0c4] transition-colors">
              Call Us (877) 976-5669
            </a>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 p-6 rounded-lg text-center">
              <div className="text-4xl font-bold text-[#1daed4]">48</div>
              <div className="text-gray-600">States</div>
            </div>
            <div className="bg-gray-50 p-6 rounded-lg text-center">
              <div className="text-4xl font-bold text-[#1daed4]">100+</div>
              <div className="text-gray-600">Loan Programs</div>
            </div>
            <div className="bg-gray-50 p-6 rounded-lg text-center">
              <div className="text-4xl font-bold text-[#1daed4]">Fast</div>
              <div className="text-gray-600">Approvals</div>
            </div>
            <div className="bg-gray-50 p-6 rounded-lg text-center">
              <div className="text-4xl font-bold text-[#1daed4]">24/7</div>
              <div className="text-gray-600">Support</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-6 bg-[#1daed4] text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold mb-4 font-heading">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Get a personalized mortgage quote in minutes. Our expert team is ready to help you find the perfect financing solution.
          </p>
          <Link href="/quote"
            className="inline-block bg-white text-[#1daed4] px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors shadow-lg font-heading">
            Get Your Quote Now
          </Link>
        </div>
      </section>
    </div>
  );
}

export const metadata: Metadata = {
  title: 'Custom Mortgage - Nationwide Lender | FinTech Financing Solutions',
  description: 'Nationwide Mortgage Lender for Commercial and Residential properties - Bridge Hard money loans, and Stated Income available. Call (877) 976-5669',
};
