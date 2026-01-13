# Agent Prompts - Phase 3: Rate Sheet Ingestion

## 🚀 Phase 2 Complete - Moving to Phase 3
Phase 2 (Pricing Engine Port) is fully complete. The Quote API is live and verified.
We are now starting **Phase 3: Automated Rate Sheet Ingestion**.

---

## 🏗️ Prompt for Jules (Infrastructure & Celery)

```
# MISSION: Setup RateSheet Infrastructure & Celery
# ROLE: The Builder
# PHASE: 3.1 - Infrastructure

# CONTEXT:
We need to ingest PDF rate sheets asynchronously.
The `ratesheets` app exists but is empty.
Redis is already running (verified in Phase 1).

# TASKS:

## 1. Configure Celery (if not fully configured)
- Check `config/settings/base.py` and `config/settings/dev.py` for CELERY_BROKER_URL.
- Ensure `config/celery.py` exists and is configured for Django.
- Update `ratesheets/apps.py` to importing signals if needed.

## 2. Define RateSheet Model
Edit `ratesheets/models.py`:
- Class `RateSheet(TimestampedModel)`
- Fields:
  - `lender`: ForeignKey to `pricing.Lender`
  - `name`: CharField (e.g., "Angel Oak DSCR Jan 2026")
  - `file`: FileField (upload_to='rate_sheets/%Y/%m/')
  - `status`: CharField (choices: PENDING, PROCESSING, PROCESSED, FAILED)
  - `processed_at`: DateTimeField(null=True)
  - `log`: TextField(blank=True) # captured stdout/stderr from processing

## 3. Create Celery Task
Edit `ratesheets/tasks.py`:
- Create `process_ratesheet(ratesheet_id)` task.
- Logic:
  1. Get RateSheet by ID.
  2. Set status = PROCESSING.
  3. (Placeholder) Call `RateSheetProcessor.process(ratesheet)` (Claude will implement).
  4. On success: Set status = PROCESSED, update processed_at.
  5. On error: Set status = FAILED, save stack trace to `log`.

## 4. Register in Admin
Edit `ratesheets/admin.py`:
- Register `RateSheet` model.
- Add action "Reprocess selected rate sheets".

# SUCCESS CRITERIA:
- [ ] `makemigrations` and `migrate` run successfully.
- [ ] RateSheet model visible in Django Admin.
- [ ] Celery worker starts without errors: `docker compose exec backend celery -A config worker -l info`
```

---

## 🧠 Prompt for Claude (Processor Implementation)

```
# MISSION: Implement Rate Sheet Processors
# ROLE: The Generator
# PHASE: 3.2 - Processing Logic

# CONTEXT:
Jules has set up the `RateSheet` model and Celery task structure.
We need the actual logic to extract data from PDF files.

# TASKS:

## 1. Create Processor Interface
Create `ratesheets/services/processors/base.py`:
- Class `BaseRateSheetProcessor`.
- Method `process(self, ratesheet_instance) -> Dict`:
    - Abstract method.
    - Should return extracted data structure (program names, adjustments, etc.).

## 2. Implement PDF Processor
Create `ratesheets/services/processors/pdf_plumber.py`:
- Use `pdfplumber` (add to requirements if needed).
- Class `PdfPlumberProcessor(BaseRateSheetProcessor)`.
- Logic:
    - Open PDF from `ratesheet.file`.
    - Extract text/tables.
    - (MVP) Log extracted text to console for now.
    - (Future) Parse specific tables into `RateAdjustment` objects.

## 3. Implement Rate Adjustment Updater
Create `ratesheets/services/ingestion.py`:
- Function `update_pricing_from_extraction(lender, data)`:
    - Take extracted data.
    - Create/Update `RateAdjustment` records.

# SUCCESS CRITERIA:
- [ ] `BaseRateSheetProcessor` defined.
- [ ] `PdfPlumberProcessor` can read a uploaded PDF.
- [ ] `process_ratesheet` task successfully delegates to processor.
```

---

## 🧪 Prompt for Ralph (Testing)

```
# MISSION: Test Rate Sheet Ingestion
# ROLE: The Closer (QA)
# PHASE: 3.3 - Verification

# CONTEXT:
Models and Processors are being built. We need to ensure the pipeline is robust.

# TASKS:

## 1. Test RateSheet Model
Create `ratesheets/tests/test_models.py`:
- Test creation.
- Test status defaults.

## 2. Test Celery Integration
Create `ratesheets/tests/test_tasks.py`:
- Mock the actual processor (we don't want to parse real PDFs in unit tests).
- Verify calling `process_ratesheet` updates the status to PROCESSING then PROCESSED.
- Verify error handling updates status to FAILED.

## 3. Integration Test
Create `ratesheets/tests/test_integration.py`:
- Create a dummy PDF file in test setup.
- Upload via `RateSheet.objects.create`.
- Run task synchronously (`process_ratesheet.apply(args=[rs.id])`).
- Assert final status is PROCESSED.

# SUCCESS CRITERIA:
- [ ] `python manage.py test ratesheets` passes.
```

---

## 📋 Execution Order
1. **Jules**: Phase 3.1 (Infra/Models)
2. **Claude**: Phase 3.2 (Processors)
3. **Ralph**: Phase 3.3 (Tests)
