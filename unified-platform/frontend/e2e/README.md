# End-to-End Testing with Playwright

## Setup Complete ✅

Playwright E2E testing is fully configured for the Unified CMTG Platform frontend.

### What's Included

- **Playwright Test Framework**: `@playwright/test@^1.57.0`
- **Configuration**: `playwright.config.ts`
- **Test Directory**: `e2e/`
- **Fixtures**: `e2e/fixtures/` for API response mocking
- **Comprehensive Test**: `full-application-flow.spec.ts` covering quote-to-lead flow

### Test Scripts

```bash
# Run all E2E tests (headless)
npm run test:e2e

# Run E2E tests with UI mode (interactive)
npm run test:e2e:ui

# Run E2E tests in headed mode (see browser)
npm run test:e2e:headed
```

### Running Tests

#### Option 1: From Host Machine (Recommended)

```bash
cd unified-platform/frontend

# Install dependencies (if not already done)
npm install

# Install Playwright browsers
npx playwright install chromium

# Run tests
npm run test:e2e
```

#### Option 2: From Docker (Requires Browser Dependencies)

The current Docker setup uses an Alpine-based Node image which doesn't include Chromium dependencies. To run tests in Docker, you would need to:

1. Update the Dockerfile to use a Debian-based image (e.g., `mcr.microsoft.com/playwright:latest`)
2. Or add browser dependencies to the Alpine image
3. Or create a separate test service in `docker-compose.yml`

### Test Coverage

The `full-application-flow.spec.ts` test covers the complete user journey:

1. **Quote Wizard Flow**
   - Property state selection
   - Loan amount input
   - Credit score input
   - Property value input
   - Quote submission

2. **Results Display**
   - Verify matched loan programs appear
   - Check lender names, program details, rates
   - Validate FICO×LTV adjustments applied

3. **Lead Submission**
   - Apply Now modal interaction
   - Form filling (first name, last name, email, phone)
   - Application submission
   - Success state verification

4. **API Mocking**
   - Quote API (`/api/v1/quote/`) mocked with realistic response
   - Lead API (`/api/v1/leads/`) mocked with validation
   - Network delays simulated for realistic behavior

### Fixtures

Mock API responses are stored in `e2e/fixtures/`:

- `quote-response.json`: Sample quote results with 2 loan programs (Acra Lending DSCR, Angel Oak Bank Statement)

### Configuration

The `playwright.config.ts` includes:

- **Base URL**: `http://127.0.0.1:3000` (adjust if needed)
- **Test Directory**: `./e2e`
- **Browsers**: Chromium (desktop)
- **Auto-start Dev Server**: Runs `npm run dev` automatically before tests
- **Retry**: 2 retries in CI, 0 locally
- **Reporter**: HTML report generated after test runs

### Extending Tests

To add more E2E tests:

1. Create new `.spec.ts` files in `e2e/` directory
2. Follow the pattern in `full-application-flow.spec.ts`
3. Add mock fixtures to `e2e/fixtures/` as needed
4. Use `page.route()` for API interception
5. Use semantic selectors (`getByRole`, `getByLabel`, `getByText`)

### Best Practices

- **Use semantic selectors**: Prefer `getByRole`, `getByLabel` over CSS selectors
- **Mock external APIs**: Use `page.route()` to intercept and mock API calls
- **Test user flows, not implementations**: Focus on end-user behavior
- **Keep tests independent**: Each test should be able to run in isolation
- **Use fixtures for test data**: Centralize mock responses in `fixtures/`

### Debugging

```bash
# Run with UI mode for debugging
npm run test:e2e:ui

# Run in headed mode to see browser
npm run test:e2e:headed

# Generate and view trace
npx playwright show-trace trace.zip
```

### CI/CD Integration

The configuration is CI-ready:
- Auto-detects CI environment (`process.env.CI`)
- Configures retries and parallelization for CI
- Generates HTML reports for test results

## Status: P0 Critical ✅

Both Playwright setup (P0 item 5/7) and Quote Generation Flow E2E test (P0 item 6/7) are complete and ready for use.
