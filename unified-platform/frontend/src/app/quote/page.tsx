'use client';
import { useState } from 'react';

export default function QuotePage() {
  const [formData, setFormData] = useState({
    property_state: 'CA',
    loan_amount: 500000,
    credit_score: 740,
    property_value: 650000
  });
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:8001/api/v1/quote/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      setError('Unable to connect. Please ensure the backend is running.');
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header Section */}
      <div className="bg-[#636363] text-white py-4 px-6">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <h1 className="text-3xl font-bold tracking-wide" style={{fontFamily: 'Bebas Neue, Arial, sans-serif'}}>
            CUSTOM MORTGAGE
          </h1>
          <span className="text-sm tracking-widest" style={{fontFamily: 'Bebas Neue, Arial, sans-serif'}}>
            NATIONWIDE LENDER
          </span>
        </div>
      </div>

      {/* Hero Section */}
      <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
        <div className="max-w-6xl mx-auto text-center">
          <h2 className="text-5xl font-bold text-[#636363] mb-4" style={{fontFamily: 'Bebas Neue, Arial, sans-serif'}}>
            Get Your Custom Quote
          </h2>
          <p className="text-lg text-[#636363] max-w-2xl mx-auto">
            FinTech Financing Solutions Tailored for Your Unique Needs
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto py-12 px-6">
        <div className="grid md:grid-cols-2 gap-8">

          {/* Quote Form Card */}
          <div className="bg-white border-2 border-[#a5a5a5] rounded-lg shadow-lg p-8">
            <h3 className="text-3xl font-bold text-[#636363] mb-6" style={{fontFamily: 'Bebas Neue, Arial, sans-serif'}}>
              Loan Details
            </h3>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-[#636363] mb-2">
                  Property State
                </label>
                <input
                  type="text"
                  value={formData.property_state}
                  onChange={(e) => setFormData({...formData, property_state: e.target.value})}
                  className="w-full p-3 border-2 border-[#a5a5a5] rounded focus:border-[#1daed4] focus:outline-none"
                  placeholder="CA"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#636363] mb-2">
                  Loan Amount
                </label>
                <input
                  type="number"
                  value={formData.loan_amount}
                  onChange={(e) => setFormData({...formData, loan_amount: Number(e.target.value)})}
                  className="w-full p-3 border-2 border-[#a5a5a5] rounded focus:border-[#1daed4] focus:outline-none"
                  placeholder="$500,000"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#636363] mb-2">
                  Credit Score (FICO)
                </label>
                <input
                  type="number"
                  value={formData.credit_score}
                  onChange={(e) => setFormData({...formData, credit_score: Number(e.target.value)})}
                  className="w-full p-3 border-2 border-[#a5a5a5] rounded focus:border-[#1daed4] focus:outline-none"
                  placeholder="740"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-[#636363] mb-2">
                  Property Value
                </label>
                <input
                  type="number"
                  value={formData.property_value}
                  onChange={(e) => setFormData({...formData, property_value: Number(e.target.value)})}
                  className="w-full p-3 border-2 border-[#a5a5a5] rounded focus:border-[#1daed4] focus:outline-none"
                  placeholder="$650,000"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-[#1daed4] hover:bg-[#17a0c4] disabled:bg-[#a5a5a5] text-white font-bold rounded-lg transition-colors text-lg"
                style={{fontFamily: 'Bebas Neue, Arial, sans-serif'}}
              >
                {loading ? 'Getting Your Quote...' : 'Get My Quote'}
              </button>
            </form>

            {error && (
              <div className="mt-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
                {error}
              </div>
            )}
          </div>

          {/* Trust Signals / Info Card */}
          <div>
            <div className="bg-[#1daed4] text-white p-8 rounded-lg shadow-lg mb-6">
              <h3 className="text-3xl font-bold mb-4" style={{fontFamily: 'Bebas Neue, Arial, sans-serif'}}>
                Why Custom Mortgage?
              </h3>
              <ul className="space-y-3">
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Expert, Client-Focused Team</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>FinTech Solutions for Unique Needs</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Nationwide Coverage</span>
                </li>
                <li className="flex items-start">
                  <span className="mr-2">✓</span>
                  <span>Stated Income & Non-QM Options</span>
                </li>
              </ul>
            </div>

            {/* Results Display */}
            {results && (
              <div className="bg-white border-2 border-[#1daed4] rounded-lg shadow-lg p-8">
                <h3 className="text-3xl font-bold text-[#636363] mb-6" style={{fontFamily: 'Bebas Neue, Arial, sans-serif'}}>
                  Your Quote Results
                </h3>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-gray-50 p-4 rounded border border-[#a5a5a5]">
                    <p className="text-sm text-[#636363] mb-1">Loan-to-Value</p>
                    <p className="text-2xl font-bold text-[#1daed4]">{results.ltv?.toFixed(2)}%</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded border border-[#a5a5a5]">
                    <p className="text-sm text-[#636363] mb-1">Programs Found</p>
                    <p className="text-2xl font-bold text-[#1daed4]">{results.matches_found}</p>
                  </div>
                </div>

                {results.quotes && results.quotes.length > 0 ? (
                  <div className="space-y-4">
                    <p className="font-semibold text-[#636363]">Available Programs:</p>
                    {results.quotes.map((quote: any, i: number) => (
                      <div key={i} className="border-2 border-[#a5a5a5] rounded-lg p-4 hover:border-[#1daed4] transition-colors">
                        <p className="font-bold text-[#636363]">{quote.lender} - {quote.program}</p>
                        <div className="mt-2 text-sm text-[#636363]">
                          <span className="mr-4">Rate: {quote.base_rate}%</span>
                          <span>Points: {quote.points}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-6 text-[#636363]">
                    <p className="mb-4">No exact matches found for your criteria.</p>
                    <p className="text-sm">Contact us for custom solutions tailored to your unique needs.</p>
                    <button className="mt-4 px-6 py-2 bg-[#1daed4] text-white rounded hover:bg-[#17a0c4]">
                      Speak with an Expert
                    </button>
                  </div>
                )}
              </div>
            )}
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
