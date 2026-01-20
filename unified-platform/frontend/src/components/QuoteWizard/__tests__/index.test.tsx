import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import QuoteWizard from '../index';
import { apiClient } from '@/lib/api-client';

// Mock Step components to simplify integration test
jest.mock('../Step1PropertyState', () => ({ onNext }: any) => <button onClick={onNext}>Next1</button>);
jest.mock('../Step2LoanAmount', () => ({ onNext }: any) => <button onClick={onNext}>Next2</button>);
jest.mock('../Step3CreditScore', () => ({ onNext }: any) => <button onClick={onNext}>Next3</button>);
jest.mock('../Step4PropertyValue', () => ({ onNext }: any) => <button onClick={onNext}>Next4</button>); // Actually calls submit

// Mock ResultsCard to verify it renders with correct data
jest.mock('../../ResultsCard', () => ({ results }: any) => (
    <div data-testid="results-card">Results: {results.total_matches}</div>
));

jest.mock('@/lib/api-client', () => ({
    apiClient: {
        pricing: {
            qualify: jest.fn(),
        },
    },
}));

describe('QuoteWizard Integration', () => {
    it('completes the flow and renders results', async () => {
        const mockQualifyResponse = {
            success: true,
            data: {
                total_matches: 5,
                calculated_ltv: 80,
                matched_programs: [],
            },
        };

        (apiClient.pricing.qualify as jest.Mock).mockResolvedValue(mockQualifyResponse);

        render(<QuoteWizard />);

        // Step 1
        fireEvent.click(screen.getByText('Next1'));

        // Step 2
        fireEvent.click(screen.getByText('Next2'));

        // Step 3
        fireEvent.click(screen.getByText('Next3'));

        // Step 4 (Submit)
        fireEvent.click(screen.getByText('Next4'));

        // Wait for results
        await waitFor(() => {
            expect(screen.getByTestId('results-card')).toBeInTheDocument();
        });

        expect(screen.getByText('Results: 5')).toBeInTheDocument();
        expect(apiClient.pricing.qualify).toHaveBeenCalled();
    });

    it('handles API error', async () => {
        const mockErrorResponse = {
            success: false,
            error: { detail: 'API Error' },
        };

        (apiClient.pricing.qualify as jest.Mock).mockResolvedValue(mockErrorResponse);

        render(<QuoteWizard />);

        // Fast forward to submit
        fireEvent.click(screen.getByText('Next1'));
        fireEvent.click(screen.getByText('Next2'));
        fireEvent.click(screen.getByText('Next3'));
        fireEvent.click(screen.getByText('Next4'));

        await waitFor(() => {
            expect(screen.getByText('API Error')).toBeInTheDocument();
        });
    });
});
