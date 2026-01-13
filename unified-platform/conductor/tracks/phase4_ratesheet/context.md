# Phase 4: Rate Sheet Agent - Context

## Goal
Automate the ingestion of lender rate sheets (PDFs) into structured data.

## Source Data
- `Ratesheet List - Ratesheets.csv`: Contains lender names and URLs.
- Lender Websites: PDFs are hosted on various lender sites.

## Components
1. **Ingestion**: Read CSV, Download PDF.
2. **Extraction**: Gemini 1.5 Pro (Vision) -> JSON.
3. **Staging**: `RateSheetImport` model for human review.
4. **Publishing**: `LenderProgramOffering` update.
