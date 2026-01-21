import { render, screen, waitFor } from '@testing-library/react';
import Header from '../Header';
import { apiClient } from '@/lib/api-client';

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    cms: {
      getSiteConfiguration: jest.fn(),
      getNavigation: jest.fn(),
    },
  },
}));

describe('Header Component', () => {
  const mockSiteConfig = {
    data: {
      site_name: 'Test Mortgage',
      phone_number: '555-0199',
      logo_url: '/test-logo.png',
    }
  };

  const mockNavMenu = {
    data: {
      items: [
        {
          id: '1',
          type: 'link',
          value: { link_text: 'Home', link_url: '/' }
        },
        {
          id: '2',
          type: 'sub_menu',
          value: {
            title: 'Programs',
            items: [
               { link_text: 'DSCR', link_url: '/programs/dscr', open_in_new_tab: false }
            ]
          }
        }
      ]
    }
  };

  beforeEach(() => {
    (apiClient.cms.getSiteConfiguration as jest.Mock).mockResolvedValue(mockSiteConfig);
    (apiClient.cms.getNavigation as jest.Mock).mockResolvedValue(mockNavMenu);
  });

  it('renders site phone number', async () => {
    render(<Header />);
    
    await waitFor(() => {
      expect(screen.getByText('555-0199')).toBeInTheDocument();
    });
  });

  it('renders navigation items', async () => {
    render(<Header />);

    await waitFor(() => {
      expect(screen.getByText('Home')).toBeInTheDocument();
      expect(screen.getByText('Programs')).toBeInTheDocument();
    });
  });
});
