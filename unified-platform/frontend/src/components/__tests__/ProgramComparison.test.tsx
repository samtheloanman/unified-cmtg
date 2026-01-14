/**
 * ProgramComparison Component Test Suite
 *
 * Tests for the loan program comparison table component.
 * Ensures proper rendering, sorting, and term extraction.
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ProgramComparison from '../ProgramComparison';

const mockQuotes = [
    {
        lender: 'Acra Lending',
        program: 'DSCR 30-Year Fixed',
        base_rate: 7.25,
        points: 0.5,
    },
    {
        lender: 'Test Lender',
        program: 'Non-QM 15-Year Fixed',
        base_rate: 6.75,
        points: 1.0,
    },
    {
        lender: 'Another Lender',
        program: 'Conventional 20-Year',
        base_rate: 7.0,
        points: 0.75,
    },
];

describe('ProgramComparison', () => {
    const mockOnSort = jest.fn();

    beforeEach(() => {
        mockOnSort.mockClear();
    });

    it('renders comparison table with all quotes', () => {
        render(
            <ProgramComparison
                quotes={mockQuotes}
                sortField="rate"
                sortDirection="asc"
                onSort={mockOnSort}
            />
        );

        // Check table header
        expect(screen.getByText('Compare All Programs')).toBeInTheDocument();

        // Check column headers
        expect(screen.getByText('Lender')).toBeInTheDocument();
        expect(screen.getByText('Program')).toBeInTheDocument();
        expect(screen.getByText('Term')).toBeInTheDocument();
        expect(screen.getByText('Rate')).toBeInTheDocument();
        expect(screen.getByText('Points')).toBeInTheDocument();

        // Check all lenders are displayed
        expect(screen.getByText('Acra Lending')).toBeInTheDocument();
        expect(screen.getByText('Test Lender')).toBeInTheDocument();
        expect(screen.getByText('Another Lender')).toBeInTheDocument();
    });

    it('extracts and displays terms correctly', () => {
        render(
            <ProgramComparison
                quotes={mockQuotes}
                sortField="rate"
                sortDirection="asc"
                onSort={mockOnSort}
            />
        );

        // Check term extraction
        expect(screen.getByText('30-Year')).toBeInTheDocument();
        expect(screen.getByText('15-Year')).toBeInTheDocument();
        expect(screen.getByText('20-Year')).toBeInTheDocument();
    });

    it('displays rates with correct formatting', () => {
        render(
            <ProgramComparison
                quotes={mockQuotes}
                sortField="rate"
                sortDirection="asc"
                onSort={mockOnSort}
            />
        );

        expect(screen.getByText('7.25%')).toBeInTheDocument();
        expect(screen.getByText('6.75%')).toBeInTheDocument();
        expect(screen.getByText('7%')).toBeInTheDocument();
    });

    it('calls onSort when clicking sortable headers', () => {
        render(
            <ProgramComparison
                quotes={mockQuotes}
                sortField="rate"
                sortDirection="asc"
                onSort={mockOnSort}
            />
        );

        // Click on lender header
        const lenderHeader = screen.getByText('Lender').parentElement;
        if (lenderHeader) {
            fireEvent.click(lenderHeader);
            expect(mockOnSort).toHaveBeenCalledWith('lender');
        }

        // Click on rate header
        mockOnSort.mockClear();
        const rateHeader = screen.getByText('Rate').parentElement;
        if (rateHeader) {
            fireEvent.click(rateHeader);
            expect(mockOnSort).toHaveBeenCalledWith('rate');
        }

        // Click on term header
        mockOnSort.mockClear();
        const termHeader = screen.getByText('Term').parentElement;
        if (termHeader) {
            fireEvent.click(termHeader);
            expect(mockOnSort).toHaveBeenCalledWith('term');
        }
    });

    it('highlights best match (first row)', () => {
        const { container } = render(
            <ProgramComparison
                quotes={mockQuotes}
                sortField="rate"
                sortDirection="asc"
                onSort={mockOnSort}
            />
        );

        // First row should have star icon
        const firstRow = container.querySelector('tbody tr:first-child');
        expect(firstRow).toHaveTextContent('⭐');
    });

    it('renders Apply buttons for all quotes', () => {
        render(
            <ProgramComparison
                quotes={mockQuotes}
                sortField="rate"
                sortDirection="asc"
                onSort={mockOnSort}
            />
        );

        const applyButtons = screen.getAllByText('Apply');
        expect(applyButtons).toHaveLength(mockQuotes.length);
    });

    it('shows sort icons correctly', () => {
        const { rerender } = render(
            <ProgramComparison
                quotes={mockQuotes}
                sortField="rate"
                sortDirection="asc"
                onSort={mockOnSort}
            />
        );

        // Rate column should show ascending icon
        expect(screen.getByText(/Rate/i).parentElement).toHaveTextContent('↑');

        // Re-render with descending sort
        rerender(
            <ProgramComparison
                quotes={mockQuotes}
                sortField="rate"
                sortDirection="desc"
                onSort={mockOnSort}
            />
        );

        expect(screen.getByText(/Rate/i).parentElement).toHaveTextContent('↓');
    });

    it('follows Premium FinTech color scheme', () => {
        const { container } = render(
            <ProgramComparison
                quotes={mockQuotes}
                sortField="rate"
                sortDirection="asc"
                onSort={mockOnSort}
            />
        );

        // Check for Cyan accent (#1daed4) in rate display
        const rateCell = screen.getByText('7.25%');
        expect(rateCell).toHaveClass('text-[#1daed4]');

        // Check for Gray (#636363) in header
        const header = container.querySelector('.bg-\\[\\#636363\\]');
        expect(header).toBeInTheDocument();
    });
});
