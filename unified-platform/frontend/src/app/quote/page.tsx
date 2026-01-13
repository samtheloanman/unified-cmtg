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
            setError('Failed to fetch quote. Is the backend running?');
            console.error(err);
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-slate-900 text-white p-8">
            <div className="max-w-2xl mx-auto">
                <h1 className="text-4xl font-bold mb-2 text-amber-400">Mortgage Quote Calculator</h1>
                <p className="text-slate-400 mb-8">Get instant rate quotes from our lending partners</p>

                <form onSubmit={handleSubmit} className="space-y-6 bg-slate-800 p-6 rounded-xl">
                    <div>
                        <label className="block text-sm font-medium mb-2">Property State</label>
                        <input
                            type="text"
                            value={formData.property_state}
                            onChange={(e) => setFormData({ ...formData, property_state: e.target.value })}
                            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:ring-2 focus:ring-amber-400 focus:border-transparent"
                            placeholder="CA"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Loan Amount</label>
                        <input
                            type="number"
                            value={formData.loan_amount}
                            onChange={(e) => setFormData({ ...formData, loan_amount: Number(e.target.value) })}
                            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:ring-2 focus:ring-amber-400"
                            placeholder="500000"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Credit Score (FICO)</label>
                        <input
                            type="number"
                            value={formData.credit_score}
                            onChange={(e) => setFormData({ ...formData, credit_score: Number(e.target.value) })}
                            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:ring-2 focus:ring-amber-400"
                            placeholder="740"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2">Property Value</label>
                        <input
                            type="number"
                            value={formData.property_value}
                            onChange={(e) => setFormData({ ...formData, property_value: Number(e.target.value) })}
                            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:ring-2 focus:ring-amber-400"
                            placeholder="650000"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full p-4 bg-amber-500 hover:bg-amber-600 disabled:bg-slate-600 text-slate-900 font-bold rounded-lg transition-colors"
                    >
                        {loading ? 'Getting Quotes...' : 'Get Quote'}
                    </button>
                </form>

                {error && (
                    <div className="mt-6 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-300">
                        {error}
                    </div>
                )}

                {results && (
                    <div className="mt-8 bg-slate-800 p-6 rounded-xl">
                        <h2 className="text-2xl font-bold mb-4 text-amber-400">Quote Results</h2>
                        <div className="grid grid-cols-2 gap-4 mb-4">
                            <div className="bg-slate-700 p-4 rounded-lg">
                                <p className="text-slate-400 text-sm">Loan-to-Value</p>
                                <p className="text-2xl font-bold">{results.ltv?.toFixed(2)}%</p>
                            </div>
                            <div className="bg-slate-700 p-4 rounded-lg">
                                <p className="text-slate-400 text-sm">Matches Found</p>
                                <p className="text-2xl font-bold">{results.matches_found}</p>
                            </div>
                        </div>

                        {results.quotes && results.quotes.length > 0 ? (
                            <div className="space-y-4">
                                {results.quotes.map((q: any, i: number) => (
                                    <div key={i} className="bg-slate-700 p-4 rounded-lg">
                                        <p className="font-bold">{q.lender} - {q.program}</p>
                                        <p className="text-slate-400">Rate: {q.base_rate}% | Points: {q.points}</p>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-slate-400">No matching programs found. Try adjusting your criteria or add seed data.</p>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}
