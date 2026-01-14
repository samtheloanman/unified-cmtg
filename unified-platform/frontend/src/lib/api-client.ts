/**
 * Type-safe API client for the Unified CMTG Platform.
 *
 * This client provides a centralized, type-safe interface for all API calls,
 * following the Premium FinTech design principles with proper error handling
 * and response typing.
 */

import { API_BASE } from './api';

/**
 * Quote request payload
 */
export interface QuoteRequest {
    property_state: string;
    loan_amount: number;
    credit_score: number;
    property_value: number;
    property_type?: string;
    entity_type?: string;
    loan_purpose?: string;
    occupancy?: string;
}

/**
 * Individual quote from a lender
 */
export interface Quote {
    lender: string;
    program: string;
    base_rate: number;
    adjusted_rate: number;
    points: number;
    adjustments_applied: number;
    min_loan: number;
    max_loan: number;
}

/**
 * Quote response from API
 */
export interface QuoteResponse {
    quotes: Quote[];
    ltv: number;
    loan_amount: number;
    property_value: number;
    matches_found: number;
}

/**
 * Health check response
 */
export interface HealthResponse {
    status: 'healthy' | 'unhealthy';
}

/**
 * API error response
 */
export interface APIError {
    error: string;
    detail?: string;
    missing?: string[];
}

/**
 * Generic API response wrapper for error handling
 */
export type APIResponse<T> =
    | { success: true; data: T }
    | { success: false; error: APIError };

/**
 * Base API client class with shared functionality
 */
class BaseAPIClient {
    protected baseURL: string;

    constructor(baseURL: string = API_BASE) {
        this.baseURL = baseURL;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    protected async request<T>(
        endpoint: string,
        options?: RequestInit
    ): Promise<APIResponse<T>> {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options?.headers,
                },
            });

            const data = await response.json();

            if (!response.ok) {
                return {
                    success: false,
                    error: data as APIError,
                };
            }

            return {
                success: true,
                data: data as T,
            };
        } catch (error) {
            return {
                success: false,
                error: {
                    error: 'Network error',
                    detail:
                        error instanceof Error
                            ? error.message
                            : 'Unable to connect to server',
                },
            };
        }
    }

    /**
     * GET request helper
     */
    protected async get<T>(endpoint: string): Promise<APIResponse<T>> {
        return this.request<T>(endpoint, { method: 'GET' });
    }

    /**
     * POST request helper
     */
    protected async post<T>(
        endpoint: string,
        body: unknown
    ): Promise<APIResponse<T>> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: JSON.stringify(body),
        });
    }
}

/**
 * Lender information
 */
export interface Lender {
    id: number;
    company_name: string;
    include_states: string[];
    is_active: boolean;
}

/**
 * Program type information
 */
export interface ProgramType {
    id: number;
    name: string;
    category: string;
    loan_type: string;
    property_types: string[];
    entity_types: string[];
    purposes: string[];
    occupancy: string[];
    base_min_fico: number;
    base_max_ltv: number;
}

/**
 * Lender program offering
 */
export interface LenderProgramOffering {
    id: number;
    lender: Lender;
    program_type: ProgramType;
    min_rate: number;
    max_rate: number;
    min_points: number;
    max_points: number;
    min_fico: number;
    max_ltv: number;
    min_loan: number;
    max_loan: number;
    is_active: boolean;
}

/**
 * Programs listing response
 */
export interface ProgramsListResponse {
    results: LenderProgramOffering[];
    count: number;
}

/**
 * Pricing API client
 */
class PricingAPI extends BaseAPIClient {
    /**
     * Get loan quotes based on qualification criteria
     */
    async getQuotes(request: QuoteRequest): Promise<APIResponse<QuoteResponse>> {
        return this.post<QuoteResponse>('/api/v1/quote/', request);
    }

    /**
     * Get list of all loan programs
     */
    async getPrograms(): Promise<APIResponse<ProgramsListResponse>> {
        return this.get<ProgramsListResponse>('/api/v1/programs/');
    }

    /**
     * Health check endpoint
     */
    async healthCheck(): Promise<APIResponse<HealthResponse>> {
        return this.get<HealthResponse>('/api/v1/health/');
    }
}

/**
 * Rate sheet upload payload
 */
export interface RateSheetUploadRequest {
    pdf_url: string;
    lender_id?: number;
    effective_date?: string;
}

/**
 * Rate sheet upload response
 */
export interface RateSheetUploadResponse {
    task_id: string;
    status: 'queued' | 'processing' | 'completed' | 'failed';
    message: string;
}

/**
 * Rate Sheet API client
 */
class RateSheetAPI extends BaseAPIClient {
    /**
     * Upload/trigger rate sheet ingestion
     */
    async upload(
        request: RateSheetUploadRequest
    ): Promise<APIResponse<RateSheetUploadResponse>> {
        return this.post<RateSheetUploadResponse>(
            '/api/v1/ratesheets/upload/',
            request
        );
    }

    /**
     * Get status of rate sheet ingestion task
     */
    async getTaskStatus(taskId: string): Promise<APIResponse<RateSheetUploadResponse>> {
        return this.get<RateSheetUploadResponse>(
            `/api/v1/ratesheets/tasks/${taskId}/`
        );
    }
}

/**
 * Main API client export with all sub-clients
 */
class APIClient {
    pricing: PricingAPI;
    rateSheets: RateSheetAPI;

    constructor(baseURL: string = API_BASE) {
        this.pricing = new PricingAPI(baseURL);
        this.rateSheets = new RateSheetAPI(baseURL);
    }
}

// Export singleton instance
export const apiClient = new APIClient();

// Export class for testing/custom instances
export { APIClient };
