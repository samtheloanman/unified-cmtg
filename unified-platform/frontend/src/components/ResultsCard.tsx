import { useState } from 'react';
import ProgramComparison from './ProgramComparison';
import LeadSubmitModal from './LeadSubmitModal';
import { Quote } from '@/lib/api-client';

interface QuoteResult {
    ltv: number;
    matches_found: number;
    quotes: Quote[];
}

interface ResultsCardProps {
    results: QuoteResult;
    onReset: () => void;
}

type SortField = 'rate' | 'points' | 'lender' | 'term';
type SortDirection = 'asc' | 'desc';

/**
 * Extract numeric term in years from program name for sorting.
 */
function getTermYears(programName: string): number {
    const termMatch = programName.match(/(\d+)[\s-]?Year/i);
    return termMatch ? parseInt(termMatch[1]) : 999; // Default to high value for unknown
}

export default function ResultsCard({ results, onReset }: ResultsCardProps) {
    const [sortField, setSortField] = useState<SortField>('rate');
    const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
    const [selectedQuote, setSelectedQuote] = useState<Quote | null>(null);
    const [showModal, setShowModal] = useState(false);
    const [showSuccessMessage, setShowSuccessMessage] = useState(false);

    const sortedQuotes = [...(results.quotes || [])].sort((a, b) => {
        const multiplier = sortDirection === 'asc' ? 1 : -1;
        switch (sortField) {
            case 'rate':
                return ((a.adjusted_rate || a.base_rate) - (b.adjusted_rate || b.base_rate)) * multiplier;
            case 'points':
                return (a.points - b.points) * multiplier;
            case 'lender':
                return a.lender.localeCompare(b.lender) * multiplier;
            case 'term':
                return (getTermYears(a.program) - getTermYears(b.program)) * multiplier;
            default:
                return 0;
        }
    });

    const bestMatch = sortedQuotes[0];

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDirection('asc');
        }
    };

    const handleApply = (quote: Quote) => {
        setSelectedQuote(quote);
        setShowModal(true);
    };

    const handleSuccessfulSubmission = () => {
        setShowModal(false);
        setShowSuccessMessage(true);
        // Hide success message after 10 seconds
        setTimeout(() => setShowSuccessMessage(false), 10000);
    };

    if (!results.quotes || results.quotes.length === 0) {
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
                        We couldn&apos;t find programs that exactly match your criteria, but don&apos;t worry!
                        Our experts specialize in unique financing solutions.
                    </p>

                    <div className="bg-[#1daed4]/10 border border-[#1daed4] rounded-lg p-4 mb-6">
                        <p className="text-[#636363] text-sm mb-2">Your Loan-to-Value Ratio:</p>
                        <p className="text-2xl font-bold text-[#1daed4]">{results.ltv?.toFixed(2)}%</p>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-4">
                        <button
                            onClick={onReset}
                            className="flex-1 py-3 bg-white border-2 border-[#a5a5a5] hover:border-[#636363] text-[#636363] font-bold rounded-lg transition-colors"
                            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                        >
                            Try Different Criteria
                        </button>
                        <button
                            className="flex-1 py-3 bg-[#1daed4] hover:bg-[#17a0c4] text-white font-bold rounded-lg transition-colors shadow-md"
                            style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}
                        >
                            Speak With an Expert
                        </button>
                    </div>
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
                        <p className="text-[#636363]">We found {results.matches_found} programs for you!</p>
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
                        <p className="text-2xl font-bold text-[#1daed4]">{results.ltv?.toFixed(2)}%</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded border border-[#a5a5a5]">
                        <p className="text-sm text-[#636363] mb-1">Programs Found</p>
                        <p className="text-2xl font-bold text-[#1daed4]">{results.matches_found}</p>
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
                    <p className="text-white/80 mb-4">{bestMatch.program}</p>
                    <div className="flex gap-6">
                        <div>
                            <p className="text-white/70 text-sm">Rate</p>
                            <p className="text-3xl font-bold">{bestMatch.adjusted_rate || bestMatch.base_rate}%</p>
                        </div>
                        <div>
                            <p className="text-white/70 text-sm">Points</p>
                            <p className="text-3xl font-bold">{bestMatch.points}</p>
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

            {/* Success Message */}
            {showSuccessMessage && (
                <div className="bg-[#1daed4] border-2 border-[#1daed4] rounded-lg p-6 text-white shadow-lg">
                    <h3 className="text-2xl font-bold mb-2" style={{ fontFamily: 'Bebas Neue, Arial, sans-serif' }}>
                        ✓ Application Submitted!
                    </h3>
                    <p className="text-white/90">
                        Check your email for your personalized application link from Floify.
                        You'll be guided through the rest of the application process securely.
                    </p>
                </div>
            )}

            {/* Comparison Table */}
            {sortedQuotes.length > 1 && (
                <ProgramComparison
                    quotes={sortedQuotes}
                    sortField={sortField}
                    sortDirection={sortDirection}
                    onSort={handleSort}
                    onApply={handleApply}
                />
            )}

            {/* Lead Submit Modal */}
            {selectedQuote && (
                <LeadSubmitModal
                    selectedQuote={selectedQuote}
                    isOpen={showModal}
                    onClose={() => setShowModal(false)}
                    onSuccess={handleSuccessfulSubmission}
                />
            )}
        </div>
    );
}
