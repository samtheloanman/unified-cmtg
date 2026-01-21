import { apiClient } from '../api-client';
import { API_BASE } from '../api';

// Mock global fetch
global.fetch = jest.fn();

describe('APIClient', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('should fetch site configuration successfully', async () => {
        const mockConfig = { site_name: 'Test Site', phone: '123-456-7890' };
        (global.fetch as jest.Mock).mockResolvedValueOnce({
            ok: true,
            json: async () => mockConfig,
        });

        const response = await apiClient.cms.getSiteConfiguration();
        
        expect(global.fetch).toHaveBeenCalledWith(
            expect.stringContaining('/api/v1/site-config/'),
            expect.any(Object)
        );
        expect(response).toEqual({ success: true, data: mockConfig });
    });

    it('should handle API errors gracefully', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
            ok: false,
            json: async () => ({ error: 'Not found' }),
        });

        const response = await apiClient.cms.getSiteConfiguration();
        
        expect(response).toEqual({
            success: false,
            error: { error: 'Not found' }
        });
    });
});
