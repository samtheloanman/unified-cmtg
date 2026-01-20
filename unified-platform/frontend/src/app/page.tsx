import Link from "next/link";
import { getFundedLoanPages, getProgramPages, getHomePage, FundedLoanPage, CMSProgramPage, HomePage } from '@/lib/wagtail-api';
import TerritorySection from '@/components/home/TerritorySection';
import ProgramStateGrid from '@/components/home/ProgramStateGrid';
import { ScrollReveal } from '@/components/ui/ScrollReveal';
import { Metadata } from 'next';

// Program type cards matching production site - Updated Icons & Text
const programTypes = [
  { name: "Stated Income", description: "No tax return verification needed", href: "/programs/stated-income-loans", icon: "📄" },
  { name: "Hard Money", description: "Equity-based lending decisions", href: "/programs/hard-money-mortgage-loans", icon: "💰" },
  { name: "Reverse Mortgage", description: "No monthly payment options", href: "/programs/reverse-mortgages-loan-programs", icon: "🏠" },
  { name: "Construction", description: "Ground-up and renovation", href: "/programs/construction-loans-2", icon: "🏗️" },
  { name: "Vacant Land", description: "Raw land financing solutions", href: "/programs/land-loans", icon: "🌲" },
  { name: "Commercial", description: "Office, retail, multi-family", href: "/programs/commercial-mortgage-loans", icon: "🏢" },
  { name: "Fix and Flip", description: "Short-term rehab loans", href: "/programs/fix-flip-rehab-loan-rehab-mortgage-loans", icon: "🔨" },
  { name: "Super Jumbo", description: "High-value residential", href: "/programs/super-jumbo-residential-mortgage-loans", icon: "💎" },
];

export const metadata: Metadata = {
  title: 'Custom Mortgage - Nationwide Lender | FinTech Financing Solutions',
  description: 'Nationwide Mortgage Lender for Commercial and Residential properties - Bridge Hard money loans, and Stated Income available. Call (877) 976-5669',
};

