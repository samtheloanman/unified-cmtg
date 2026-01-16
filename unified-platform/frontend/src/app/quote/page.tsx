'use client';

import QuoteWizard from '../../components/QuoteWizard';

export default function QuotePage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header Section */}
      <div className="bg-[#636363] text-white py-4 px-6">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <h1 className="text-3xl font-bold tracking-wide" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
            CUSTOM MORTGAGE
          </h1>
          <span className="text-sm tracking-widest" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
            NATIONWIDE LENDER
          </span>
        </div>
      </div>

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-5xl font-bold text-[#636363] mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
            Get Your Custom Quote
          </h2>
          <p className="text-lg text-[#636363] max-w-2xl mx-auto">
            FinTech Financing Solutions Tailored for Your Unique Needs
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto py-12 px-6">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Quote Wizard - Takes 2 columns on large screens */}
          <div className="lg:col-span-2">
            <QuoteWizard />
          </div>

          {/* Trust Signals Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-[#1daed4] text-white p-8 rounded-lg shadow-lg sticky top-6">
              <h3 className="text-3xl font-bold mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                Why Custom Mortgage?
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <span className="mr-2 text-xl">✓</span>
                  <span>Expert, Client-Focused Team</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-xl">✓</span>
                  <span>FinTech Solutions for Unique Needs</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-xl">✓</span>
                  <span>Nationwide Coverage</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-xl">✓</span>
                  <span>Stated Income & Non-QM Options</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2 text-xl">✓</span>
                  <span>Fast Pre-Approvals</span>
                </li>
              </ul>
              
              <div className="mt-8 pt-6 border-t border-white/30">
                <p className="text-white/80 text-sm mb-2">Need help?</p>
                <p className="text-xl font-bold" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                  1-800-CUSTOM-M
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-[#636363] text-white py-8 px-6 mt-12">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-sm">
            © 2026 Custom Mortgage Inc. | Nationwide Lender | FinTech Financing Solutions
          </p>
        </div>
      </div>
    </div>
  );
}
