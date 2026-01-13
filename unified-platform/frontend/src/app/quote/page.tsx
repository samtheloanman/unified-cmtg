'use client';

import { useState } from 'react';
import { API_BASE } from '@/lib/api';

interface QuoteRequest {
  loan_amount: number;
  ltv: number;
  fico_score: number;
  property_type: string;
  purpose: string;
}

interface QuoteResult {
  interest_rate: number;
  points: number;
  apr: number;
  monthly_payment: number;
}

export default function QuotePage() {
  const [formData, setFormData] = useState<QuoteRequest>({
    loan_amount: 500000,
    ltv: 80,
    fico_score: 720,
    property_type: 'Single Family',
    purpose: 'Purchase',
  });

  const [result, setResult] = useState<QuoteResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE}/api/v1/quote/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          ltv: formData.ltv / 100, // Convert percentage to decimal
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch quote');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'property_type' || name === 'purpose' ? value : Number(value),
    }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-card rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-center mb-8 text-primary">Mortgage Quote Calculator</h1>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">Loan Amount ($)</label>
              <input
                type="number"
                name="loan_amount"
                value={formData.loan_amount}
                onChange={handleChange}
                className="w-full p-3 rounded bg-input border border-gray-700 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">LTV (%)</label>
              <input
                type="number"
                name="ltv"
                value={formData.ltv}
                onChange={handleChange}
                min="0"
                max="100"
                className="w-full p-3 rounded bg-input border border-gray-700 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">FICO Score</label>
              <input
                type="number"
                name="fico_score"
                value={formData.fico_score}
                onChange={handleChange}
                min="300"
                max="850"
                className="w-full p-3 rounded bg-input border border-gray-700 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Property Type</label>
              <select
                name="property_type"
                value={formData.property_type}
                onChange={handleChange}
                className="w-full p-3 rounded bg-input border border-gray-700 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition"
              >
                <option value="Single Family">Single Family</option>
                <option value="Condo">Condo</option>
                <option value="Multi-Family">Multi-Family</option>
                <option value="Townhouse">Townhouse</option>
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium mb-2">Loan Purpose</label>
              <select
                name="purpose"
                value={formData.purpose}
                onChange={handleChange}
                className="w-full p-3 rounded bg-input border border-gray-700 focus:border-accent focus:ring-1 focus:ring-accent outline-none transition"
              >
                <option value="Purchase">Purchase</option>
                <option value="Refinance">Refinance</option>
                <option value="Cash-Out">Cash-Out</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-accent text-primary font-bold text-lg rounded hover:opacity-90 transition disabled:opacity-50"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Calculating...
              </span>
            ) : (
              'Calculate Quote'
            )}
          </button>
        </form>

        {error && (
          <div className="mt-6 p-4 bg-red-900/50 border border-red-500 rounded text-red-200 text-center">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-8 p-6 bg-primary/20 rounded border border-accent/30 animate-in fade-in slide-in-from-bottom-4">
            <h2 className="text-xl font-bold text-accent mb-4 border-b border-accent/20 pb-2">Quote Results</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-400">Interest Rate</p>
                <p className="text-2xl font-bold">{result.interest_rate}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">APR</p>
                <p className="text-2xl font-bold">{result.apr}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Points/Credits</p>
                <p className="text-xl">{result.points}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Est. Monthly Payment</p>
                <p className="text-xl">${result.monthly_payment.toLocaleString()}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
