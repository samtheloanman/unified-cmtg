import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ResultsCard from '../ResultsCard';
import { QualificationResponse, MatchedProgram } from '@/lib/api-client';

// Mock LeadSubmitModal to avoid complex modal logic in unit test
// We just verify it is rendered when Apply is clicked
jest.mock('../LeadSubmitModal', () => {
    return function MockModal({ isOpen, onSuccess }: { isOpen: boolean; onSuccess: () => void }) {
        if (!isOpen) return null;
        return (
            <div data-testid="mock-modal">
                <button onClick={onSuccess}>Submit</button>
            </div>
        );
    };
});

// Mock ProgramComparison (disabled in component, but if re-enabled)
jest.mock('../ProgramComparison', () => () => <div data-testid="program-comparison" />);

const mockMatch: MatchedProgram = {
    program_id: 1,
    program_name: 'Test Program',
    lender: 'Test Lender',
    estimated_rate_range: '6.5-7.0',
    match_score: 90,
    notes: ['Note 1'],
};

const mockResults: QualificationResponse = {
    total_matches: 1,
    calculated_ltv: 80,
    matched_programs: [mockMatch],
};

const mockOnReset = jest.fn();

describe('ResultsCard', () => {
    beforeEach(() => {
        mockOnReset.mockClear();
    });

    it('renders no matches state correctly', () => {
        const emptyResults: QualificationResponse = {
            total_matches: 0,
            calculated_ltv: 0,
            matched_programs: [],
        };

        render(<ResultsCard results={emptyResults} onReset={mockOnReset} />);

        expect(screen.getByText('No Exact Matches Found')).toBeInTheDocument();
        expect(screen.getByText('Try Different Criteria')).toBeInTheDocument();
    });

    it('renders matches correctly', () => {
        render(<ResultsCard results={mockResults} onReset={mockOnReset} />);

        expect(screen.getByText('Your Quote Results')).toBeInTheDocument();
        expect(screen.getAllByText('Test Lender')[0]).toBeInTheDocument();
        expect(screen.getAllByText('Test Program')[0]).toBeInTheDocument();
        // Check rate range and score
        expect(screen.getAllByText('6.5-7.0%')[0]).toBeInTheDocument();
        expect(screen.getAllByText('90')[0]).toBeInTheDocument();
    });

    it('opens modal on Apply click', () => {
        render(<ResultsCard results={mockResults} onReset={mockOnReset} />);

        const applyButtons = screen.getAllByText('Apply Now');
        fireEvent.click(applyButtons[0]); // Best match card button

        expect(screen.getByTestId('mock-modal')).toBeInTheDocument();
    });

    it('calls onReset when Start Over is clicked', () => {
        render(<ResultsCard results={mockResults} onReset={mockOnReset} />);

        fireEvent.click(screen.getByText('Start Over'));
        expect(mockOnReset).toHaveBeenCalled();
    });
});
