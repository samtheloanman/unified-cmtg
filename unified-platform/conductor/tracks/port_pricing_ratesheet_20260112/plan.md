# Track Plan: Port Legacy Pricing Engine & Implement Rate Sheet Ingestion MVP

## Track ID: `port_pricing_ratesheet_20260112`

This plan details the phases and tasks required to port the legacy pricing engine and implement the MVP for the rate sheet ingestion agent, as per the track specification.

---

## Phase 1: Environment Setup & Legacy Code Analysis

**Objective:** Prepare the new development environment and thoroughly understand the legacy `cmtgdirect` pricing codebase.

*   [ ] Task: Jules - Set up core Django/Wagtail backend project in `unified-platform/backend/`.
    *   **Action:** Ensure `manage.py`, `config/settings.py`, `config/urls.py` are correctly configured for a new Django project.
    *   **Verification:** Django development server runs successfully, and Wagtail admin is accessible.
*   [ ] Task: Jules - Set up Next.js frontend project in `unified-platform/frontend/`.
    *   **Action:** Initialize a new Next.js project with TypeScript and Tailwind CSS (if not already done).
    *   **Verification:** Next.js development server runs successfully, and basic page renders.
*   [ ] Task: Claude - Copy legacy `cmtgdirect` to `unified-platform/backend/legacy_cmtgdirect/`.
    *   **Action:** Copy the entire `cmtgdirect` repository into the specified directory.
    *   **Verification:** Directory exists and contains all legacy files.
*   [ ] Task: Claude - Analyze legacy pricing logic for `Lender` and `LoanProgram` in `legacy_cmtgdirect/loans/models/programs.py`.
    *   **Action:** Use "Legacy Code Mapping Translator" skill to document current model structure, relationships, and data types.
    *   **Verification:** Detailed `legacy_cmtgdirect_pricing_models_analysis.md` created in track context.
*   [ ] Task: Claude - Analyze legacy pricing logic for core calculations in `legacy_cmtgdirect/loans/queries.py` and `api/views.py`.
    *   **Action:** Use "Legacy Code Mapping Translator" skill to document core logic, inputs, outputs, and dependencies of `get_matched_loan_programs_for_qual()`.
    *   **Verification:** Detailed `legacy_cmtgdirect_pricing_logic_analysis.md` created in track context.
*   [ ] Task: Conductor - Manual Verification: Review Phase 1 completion and analysis documents. (Protocol in workflow.md)

---

## Phase 2: Pricing Engine Porting - Core Models & Logic

**Objective:** Port the essential `Lender` and `LoanProgram` models and core pricing logic into the new `unified-platform/backend` structure.

*   [ ] Task: Claude - Generate `Lender` model in `unified-platform/backend/pricing/models.py`.
    *   **Action:** Based on `legacy_cmtgdirect_pricing_models_analysis.md` and current project conventions, generate the `Lender` model.
    *   **Verification:** `Lender` model file exists and passes basic `makemigrations`.
*   [ ] Task: Claude - Generate `LoanProgram` model in `unified-platform/backend/pricing/models.py`.
    *   **Action:** Based on `legacy_cmtgdirect_pricing_models_analysis.md` and current project conventions (including Wagtail `Page` inheritance), generate the `LoanProgram` model.
    *   **Verification:** `LoanProgram` model file exists and passes basic `makemigrations`.
*   [ ] Task: Ralph - Implement unit tests for `Lender` and `LoanProgram` models.
    *   **Action:** Create tests to verify field integrity, relationships, and basic query methods.
    *   **Verification:** Tests are created and pass.
*   [ ] Task: Claude - Port core pricing calculation logic.
    *   **Action:** Translate `get_matched_loan_programs_for_qual()` logic into a new service or model method within `unified-platform/backend/pricing/`.
    *   **Verification:** Logic is present in the new backend.
*   [ ] Task: Ralph - Implement unit tests for ported pricing logic.
    *   **Action:** Create tests replicating key scenarios from legacy system to verify ported logic's correctness.
    *   **Verification:** Tests are created and pass, demonstrating functional equivalence.
