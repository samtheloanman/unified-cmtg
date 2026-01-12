# AI-Native Unified Mortgage Platform - Implementation Plan

## Goal
Build unified Django+Wagtail platform on `cmre.c-mtg.com`, then cut over to `custommortgageinc.com` with 1:1 URL parity.

---

## Key Decisions (From Redteam)

> [!IMPORTANT]
> **Quote Engine**: Reuse existing `QualifyingFormWizard` from `cmtgdirect`. Skin with Tailwind.

> [!IMPORTANT]
> **Floify Workflow**: Push leads via `POST /prospects`. Floify emails the applicant. Webhook syncs data back to Django.

> [!TIP]
> **Ratesheet Agent**: Priority feature. Browser agent + OCR/LLM to extract rates from lender PDFs.

---

## Existing Assets (cmtgdirect)

| Asset | Location | Reuse |
|-------|----------|-------|
| `QualifyingFormWizard` | `loans/views.py` | ✅ Quote Engine |
| `QualifyView` API | `api/views.py` | ✅ Program matching |
| `LenderProgramOffering` | `loans/models/program_types.py` | ✅ Rate storage |
| `ProgramType` | `loans/models/program_types.py` | ✅ Canonical programs |
| Floify webhook | `api/views.py` | ⚠️ Placeholder, needs work |

---

## Implementation Chunks

### Chunk 1: Project Setup (Day 1-2)
- Create `cmre/` unified project
- Install Wagtail
- Configure Docker Compose
- Copy loans, api apps from cmtgdirect

### Chunk 2: Content Migration (Day 3-5)
- WP REST API extractor for programs, blogs, locations
- Import to Wagtail with matching slugs
- Migrate user-uploaded media only

### Chunk 3: Quote Engine Port (Day 6-8)
- Port `QualifyingFormWizard` and forms
- **Integrate HTMX**: Use hx-taret/hx-swap for SPA-like transitions without full reloads
- Skin with Tailwind CSS
- Create headless API endpoints (backup)

### Chunk 4: Floify Integration (Day 9-11)
- Implement `POST /prospects` in chatbot flow
- Build complete `floify_webhook` handler
- Sync 1003 JSON to local `Application` model
- Create Borrower Dashboard

### Chunk 5: Ratesheet Agent (Day 12-16)
- **Email Ingestion**: Setup Zoho alias listener + Allowlist (known lender domains only)
- Browser agent to visit URLs and download PDFs
- OCR + LLM extraction to JSON (with Confidence Scores)
- **Validation UI**: Admin view showing "Yesterday vs Today" diffs (Force manual approval if >0.25% variance)
- Sync to `LenderProgramOffering` model
- Create `RateAdjustment` model for LLPAs

### Chunk 6: Chatbot & Polish (Day 17-20)
- Integrate Gemini chatbot widget
- Connect lead capture to Floify prospects
- Final UI polish
- Deploy to cmre.c-mtg.com

---

## Proposed New Model

```python
class RateAdjustment(TimestampedModel):
    """
    Loan Level Price Adjustments (LLPAs) from rate sheets.
    """
    offering = ForeignKey(LenderProgramOffering, related_name='adjustments')
    adjustment_type = CharField(choices=[
        ('fico', 'Credit Score'),
        ('ltv', 'Loan-to-Value'),
        ('property_type', 'Property Type'),
        ('purpose', 'Loan Purpose'),
        ('lock_period', 'Lock Period'),
    ])
    min_value = FloatField()
    max_value = FloatField()
    adjustment_bps = IntegerField(help_text="Basis points, e.g. +25")
```

---

## Verification Plan

### Automated Tests
```bash
pytest apps/loans/tests/
pytest apps/applications/tests/
pytest apps/ratesheets/tests/  # New extraction tests
python manage.py verify_migration --compare-urls
```

### Browser/Manual
- Quote wizard completes successfully (HTMX transitions smooth)
- Floify prospect created and email received
- Ratesheet agent extracts rates (Diff View correctly flags changes)

---

## Next Steps
1. Approve this plan
2. Start Chunk 1: Project Setup