export default async function Home() {
  // Parallel Data Fetching
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
  }

  return (
    <div className="bg-white overflow-hidden">
      {/* Hero Section - Sharp FinTech Look */}
      <section className="relative bg-[#0f2933] text-white py-24 px-6 border-b-4 border-[#1daed4]">
        <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <ScrollReveal animation="slide-in-right">
            <div className="text-left">
              <h1 className="text-5xl md:text-7xl font-black mb-6 font-heading leading-none tracking-tighter uppercase" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                {homePage?.hero_title || "Custom Mortgage"}
                <span className="block text-[#1daed4]">Nationwide Lender</span>
              </h1>

              <div className="text-xl md:text-2xl mb-10 text-gray-300 font-light max-w-lg leading-relaxed"
                dangerouslySetInnerHTML={{ __html: homePage?.hero_subtitle || "<p>FinTech Financing Solutions Tailored for Your Unique Needs</p>" }} />

              <div className="flex flex-col sm:flex-row gap-4">
                <Link href={homePage?.hero_cta_url || "/quote"}
                  className="inline-block bg-[#1daed4] text-white px-10 py-4 font-bold text-lg hover:bg-white hover:text-[#0f2933] transition-all uppercase tracking-widest shadow-[4px_4px_0px_0px_rgba(255,255,255,0.2)] hover:shadow-none hover:translate-x-[2px] hover:translate-y-[2px]"
                  style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                  {homePage?.hero_cta_text || "Get Your Quote"}
                </Link>
                <a href="https://custommortgage.floify.com/" target="_blank" rel="noopener noreferrer"
                  className="inline-block border-2 border-white text-white px-10 py-4 font-bold text-lg hover:bg-white hover:text-[#0f2933] transition-all uppercase tracking-widest"
                  style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                  Start Application
                </a>
              </div>
            </div>
          </ScrollReveal>

          {/* Abstract Technical Visual */}
          <ScrollReveal delay={200} animation="fade-in">
            <div className="hidden md:block relative h-full min-h-[400px] border-l border-white/10 pl-12 scale-90 opacity-80">
              <div className="absolute top-0 right-0 w-64 h-64 bg-[#1daed4] opacity-10 rounded-full blur-3xl"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/5 p-6 border border-white/10 backdrop-blur-sm">
                  <span className="text-[#1daed4] text-4xl block mb-2 font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>48</span>
                  <span className="text-xs uppercase tracking-widest">States Covered</span>
                </div>
                <div className="bg-white/5 p-6 border border-white/10 backdrop-blur-sm mt-8">
                  <span className="text-[#1daed4] text-4xl block mb-2 font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>$500M+</span>
                  <span className="text-xs uppercase tracking-widest">Funded Loans</span>
                </div>
                <div className="bg-white/5 p-6 border border-white/10 backdrop-blur-sm -mt-8">
                  <span className="text-[#1daed4] text-4xl block mb-2 font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>7 Days</span>
                  <span className="text-xs uppercase tracking-widest">Fast Closing</span>
                </div>
                <div className="bg-white/5 p-6 border border-white/10 backdrop-blur-sm">
                  <span className="text-[#1daed4] text-4xl block mb-2 font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>100+</span>
                  <span className="text-xs uppercase tracking-widest">Programs</span>
                </div>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Program Type Cards - "Technical Grid" Style */}
      <section className="py-24 px-6 bg-white relative z-10 -mt-12">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-0 border border-gray-200 shadow-xl bg-white">
            {programTypes.map((program, idx) => (
              <ScrollReveal key={program.name} delay={idx * 50} width="100%">
                <Link href={program.href}
                  className="block group p-8 border hover:z-20 border-gray-100 hover:border-[#1daed4] hover:bg-white transition-all hover:shadow-[0_0_40px_-10px_rgba(29,174,212,0.15)] h-full relative"
                >
                  <div className="text-4xl mb-4 group-hover:scale-110 transition-transform duration-300">{program.icon}</div>
                  <h3 className="text-xl font-bold text-[#0f2933] group-hover:text-[#1daed4] transition-colors uppercase font-heading mb-2 leading-none" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                    {program.name}
                  </h3>
                  <p className="text-sm text-gray-400 group-hover:text-gray-600 transition-colors leading-tight">{program.description}</p>
                  <div className="absolute top-4 right-4 text-[#1daed4] opacity-0 group-hover:opacity-100 transition-opacity">↗</div>
                </Link>
              </ScrollReveal>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link href="/programs" className="inline-block border-b-2 border-[#1daed4] text-[#0f2933] font-bold text-sm tracking-widest hover:text-[#1daed4] transition-colors uppercase pb-1">
              View All Loan Programs
            </Link>
          </div>
        </div>
      </section>

      {/* NEW: Territory Section */}
      <TerritorySection />

      {/* NEW: Programs by State Matrix */}
      <ProgramStateGrid />

      {/* CMS Programs (Featured) - Horizontal Scroll or Grid */}
      {programs.length > 0 && (
        <section className="py-20 px-6 bg-[#f8f9fa] border-b border-gray-200">
          <div className="max-w-7xl mx-auto">
            <ScrollReveal>
              <div className="flex justify-between items-end mb-12">
                <h2 className="text-4xl md:text-5xl font-black text-[#0f2933] uppercase tracking-tighter" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                  Featured
                </h2>
                <Link href="/programs" className="hidden md:block text-[#1daed4] font-bold tracking-widest text-xs uppercase hover:underline">
                  See All Programs →
                </Link>
              </div>
            </ScrollReveal>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {programs.slice(0, 3).map((program, idx) => (
                <ScrollReveal key={program.id} delay={idx * 100}>
                  <Link href={`/programs/${program.meta.slug}`}
                    className="block bg-white p-8 border-l-4 border-[#1daed4] shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all group">
                    <span className="text-xs font-bold text-[#1daed4] uppercase tracking-widest mb-3 block">Loan Program</span>
                    <h3 className="text-2xl font-bold text-[#0f2933] mb-4 group-hover:text-[#1daed4] transition-colors font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                      {program.title}
                    </h3>
                    <div className="flex items-center text-sm font-bold text-gray-400 group-hover:text-[#0f2933] transition-colors">
                      <span>Read Details</span>
                      <span className="ml-2 bg-gray-100 text-gray-500 rounded px-2 py-0 text-[10px] group-hover:bg-[#1daed4] group-hover:text-white transition-colors">➜</span>
                    </div>
                  </Link>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Recently Funded Section - Dark Mode */}
      <section className="py-24 px-6 bg-[#0a1f26] text-white">
        <div className="max-w-7xl mx-auto">
          <ScrollReveal>
            <h2 className="text-4xl md:text-5xl font-black text-center mb-16 text-white uppercase tracking-tighter" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
              Recently Funded Deals
            </h2>
          </ScrollReveal>

          {fundedLoans.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {fundedLoans.map((loan, idx) => (
                <ScrollReveal key={loan.id} delay={idx * 50}>
                  <Link href={`/funded-loans/${loan.meta.slug}`}
                    className="block bg-white/5 border border-white/10 p-6 hover:bg-[#1daed4] hover:border-[#1daed4] transition-all group relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-16 h-16 bg-white/10 rounded-full -mr-8 -mt-8 group-hover:scale-150 transition-transform duration-500"></div>

                    <div className="relative z-10">
                      <span className="text-[10px] uppercase tracking-widest text-[#1daed4] group-hover:text-white mb-2 block">Closed Deal</span>
                      <h3 className="text-lg font-bold leading-tight mb-4 line-clamp-2 h-12 font-heading tracking-wide">
                        {loan.title}
                      </h3>
                      <span className="text-xs font-bold border-b border-white/20 pb-1 group-hover:border-white">View Case Study</span>
                    </div>
                  </Link>
                </ScrollReveal>
              ))}
            </div>
          ) : (
            <p className="text-center opacity-50 font-mono text-sm">LOADING FUNDED LOANS DATABASE...</p>
          )}

          <div className="text-center mt-16">
            <Link href="/funded-loans" className="inline-block border border-white/20 text-white px-8 py-3 font-bold uppercase tracking-widest text-sm hover:bg-white hover:text-[#0f2933] transition-all">
              View All Transactions
            </Link>
          </div>
        </div>
      </section>

      {/* About Section - Split Layout */}
      <section className="py-24 px-6 bg-white overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-16 items-center">
            <ScrollReveal>
              <div>
                <span className="text-[#1daed4] font-bold tracking-widest uppercase text-sm mb-4 block">About Us</span>
                <h2 className="text-5xl md:text-6xl font-black text-[#0f2933] mb-8 uppercase tracking-tighter leading-none" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
                  FinTech Speed.<br />Bank Stability.
                </h2>
                <p className="text-gray-600 mb-6 text-lg leading-relaxed font-light">
                  We combine industry expertise with a FinTech approach to meet all your real estate and financial needs.
                  Whether you&apos;re looking to secure the perfect mortgage, invest in a new property, or refinance an existing loan,
                  our team of professionals is here to guide you every step of the way.
                </p>
                <a href="tel:8779765669" className="inline-flex items-center gap-4 text-[#0f2933] font-bold text-xl group hover:text-[#1daed4] transition-colors">
                  <span className="w-12 h-12 rounded-full border-2 border-[#1daed4] flex items-center justify-center text-[#1daed4] group-hover:bg-[#1daed4] group-hover:text-white transition-all">📞</span>
                  (877) 976-5669
                </a>
              </div>
            </ScrollReveal>

            <ScrollReveal delay={200} animation="fade-in">
              <div className="grid grid-cols-2 gap-4">
                {[
                  { val: "48", label: "States Authorized" },
                  { val: "100+", label: "Loan Programs" },
                  { val: "7", label: "Days to Close" },
                  { val: "24/7", label: "Support Team" }
                ].map((stat, i) => (
                  <div key={i} className="bg-gray-50 border border-gray-100 p-8 text-center hover:border-[#1daed4] transition-colors">
                    <div className="text-5xl font-bold text-[#1daed4] mb-2 font-heading" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>{stat.val}</div>
                    <div className="text-gray-400 text-xs font-bold uppercase tracking-widest">{stat.label}</div>
                  </div>
                ))}
              </div>
            </ScrollReveal>
          </div>
        </div>
      </section>

      {/* CTA Section - Minimal & Strong */}
      <section className="py-24 px-6 bg-[#1daed4] text-white">
        <div className="max-w-4xl mx-auto text-center">
          <ScrollReveal animation="scale-up">
            <h2 className="text-5xl md:text-7xl font-black mb-6 uppercase tracking-tighter leading-none" style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
              Ready to Execute?
            </h2>
            <p className="text-xl mb-10 opacity-90 font-light max-w-2xl mx-auto">
              Get a personalized mortgage quote in minutes. Our expert team is standing by.
            </p>
            <Link href="/quote"
              className="inline-block bg-white text-[#1daed4] px-12 py-5 font-black text-xl hover:bg-[#0f2933] hover:text-white transition-all transform hover:-translate-y-1 shadow-[8px_8px_0px_0px_rgba(0,0,0,0.1)] uppercase tracking-widest"
              style={{ fontFamily: 'Bebas Neue, sans-serif' }}>
              Get Your Quote Now
            </Link>
          </ScrollReveal>
        </div>
      </section>
    </div>
  );
}
