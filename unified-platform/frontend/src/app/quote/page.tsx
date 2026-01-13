'use client';
import { useState } from 'react';

export default function QuotePage() {
  const [formData, setFormData] = useState({
    property_state: 'CA',
    loan_amount: 500000,
    credit_score: 740,
    property_value: 650000
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8001/api/v1/quote/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-8">Mortgage Quote Calculator</h1>

      <form onSubmit={handleSubmit} className="max-w-md space-y-4">
        <div>
          <label>State</label>
          <input
            type="text"
            value={formData.property_state}
            onChange={(e) => setFormData({...formData, property_state: e.target.value})}
            className="w-full p-2 bg-gray-800 rounded border border-gray-700 focus:border-blue-500 outline-none"
          />
        </div>
        <div>
          <label>Loan Amount</label>
          <input
            type="number"
            value={formData.loan_amount}
            onChange={(e) => setFormData({...formData, loan_amount: Number(e.target.value)})}
            className="w-full p-2 bg-gray-800 rounded border border-gray-700 focus:border-blue-500 outline-none"
          />
        </div>
        <div>
          <label>Credit Score</label>
          <input
            type="number"
            value={formData.credit_score}
            onChange={(e) => setFormData({...formData, credit_score: Number(e.target.value)})}
            className="w-full p-2 bg-gray-800 rounded border border-gray-700 focus:border-blue-500 outline-none"
          />
        </div>
        <div>
          <label>Property Value</label>
          <input
            type="number"
            value={formData.property_value}
            onChange={(e) => setFormData({...formData, property_value: Number(e.target.value)})}
            className="w-full p-2 bg-gray-800 rounded border border-gray-700 focus:border-blue-500 outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full p-3 bg-blue-600 hover:bg-blue-700 rounded font-bold transition disabled:opacity-50"
        >
          {loading ? 'Loading...' : 'Get Quote'}
        </button>
      </form>

      {results && (
        <div className="mt-8 p-4 bg-gray-800 rounded border border-gray-700">
          <h2 className="text-xl font-bold mb-4">Results</h2>
          <pre className="whitespace-pre-wrap">{JSON.stringify(results, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
