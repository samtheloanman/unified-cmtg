/**
 * API Client Test Suite
 *
 * Tests for the type-safe API client following Premium FinTech standards.
 * These tests ensure robust error handling and proper response typing.
 */

import { APIClient, apiClient } from '../api-client';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('APIClient', () => {
    beforeEach(() => {
        mockFetch.mockClear();
    });

    describe('PricingAPI', () => {
        describe('getQuotes', () => {
            it('should successfully fetch quotes with valid request', async () => {
                const mockResponse = {
                    quotes: [
                        {
                            lender: 'Acra Lending',
                            program: 'DSCR 30-Year Fixed',
                            base_rate: 7.25,
                            adjusted_rate: 7.25,
                            points: 0.0,
                            adjustments_applied: 0,
                            min_loan: 75000,
                            max_loan: 2000000,
                        },
                    ],
                    ltv: 76.92,
                    loan_amount: 500000,
                    property_value: 650000,
                    matches_found: 1,
                };

                mockFetch.mockResolvedValueOnce({
                    ok: true,
                    json: async () => mockResponse,
                });

                const result = await apiClient.pricing.getQuotes({
                    property_state: 'CA',
                    loan_amount: 500000,
                    credit_score: 720,
                    property_value: 650000,
                });

                expect(result.success).toBe(true);
                if (result.success) {
                    expect(result.data.quotes).toHaveLength(1);
                    expect(result.data.ltv).toBe(76.92);
                    expect(result.data.matches_found).toBe(1);
                }
            });

            it('should handle API errors gracefully', async () => {
                mockFetch.mockResolvedValueOnce({
                    ok: false,
                    json: async () => ({
                        error: 'Validation error',
                        detail: 'Missing required fields',
                    }),
                });

                const result = await apiClient.pricing.getQuotes({
                    property_state: '',
                    loan_amount: 0,
                    credit_score: 0,
                    property_value: 0,
                });

                expect(result.success).toBe(false);
                if (!result.success) {
                    expect(result.error.error).toBe('Validation error');
                    expect(result.error.detail).toBe('Missing required fields');
                }
            });

            it('should handle network errors', async () => {
                mockFetch.mockRejectedValueOnce(new Error('Network error'));

                const result = await apiClient.pricing.getQuotes({
                    property_state: 'CA',
                    loan_amount: 500000,
                    credit_score: 720,
                    property_value: 650000,
                });

                expect(result.success).toBe(false);
                if (!result.success) {
                    expect(result.error.error).toBe('Network error');
                }
            });
        });

        describe('qualify', () => {
            it('should successfully fetch qualification matches', async () => {
                const mockResponse = {
                    total_matches: 2,
                    calculated_ltv: 75.0,
                    matched_programs: [
                        {
                            program_id: 101,
                            program_name: 'Super Prime',
                            lender: 'Acme Lending',
                            estimated_rate_range: '6.5-7.0',
                            match_score: 95,
                            notes: ['Great fit'],
                        },
                    ],
                };

                mockFetch.mockResolvedValueOnce({
                    ok: true,
                    json: async () => mockResponse,
                });

                const result = await apiClient.pricing.qualify({
                    loan_amount: 500000,
                    property_value: 650000,
                    credit_score: 720,
                    property_state: 'CA',
                });

                expect(result.success).toBe(true);
                if (result.success) {
                    expect(result.data.total_matches).toBe(2);
                    expect(result.data.matched_programs).toHaveLength(1);
                    expect(result.data.matched_programs[0].match_score).toBe(95);
                }
            });
        });

        describe('healthCheck', () => {
            it('should return healthy status', async () => {
                mockFetch.mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ status: 'healthy' }),
                });

                const result = await apiClient.pricing.healthCheck();

                expect(result.success).toBe(true);
                if (result.success) {
                    expect(result.data.status).toBe('healthy');
                }
            });
        });
    });

    describe('RateSheetAPI', () => {
        describe('upload', () => {
            it('should upload rate sheet successfully', async () => {
                const mockResponse = {
                    task_id: 'task-123',
                    status: 'queued' as const,
                    message: 'Rate sheet ingestion started',
                };

                mockFetch.mockResolvedValueOnce({
                    ok: true,
                    json: async () => mockResponse,
                });

                const result = await apiClient.rateSheets.upload({
                    pdf_url: 'https://example.com/ratesheet.pdf',
                    lender_id: 1,
                });

                expect(result.success).toBe(true);
                if (result.success) {
                    expect(result.data.task_id).toBe('task-123');
                    expect(result.data.status).toBe('queued');
                }
            });
        });

        describe('getTaskStatus', () => {
            it('should fetch task status successfully', async () => {
                const mockResponse = {
                    task_id: 'task-123',
                    status: 'completed' as const,
                    message: 'Rate sheet processed successfully',
                };

                mockFetch.mockResolvedValueOnce({
                    ok: true,
                    json: async () => mockResponse,
                });

                const result = await apiClient.rateSheets.getTaskStatus('task-123');

                expect(result.success).toBe(true);
                if (result.success) {
                    expect(result.data.status).toBe('completed');
                }
            });
        });
    });
});
