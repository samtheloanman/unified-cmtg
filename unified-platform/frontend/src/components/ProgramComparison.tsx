'use client';

import { Quote } from '@/lib/api-client';

type SortField = 'rate' | 'points' | 'lender' | 'term';
type SortDirection = 'asc' | 'desc';

interface ProgramComparisonProps {
    quotes: Quote[];
    sortField: SortField;
    sortDirection: SortDirection;
    onSort: (field: SortField) => void;
    onApply: (quote: Quote) => void;
}

/**
 * Extract term (e.g., "30-Year", "15-Year") from program name.
 * Returns the term string or empty if not found.
 */
function extractTerm(programName: string): string {
    const termMatch = programName.match(/(\d+)[\s-]?Year/i);
    return termMatch ? `${termMatch[1]}-Year` : '';
}

/**
 * Extract numeric year value for sorting.
 */
function getTermYears(programName: string): number {
    const termMatch = programName.match(/(\d+)[\s-]?Year/i);
    return termMatch ? parseInt(termMatch[1]) : 999; // Default to high value for unknown
}

const SortIcon = ({
    field,
    currentSortField,
    sortDirection
}: {
    field: SortField;
    currentSortField: SortField;
    sortDirection: SortDirection;
}) => {
    if (currentSortField !== field) {
        return <span className="text-[#a5a5a5] ml-1">↕</span>;
    }
    return <span className="text-[#1daed4] ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>;
};

export default function ProgramComparison({ quotes, sortField, sortDirection, onSort, onApply }: ProgramComparisonProps) {
    return (
        <div className="bg-white border-2 border-[#a5a5a5] rounded-lg shadow-lg overflow-hidden">
            <div className="bg-[#636363] text-white px-6 py-4">
                <h4 className="text-xl font-bold font-heading">
                    Compare All Programs
                </h4>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b-2 border-[#a5a5a5]">
                        <tr>
                            <th
                                className="px-6 py-4 text-left text-sm font-semibold text-[#636363] cursor-pointer hover:bg-gray-100 transition-colors"
                                onClick={() => onSort('lender')}
                            >
                                Lender <SortIcon field="lender" currentSortField={sortField} sortDirection={sortDirection} />
                            </th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-[#636363]">
                                Program
                            </th>
                            <th
                                className="px-6 py-4 text-center text-sm font-semibold text-[#636363] cursor-pointer hover:bg-gray-100 transition-colors"
                                onClick={() => onSort('term')}
                            >
                                Term <SortIcon field="term" currentSortField={sortField} sortDirection={sortDirection} />
                            </th>
                            <th
                                className="px-6 py-4 text-center text-sm font-semibold text-[#636363] cursor-pointer hover:bg-gray-100 transition-colors"
                                onClick={() => onSort('rate')}
                            >
                                Rate <SortIcon field="rate" currentSortField={sortField} sortDirection={sortDirection} />
                            </th>
                            <th
                                className="px-6 py-4 text-center text-sm font-semibold text-[#636363] cursor-pointer hover:bg-gray-100 transition-colors"
                                onClick={() => onSort('points')}
                            >
                                Points <SortIcon field="points" currentSortField={sortField} sortDirection={sortDirection} />
                            </th>
                            <th className="px-6 py-4 text-center text-sm font-semibold text-[#636363]">
                                Action
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-[#a5a5a5]/50">
                        {quotes.map((quote, index) => (
                            <tr
                                key={index}
                                className={`
                  hover:bg-[#1daed4]/5 transition-colors
                  ${index === 0 ? 'bg-[#1daed4]/10' : ''}
                `}
                            >
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-2">
                                        {index === 0 && (
                                            <span className="text-yellow-500">⭐</span>
                                        )}
                                        <span className="font-semibold text-[#636363]">{quote.lender}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-[#636363]">
                                    {quote.program}
                                </td>
                                <td className="px-6 py-4 text-center">
                                    <span className="font-semibold text-[#636363]">
                                        {extractTerm(quote.program) || 'N/A'}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-center">
                                    <span className="font-bold text-[#1daed4] text-lg">{quote.adjusted_rate || quote.base_rate}%</span>
                                </td>
                                <td className="px-6 py-4 text-center text-[#636363]">
                                    {quote.points}
                                </td>
                                <td className="px-6 py-4 text-center">
                                    <button
                                        onClick={() => onApply(quote)}
                                        className="px-4 py-2 bg-[#1daed4] hover:bg-[#17a0c4] text-white text-sm font-semibold rounded transition-colors shadow-sm hover:shadow-md"
                                    >
                                        Apply
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="bg-gray-50 px-6 py-3 border-t border-[#a5a5a5]/50 text-center">
                <p className="text-xs text-[#a5a5a5]">
                    Rates and terms are subject to change. Contact us for the most up-to-date information.
                </p>
            </div>
        </div>
    );
}