*   [ ] Task: Claude - Integrate ported pricing logic into new DRF API.
    *   **Action:** Generate basic DRF Serializers and ViewSets for `Lender` and `LoanProgram` to expose them via API.
    *   **Verification:** API endpoints exist and return model data.
*   [ ] Task: Conductor - Automated Verification: Run integration tests for 'Pricing Engine Porting' phase. (Protocol in workflow.md)
    *   **Action:** Ralph runs integration tests covering API endpoints and pricing calculations.
    *   **Verification:** All integration tests pass.

---

## Phase 3: Rate Sheet Ingestion Agent - MVP

**Objective:** Build the MVP for automated rate sheet ingestion, including data models and initial processing.

*   [ ] Task: Claude - Generate `RateSheet` and `RateAdjustment` data models.
    *   **Action:** Define models in `unified-platform/backend/ratesheets/models.py` based on `rate_extraction_field_mapping.md` (from `knowledge-base/`).
    *   **Verification:** Models exist and pass basic `makemigrations`.
*   [ ] Task: Ralph - Implement unit tests for `RateSheet` and `RateAdjustment` models.
    *   **Action:** Create tests to verify field integrity and relationships.
    *   **Verification:** Tests are created and pass.
*   [ ] Task: Jules - Configure Celery and Redis for asynchronous tasks.
    *   **Action:** Ensure `celery` and `redis` are integrated into `unified-platform/backend`'s Docker setup and Django settings.
    *   **Verification:** A basic Celery task can be defined and executed successfully.
*   [ ] Task: Claude - Develop basic PDF download and parsing service.
    *   **Action:** Implement a Celery task that can download a PDF from a URL and perform initial text extraction (using a simple library like `PyPDF2` or `pdfminer.six` for MVP, not full OCR/LLM yet).
    *   **Verification:** Service can successfully extract text from a sample PDF rate sheet.
*   [ ] Task: Claude - Develop basic data extraction to `RateSheet` models.
    *   **Action:** Implement logic within the Celery task to parse the extracted text and map it to `RateSheet` and `RateAdjustment` model fields.
    *   **Verification:** A sample PDF ingestion successfully populates the database.
*   [ ] Task: Claude - Integrate Rate Sheet ingestion with `LoanProgram` model.
    *   **Action:** Establish ManyToMany relationship between `LoanProgram` and `RateSheet` models via `RateSheetProgram` (if not already done).
    *   **Verification:** Relationship is established and testable.
*   [ ] Task: Conductor - Automated Verification: Run integration tests for 'Rate Sheet Ingestion MVP' phase. (Protocol in workflow.md)
    *   **Action:** Ralph runs integration tests for the full ingestion pipeline: download -> parse -> extract -> save.
    *   **Verification:** All integration tests pass.

---

## Phase 4: Frontend Integration & MVP Demonstration

**Objective:** Integrate the frontend with the new backend APIs and demonstrate the end-to-end MVP.

*   [ ] Task: Claude - Build Next.js components to display loan programs.
    *   **Action:** Create a simple page and components in `unified-platform/frontend/` to fetch and display a list of `LoanProgram` instances from the new API.
    *   **Verification:** Frontend page loads and shows loan program data.
*   [ ] Task: Claude - Connect frontend to new pricing API.
    *   **Action:** Implement data fetching logic in Next.js to call the DRF API for loan program data.
    *   **Verification:** Frontend successfully retrieves and displays data from the backend API.
*   [ ] Task: Claude - Develop basic UI for rate sheet ingestion/review (manual upload for MVP).
    *   **Action:** Create a simple frontend form to trigger the Celery task for rate sheet ingestion by providing a PDF URL.
    *   **Verification:** Form functions, and ingestion task is initiated successfully.
*   [ ] Task: Conductor - Manual Verification: Review End-to-End MVP Functionality. (Protocol in workflow.md)
    *   **Action:** L1 Orchestrator presents the running MVP application for user review.
    *   **Verification:** The user confirms that the MVP meets the specified criteria: Homebuyer can view loan programs, and an LO can trigger basic rate sheet ingestion.

---
