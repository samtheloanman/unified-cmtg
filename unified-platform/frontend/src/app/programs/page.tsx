'use client';

import { useState, useEffect } from 'react';
import { apiClient, type LenderProgramOffering } from '@/lib/api-client';

/**
 * Extract term from program name
 */
function extractTerm(programName: string): string {
    const termMatch = programName.match(/(\d+)[\s-]?Year/i);
    return termMatch ? `${termMatch[1]}-Year` : 'Varies';
}

/**
 * Format currency for display
 */
function formatCurrency(amount: number): string {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
    }).format(amount);
}

export default function ProgramsPage() {
    const [programs, setPrograms] = useState<LenderProgramOffering[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [filter, setFilter] = useState<'all' | 'residential' | 'commercial'>('all');

    useEffect(() => {
        loadPrograms();
    }, []);

    const loadPrograms = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await apiClient.pricing.getPrograms();

            if (!response.success) {
                throw new Error(response.error.detail || response.error.error);
            }

            setPrograms(response.data.results);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load programs');
        } finally {
            setLoading(false);
        }
    };

    const filteredPrograms = programs.filter((program) => {
        if (filter === 'all') return true;
        return program.program_type.property_types.includes(filter);
    });

    return (
        <div className="min-h-screen bg-white">
            {/* Header */}
            <div className="bg-[#636363] text-white py-4 px-6">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <h1
                        className="text-3xl font-bold tracking-wide"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        CUSTOM MORTGAGE
                    </h1>
                    <span
                        className="text-sm tracking-widest"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        NATIONWIDE LENDER
                    </span>
                </div>
            </div>

            {/* Hero Section */}
            <div className="bg-gradient-to-r from-gray-50 to-white py-12 px-6 border-b-4 border-[#1daed4]">
                <div className="max-w-7xl mx-auto">
                    <h2
                        className="text-5xl font-bold text-[#636363] mb-4"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Loan Programs
                    </h2>
                    <p className="text-lg text-[#636363] max-w-2xl">
                        Explore our comprehensive range of financing solutions. We specialize in
                        unique mortgage requirements with expert, client-focused service.
                    </p>
                </div>
            </div>

            {/* Main Content */}
            <div className="max-w-7xl mx-auto py-12 px-6">
                {/* Filters */}
                <div className="mb-8 flex gap-4">
                    <button
                        onClick={() => setFilter('all')}
                        className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                            filter === 'all'
                                ? 'bg-[#1daed4] text-white'
                                : 'bg-gray-100 text-[#636363] hover:bg-gray-200'
                        }`}
                    >
                        All Programs
                    </button>
                    <button
                        onClick={() => setFilter('residential')}
                        className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                            filter === 'residential'
                                ? 'bg-[#1daed4] text-white'
                                : 'bg-gray-100 text-[#636363] hover:bg-gray-200'
                        }`}
                    >
                        Residential
                    </button>
                    <button
                        onClick={() => setFilter('commercial')}
                        className={`px-6 py-3 rounded-lg font-semibold transition-colors ${
                            filter === 'commercial'
                                ? 'bg-[#1daed4] text-white'
                                : 'bg-gray-100 text-[#636363] hover:bg-gray-200'
                        }`}
                    >
                        Commercial
                    </button>
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="text-center py-12">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-[#1daed4] border-t-transparent"></div>
                        <p className="text-[#636363] mt-4">Loading programs...</p>
                    </div>
                )}

                {/* Error State */}
                {error && (
                    <div className="bg-red-50 border-2 border-red-500 rounded-lg p-6 text-center">
                        <p className="text-red-700 font-semibold">Error loading programs</p>
                        <p className="text-red-600 text-sm mt-2">{error}</p>
                        <button
                            onClick={loadPrograms}
                            className="mt-4 px-6 py-2 bg-red-500 text-white font-semibold rounded hover:bg-red-600 transition-colors"
                        >
                            Retry
                        </button>
                    </div>
                )}

                {/* Programs Grid */}
                {!loading && !error && (
                    <>
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {filteredPrograms.map((program) => (
                                <div
                                    key={program.id}
                                    className="bg-white border-2 border-[#a5a5a5] rounded-lg shadow-lg hover:border-[#1daed4] transition-colors overflow-hidden"
                                >
                                    {/* Card Header */}
                                    <div className="bg-[#636363] text-white px-6 py-4">
                                        <h3
                                            className="text-2xl font-bold"
                                            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                                        >
                                            {program.program_type.name}
                                        </h3>
                                        <p className="text-white/80 text-sm mt-1">
                                            {program.lender.company_name}
                                        </p>
                                    </div>

                                    {/* Card Body */}
                                    <div className="p-6 space-y-4">
                                        {/* Rate Range */}
                                        <div className="flex justify-between items-center pb-4 border-b border-[#a5a5a5]/30">
                                            <div>
                                                <p className="text-xs text-[#a5a5a5] uppercase tracking-wide">
                                                    Rate Range
                                                </p>
                                                <p className="text-2xl font-bold text-[#1daed4] mt-1">
                                                    {program.min_rate}% - {program.max_rate}%
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-xs text-[#a5a5a5] uppercase tracking-wide">
                                                    Term
                                                </p>
                                                <p className="text-lg font-semibold text-[#636363] mt-1">
                                                    {extractTerm(program.program_type.name)}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Details Grid */}
                                        <div className="grid grid-cols-2 gap-4 text-sm">
                                            <div>
                                                <p className="text-[#a5a5a5]">Loan Amount</p>
                                                <p className="text-[#636363] font-semibold mt-1">
                                                    {formatCurrency(program.min_loan)} -{' '}
                                                    {formatCurrency(program.max_loan)}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-[#a5a5a5]">Max LTV</p>
                                                <p className="text-[#636363] font-semibold mt-1">
                                                    {program.max_ltv}%
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-[#a5a5a5]">Min FICO</p>
                                                <p className="text-[#636363] font-semibold mt-1">
                                                    {program.min_fico}
                                                </p>
                                            </div>
                                            <div>
                                                <p className="text-[#a5a5a5]">Points</p>
                                                <p className="text-[#636363] font-semibold mt-1">
                                                    {program.min_points} - {program.max_points}
                                                </p>
                                            </div>
                                        </div>

                                        {/* Tags */}
                                        <div className="pt-4 border-t border-[#a5a5a5]/30">
                                            <div className="flex flex-wrap gap-2">
                                                {program.program_type.property_types.map((type) => (
                                                    <span
                                                        key={type}
                                                        className="px-3 py-1 bg-[#1daed4]/10 text-[#1daed4] text-xs font-semibold rounded-full"
                                                    >
                                                        {type}
                                                    </span>
                                                ))}
                                                {program.program_type.category && (
                                                    <span className="px-3 py-1 bg-[#636363]/10 text-[#636363] text-xs font-semibold rounded-full">
                                                        {program.program_type.category}
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        {/* CTA Button */}
                                        <button className="w-full mt-4 py-3 bg-[#1daed4] hover:bg-[#17a0c4] text-white font-bold rounded-lg transition-colors shadow-md"
                                            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif', fontSize: '1.1rem' }}>
                                            Get Quote
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Empty State */}
                        {filteredPrograms.length === 0 && (
                            <div className="text-center py-12">
                                <p className="text-[#636363] text-lg">No programs found for this filter.</p>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Footer */}
            <div className="bg-[#636363] text-white py-8 px-6 mt-12">
                <div className="max-w-7xl mx-auto text-center">
                    <p className="text-sm">
                        © 2026 Custom Mortgage Inc. | Nationwide Lender | FinTech Financing Solutions
                    </p>
                </div>
            </div>
        </div>
    );
}
