import { useState } from 'react';
// import ProgramComparison from './ProgramComparison'; // Disabled for now
import LeadSubmitModal from './LeadSubmitModal';
import { Quote, QualificationResponse, MatchedProgram } from '@/lib/api-client';

interface ResultsCardProps {
    results: QualificationResponse;
    onReset: () => void;
}

type SortField = 'score' | 'rate' | 'lender';
type SortDirection = 'asc' | 'desc';

export default function ResultsCard({ results, onReset }: ResultsCardProps) {
    const [sortField, setSortField] = useState<SortField>('score'); // Default to Match Score
    const [sortDirection, setSortDirection] = useState<SortDirection>('desc'); // High score first
    const [selectedProgram, setSelectedProgram] = useState<MatchedProgram | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [showSuccessMessage, setShowSuccessMessage] = useState(false);

    const sortedPrograms = [...(results.matched_programs || [])].sort((a, b) => {
        const multiplier = sortDirection === 'asc' ? 1 : -1;
        switch (sortField) {
            case 'rate':
                // Parse "6.5-7.5" -> 6.5
                const rateA = parseFloat(a.estimated_rate_range) || 0;
                const rateB = parseFloat(b.estimated_rate_range) || 0;
                return (rateA - rateB) * multiplier;
            case 'score':
                return (a.match_score - b.match_score) * multiplier;
            case 'lender':
                return a.lender.localeCompare(b.lender) * multiplier;
            default:
                return 0;
        }
    });

    const bestMatch = sortedPrograms[0];

    // Adapter for Legacy Modal
    const quoteAdapter = selectedProgram ? {
        lender: selectedProgram.lender,
        program: selectedProgram.program_name,
        base_rate: parseFloat(selectedProgram.estimated_rate_range) || 0,
        adjusted_rate: parseFloat(selectedProgram.estimated_rate_range) || 0,
        points: 0,
        adjustments_applied: 0,
        min_loan: 0,
        max_loan: 0
    } : null;

    const handleApply = (program: MatchedProgram) => {
        setSelectedProgram(program);
        setShowModal(true);
    };

    const handleSuccessfulSubmission = () => {
        setShowModal(false);
        setShowSuccessMessage(true);
        setTimeout(() => setShowSuccessMessage(false), 10000);
    };

    if (!results.matched_programs || results.matched_programs.length === 0) {
        return (
            <div className="w-full max-w-2xl mx-auto">
                <div className="bg-white border-2 border-[#a5a5a5] rounded-lg shadow-lg p-8 text-center">
                    <div className="w-20 h-20 mx-auto mb-6 bg-[#a5a5a5]/20 rounded-full flex items-center justify-center">
                        <svg className="w-10 h-10 text-[#a5a5a5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>

                    <h3 className="text-3xl font-bold text-[#636363] mb-4" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                        No Exact Matches Found
                    </h3>
                    <p className="text-[#636363] mb-6">
                        We couldn&apos;t find programs that exactly match your criteria.
                    </p>

                    <div className="bg-[#1daed4]/10 border border-[#1daed4] rounded-lg p-4 mb-6">
                        <p className="text-[#636363] text-sm mb-2">Calculated LTV:</p>
                        <p className="text-2xl font-bold text-[#1daed4]">{results.calculated_ltv?.toFixed(2)}%</p>
                    </div>

                    <button
                        onClick={onReset}
                        className="w-full py-3 bg-white border-2 border-[#a5a5a5] hover:border-[#636363] text-[#636363] font-bold rounded-lg transition-colors"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                    >
                        Try Different Criteria
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full max-w-4xl mx-auto space-y-6">
            {/* Summary Card */}
            <div className="bg-white border-2 border-[#1daed4] rounded-lg shadow-lg p-6">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h3 className="text-3xl font-bold text-[#636363]" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                            Your Quote Results
                        </h3>
                        <p className="text-[#636363]">We found {results.total_matches} programs for you!</p>
                    </div>
                    <button
                        onClick={onReset}
                        className="px-4 py-2 text-sm bg-white border border-[#a5a5a5] hover:border-[#636363] text-[#636363] rounded transition-colors"
                    >
                        Start Over
                    </button>
                </div>

                <div className="grid grid-cols-2 gap-4">
                    <div className="bg-gray-50 p-4 rounded border border-[#a5a5a5]">
                        <p className="text-sm text-[#636363] mb-1">Loan-to-Value</p>
                        <p className="text-2xl font-bold text-[#1daed4]">{results.calculated_ltv?.toFixed(2)}%</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded border border-[#a5a5a5]">
                        <p className="text-sm text-[#636363] mb-1">Programs Found</p>
                        <p className="text-2xl font-bold text-[#1daed4]">{results.total_matches}</p>
                    </div>
                </div>
            </div>

            {/* Best Match Card */}
            {bestMatch && (
                <div className="bg-gradient-to-r from-[#1daed4] to-[#17a0c4] rounded-lg shadow-lg p-6 text-white">
                    <div className="flex items-center gap-2 mb-3">
                        <span className="bg-white/20 px-3 py-1 rounded-full text-sm font-semibold">
                            ⭐ Best Match
                        </span>
                    </div>
                    <h4 className="text-2xl font-bold mb-1" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                        {bestMatch.lender}
                    </h4>
                    <p className="text-white/80 mb-4">{bestMatch.program_name}</p>
                    <div className="flex gap-6">
                        <div>
                            <p className="text-white/70 text-sm">Est. Rate Range</p>
                            <p className="text-3xl font-bold">{bestMatch.estimated_rate_range}%</p>
                        </div>
                        <div>
                            <p className="text-white/70 text-sm">Match Score</p>
                            <p className="text-3xl font-bold">{bestMatch.match_score}</p>
                        </div>
                    </div>
                    <button
                        onClick={() => handleApply(bestMatch)}
                        className="mt-4 w-full py-3 bg-white text-[#1daed4] font-bold rounded-lg hover:bg-gray-100 transition-colors shadow-md"
                        style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                        Apply Now
                    </button>
                </div>
            )}

            {/* List View */}
            <div className="space-y-4">
                <div className="flex justify-between items-center">
                    <h3 className="text-xl font-bold text-[#636363]">All Matches</h3>
                    <div className="text-sm text-gray-500">
                        Sorted by: <span className="font-semibold capitalize">{sortField}</span>
                        <button onClick={() => setSortField('score')} className="ml-2 underline">Score</button>
                        <button onClick={() => setSortField('rate')} className="ml-2 underline">Rate</button>
                    </div>
                </div>

                {sortedPrograms.map(prog => (
                    <div key={prog.program_id} className="bg-white border rounded p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 hover:shadow-md transition-shadow">
                        <div>
                            <h4 className="font-bold text-lg text-[#636363]">{prog.lender}</h4>
                            <p className="text-sm text-gray-600">{prog.program_name}</p>
                            <div className="flex flex-wrap gap-2 mt-2">
                                {prog.notes.slice(0, 3).map((note, i) => (
                                    <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                                        {note}
                                    </span>
                                ))}
                            </div>
                        </div>
                        <div className="text-right flex flex-row sm:flex-col items-center sm:items-end gap-4 sm:gap-0 w-full sm:w-auto justify-between">
                            <div>
                                <div className="font-bold text-[#1daed4] text-xl">{prog.estimated_rate_range}%</div>
                                <div className="text-xs text-gray-500">Match Score: {prog.match_score}</div>
                            </div>
                            <button
                                onClick={() => handleApply(prog)}
                                className="px-4 py-2 bg-[#1daed4] text-white font-bold rounded hover:bg-[#17a0c4] transition-colors"
                            >
                                Apply
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Success Message */}
            {showSuccessMessage && (
                <div className="fixed bottom-4 right-4 bg-[#1daed4] text-white p-4 rounded-lg shadow-xl z-50 animate-fade-in-up">
                    <h3 className="font-bold">✓ Application Submitted!</h3>
                    <p className="text-sm">Check your email for next steps.</p>
                </div>
            )}

            {/* Modal */}
            {quoteAdapter && (
                <LeadSubmitModal
                    selectedQuote={quoteAdapter as unknown as Quote}
                    isOpen={showModal}
                    onClose={() => setShowModal(false)}
                    onSuccess={handleSuccessfulSubmission}
                />
            )}
        </div>
    );
}
