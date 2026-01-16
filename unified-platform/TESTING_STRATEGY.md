# Comprehensive Testing Strategy & System Audit

## 1. System Components Inventory

### Frontend (`unified-platform/frontend`)
*   **Stack**: Next.js 16 (App Router), React 19, Tailwind CSS v4.
*   **Key Routes**:
    *   `/quote` - Mortgage Calculator & Lead Gen Form.
    *   `/[...slug]` - Dynamic CMS Page Renderer (Programs, Blogs).
    *   `/admin/upload` - Rate Sheet Upload Interface.
    *   `/test` - Internal testing/debug route.
*   **Key Components**:
    *   `Calculator` (Mortgage math logic).
    *   `QuoteForm` (Lead submission).
    *   `CMSRenderer` (Wagtail content block rendering).

### Backend (`unified-platform/backend`)
*   **Stack**: Django 5, Wagtail 6, Django REST Framework.
*   **Apps**:
    *   `api`:
        *   `views.QuoteView`: Pricing engine orchestration.
        *   `views.LeadSubmitView`: Floify integration.
        *   `views.floify_webhook`: Webhook handling.
    *   `cms`:
        *   Models: `ProgramPage` (64 fields), `FundedLoanPage`, `BlogPage`.
        *   API: Wagtail v2 API (`/api/v2/pages/`).
    *   `pricing`:
        *   Models: `Lender`, `ProgramType`, `RateAdjustment`.
        *   Service: `LoanMatchingService` (Core pricing logic).
    *   `ratesheets`:
        *   Ingestion Pipeline: PDF Downloader -> Text Extraction -> Gemini Parsing -> Database.
*   **Infrastructure**:
    *   Celery + Redis (Async tasks for ingestion).
    *   PostgreSQL (Production) / SQLite (Dev).

---

## 2. Comprehensive Testing Suite Plan

### Layer 1: Backend Unit & Service Tests
*   **Goal**: Verify core business logic independent of HTTP or UI.
*   **Tools**: `pytest`, `pytest-django`, `factory_boy`.
*   **Scope**:
    *   **Pricing Engine**: Verify `LoanMatchingService` correctly filters programs and calculates rates based on inputs (FICO, LTV, Loan Amount).
    *   **CMS Models**: Verify `ProgramPage` field constraints, tab configurations, and custom methods.
    *   **Rate Sheets**: Test parsers with mock PDF text.

### Layer 2: Backend Integration Tests
*   **Goal**: Verify data flow between components and external services (mocked).
*   **Tools**: `pytest`, `requests-mock`.
*   **Scope**:
    *   **API Endpoints**: Test `/api/v1/quote/` returns correct JSON structure and status codes.
    *   **Wagtail API**: Verify `/api/v2/pages/` returns all custom API fields (e.g., `program_details`).
    *   **Floify Integration**: Mock Floify API to verify lead payload formatting.
    *   **Celery**: Test task queuing and execution logic (using `CELERY_TASK_ALWAYS_EAGER`).

### Layer 3: Frontend Component Tests
*   **Goal**: Verify UI logic and rendering.
*   **Tools**: `Vitest` (faster than Jest), `React Testing Library`.
*   **Scope**:
    *   **Calculator**: Verify math output updates when inputs change.
    *   **Forms**: Test validation logic (required fields, regex).
    *   **CMS Components**: Verify correct rendering of StreamField blocks.

### Layer 4: End-to-End (E2E) Tests
*   **Goal**: Verify critical user journeys across the full stack.
*   **Tools**: `Playwright`.
*   **Scope**:
    *   **Get a Quote**: User lands on `/quote` -> fills form -> sees results -> submits lead.
    *   **View Program**: User navigates to `/programs/dscr` -> sees correctly rendered CMS data.
    *   **Admin Upload**: Admin logs in -> uploads rate sheet -> checks status.

---

## 3. Top 20 "To-Do" List (Prioritized)

### P0: Critical Infrastructure & Logic (High Risk)
1.  **Setup Pytest Framework**: Configure `pytest.ini` and `conftest.py` for Django.
2.  **Test Pricing Engine Logic**: Write rigorous unit tests for `LoanMatchingService` (edge cases: boundary FICO, LTV limits).
3.  **Test Wagtail API Output**: Ensure `ProgramPage` exposes all 64 fields correctly via `/api/v2/pages/` (headless requirement).
4.  **Setup Playwright**: Initialize E2E framework in `frontend/e2e`.
5.  **E2E: Quote Generation Flow**: automate the "Get a Quote" user journey.
6.  **Test Floify Integration**: Verify lead submission does not fail silently (mock API).
7.  **Rate Sheet Ingestion Mock**: Test the pipeline with a static text fixture (avoid calling Gemini API in tests).

### P1: Frontend Stability & UX
8.  **Setup Vitest for Next.js**: Configure test runner for React components.
9.  **Test Mortgage Calculator**: Unit test the JS math logic in the frontend component.
10. **Test Quote Form Validation**: Ensure users can't submit invalid data (e.g., negative loan amounts).
11. **E2E: Dynamic Page Rendering**: Verify `[...slug]` routes load content from Django backend without errors.
12. **Mobile Responsiveness Test**: Use Playwright to screenshot critical pages on mobile viewports.

### P2: Backend Robustness
13. **Test Celery Task Execution**: Ensure async tasks (ingestion) can be triggered and tracked.
14. **Test Database Migrations**: CI step to check `makemigrations --check` (ensure no missing migrations).
15. **Secure API Endpoints**: specific tests for Auth/Permissions on Admin API routes.
16. **Test Error Handling**: Verify 404/500 pages render correctly on Frontend and Backend.

### P3: DevOps & Maintenance
17. **CI/CD Pipeline**: Create GitHub Action to run Pytest + Vitest on PRs.
18. **Linting & Formatting**: Enforce `flake8` (Backend) and `eslint/prettier` (Frontend).
19. **Test SEO Meta Tags**: Verify dynamic pages render correct `meta` tags (Critical for Programmatic SEO).
20. **Redis Connection Test**: Simple health check test for Cache/Broker connectivity.
