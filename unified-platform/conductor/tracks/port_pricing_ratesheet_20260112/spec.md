# Track Specification: Port Legacy Pricing Engine & Implement Rate Sheet Ingestion MVP

## 1. Overview

This track aims to establish the foundational backend logic and an initial AI-driven workflow for the Unified CMTG Platform. It involves porting the core loan pricing engine from the legacy `cmtgdirect` application into the new Django backend and developing a Minimum Viable Product (MVP) for automated rate sheet ingestion. This track is crucial for validating the core AI-native capabilities and integrating essential business logic into the new headless architecture.

## 2. Key Objectives

*   Successfully port and integrate the `cmtgdirect` loan pricing models and calculation logic into the new Django/DRF backend.
*   Develop an MVP of the "Rate Sheet Ingestion Agent" to automate the extraction of key data from lender rate sheets.
*   Establish an end-to-end data flow from rate sheet ingestion through the pricing engine to a basic frontend display.
*   Validate the core AI-native and headless architecture principles.

## 3. Scope (In/Out)

### In Scope
*   Migration of `Lender`, `LoanProgram`, and core pricing calculation logic from `cmtgdirect` to `unified-platform/backend/pricing`.
*   Implementation of a new `RateSheet` data model in Django.
*   Development of a service to download and parse PDF rate sheets (initial version will focus on structured PDFs, with placeholder for advanced OCR/LLM).
*   Development of a basic mechanism to extract key rate data and update `LoanProgram` and `RateSheet` related models.
*   A basic API endpoint via DRF to expose loan programs and pricing.
*   A simple Next.js frontend component to demonstrate listing and querying basic loan programs.
*   Integration of Celery/Redis for asynchronous rate sheet processing.
*   Comprehensive unit and integration tests for all ported and new components.

### Out of Scope
*   Full migration of all `cmtgdirect` models or features beyond core pricing.
*   Advanced UI/UX for the rate sheet ingestion process (MVP focuses on core functionality).
*   Full OCR/LLM integration for unstructured PDF parsing (initial focus on structured data, with an architectural placeholder).
*   Frontend features beyond basic loan program display and query.
*   Comprehensive UI for managing lenders or loan programs (initially handled via Django Admin).
*   Any features related to the "Community Forum," "Investment Fund Management," or advanced "Real Estate Services."

## 4. User Stories (High-Level)

*   **As a Loan Officer**, I want the system to automatically ingest and update rates from lender rate sheets so that our pricing is always current.
*   **As a Homebuyer/Borrower**, I want to view available loan programs and get estimated pricing through a modern, fast interface.
*   **As a Developer**, I want the legacy pricing logic to be cleanly integrated into the new, modular backend for easier maintenance and extension.

## 5. Technical Details

*   **Backend Porting:** Focus on `cmtgdirect/loans/queries.py` (`get_matched_loan_programs_for_qual`), `models/programs.py`, `models/program_types.py`.
*   **Rate Sheet Agent:** Will utilize Celery tasks for background PDF processing.
*   **Data Models:** New Django models for `RateSheet` and associated data.
*   **API:** DRF endpoints for `LoanProgram` and basic rate lookup.
*   **Frontend:** Next.js pages/components consuming the new DRF API.

## 6. Success Criteria

*   All specified legacy pricing models and logic are successfully ported and integrated into the new backend.
*   The Rate Sheet Ingestion MVP can process a sample structured PDF rate sheet, extract key data, and update the database.
*   A basic Next.js frontend can query and display ported loan programs with pricing information from the new API.
*   All new and ported components have comprehensive unit and integration tests (target >80% coverage).
*   The workflow adheres to the "Phase Completion Verification and Checkpointing Protocol" defined in `workflow.md`.

## 7. Dependencies

*   Fully configured Docker environment (`docker-compose.yml` operational).
*   Access to sample PDF rate sheets for testing the ingestion agent.
*   Existing `Lender` model (or a basic placeholder) for `LoanProgram` foreign key.
