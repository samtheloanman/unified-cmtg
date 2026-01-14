
import Image from "next/image";
import Link from "next/link";
import { Metadata } from 'next';

// Data interface based on Wagtail model
interface HomePageData {
  id: number;
  title: string;
  hero_title: string;
  hero_subtitle: string;
  hero_cta_text: string;
  hero_cta_url: string;
}

// Internal API URL for server-side fetching
const API_URL = process.env.INTERNAL_API_URL || 'http://backend:8000';

async function getHomePage(): Promise<HomePageData | null> {
  try {
    // Fetch the home page by type
    const url = `${API_URL}/api/v2/pages/?type=cms.HomePage&fields=*&limit=1`;
    console.log(`Fetching Home Page: ${url}`);

    const response = await fetch(url, {
      cache: 'no-store',
      headers: { 'Accept': 'application/json' }
    });

    if (!response.ok) {
      console.error(`API returned ${response.status} for Home Page`);
      return null;
    }

    const data = await response.json();
    if (data.items && data.items.length > 0) {
      return data.items[0];
    }
    return null;
  } catch (error) {
    console.error('Error fetching Home Page:', error);
    return null;
  }
}

export default async function Home() {
  const page = await getHomePage();

  // Fallback content if API fails or content not populated
  const content = {
    title: page?.hero_title || "CUSTOM MORTGAGE",
    subtitle: page?.hero_subtitle?.replace(/<[^>]*>/g, '') || "Nationwide Lender | FinTech Financing Solutions",
    ctaText: page?.hero_cta_text || "Get Your Quote",
    ctaUrl: page?.hero_cta_url || "/quote"
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-[#636363] text-white py-4 px-6 md:px-12">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-3xl font-bold tracking-wide" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
            CUSTOM MORTGAGE
          </h1>
          <span className="text-sm tracking-widest hidden sm:block" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
            NATIONWIDE LENDER
          </span>
          <Link href="/quote" className="sm:hidden text-sm underline">
            Get Quote
          </Link>
        </div>
      </div>

      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-gray-50 to-white overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="relative z-10 pb-8 bg-transparent sm:pb-16 md:pb-20 lg:max-w-2xl lg:w-full lg:pb-28 xl:pb-32">
            <main className="mt-10 mx-auto max-w-7xl px-4 sm:mt-12 sm:px-6 md:mt-16 lg:mt-20 lg:px-8 xl:mt-28">
              <div className="sm:text-center lg:text-left">
                <h1 className="text-4xl tracking-tight font-extrabold text-[#636363] sm:text-5xl md:text-6xl" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                  <span className="block xl:inline">{content.title}</span>
                </h1>
                <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-lg sm:max-w-xl sm:mx-auto md:mt-5 md:text-xl lg:mx-0">
                  {content.subtitle}
                </p>
                <div className="mt-5 sm:mt-8 sm:flex sm:justify-center lg:justify-start">
                  <div className="rounded-md shadow">
                    <Link href={content.ctaUrl}
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-[#1daed4] hover:bg-[#17a0c4] md:py-4 md:text-lg md:px-10 transition-colors"
                      style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                      {content.ctaText}
                    </Link>
                  </div>
                  <div className="mt-3 sm:mt-0 sm:ml-3">
                    <Link href="/programs"
                      className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-[#1daed4] bg-[#1daed4]/10 hover:bg-[#1daed4]/20 md:py-4 md:text-lg md:px-10 transition-colors"
                      style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                      View Programs
                    </Link>
                  </div>
                </div>
              </div>
            </main>
          </div>
        </div>
        {/* Decorative blob */}
        <div className="lg:absolute lg:inset-y-0 lg:right-0 lg:w-1/2 bg-[#1daed4]/5 flex items-center justify-center">
          <svg className="h-56 w-56 text-[#1daed4]/20 transform scale-150" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2L2 7l10 5 10-5-10-5zm0 9l2.5-1.25L12 8.75l-2.5 1.25L12 11zm0 2.5l-5-2.5-5 2.5L12 22l10-8.5-5-2.5-5 2.5z" />
          </svg>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-12 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:text-center">
            <h2 className="text-base text-[#1daed4] font-semibold tracking-wide uppercase">FinTech Advantage</h2>
            <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-[#636363] sm:text-4xl" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
              A Better Way to Borrow
            </p>
            <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
              We combine cutting-edge technology with personalized service to deliver the perfect loan for your unique situation.
            </p>
          </div>

          <div className="mt-10">
            <dl className="space-y-10 md:space-y-0 md:grid md:grid-cols-3 md:gap-x-8 md:gap-y-10">
              <div className="relative">
                <dt>
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-[#1daed4] text-white">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-[#636363]" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif', letterSpacing: '0.05em' }}>Fast Approvals</p>
                </dt>
                <dd className="mt-2 ml-16 text-base text-gray-500">
                  Our automated underwriting engine provides instant feedback and quicker clear-to-close times.
                </dd>
              </div>

              <div className="relative">
                <dt>
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-[#1daed4] text-white">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-[#636363]" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif', letterSpacing: '0.05em' }}>Custom Programs</p>
                </dt>
                <dd className="mt-2 ml-16 text-base text-gray-500">
                  From DSCR to Bank Statement loans, we have programs that fit complex borrower profiles.
                </dd>
              </div>

              <div className="relative">
                <dt>
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-[#1daed4] text-white">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-[#636363]" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif', letterSpacing: '0.05em' }}>Nationwide Reach</p>
                </dt>
                <dd className="mt-2 ml-16 text-base text-gray-500">
                  We lend in 48 states, offering consistent service wherever your next investment takes you.
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-[#636363] text-white py-8 px-6 mt-auto">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-sm">
            © 2026 Custom Mortgage Inc. | Nationwide Lender | FinTech Financing Solutions
          </p>
        </div>
      </div>
    </div>
  );
}

export const metadata: Metadata = {
  title: 'Custom Mortgage Inc | Nationwide Lender',
  description: 'Custom Mortgage Inc offers unique financing solutions for residential and commercial properties nationwide.',
}
