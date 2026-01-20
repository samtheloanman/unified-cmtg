# 🎯 Multi-Agent Sprint: Task Assignments

**Objective**: Working Prototype with Functional UI
**Agents**: Claude Code, Jules, Gemini CLI, Antigravity

---

## 📊 Remaining Tasks (All Sources)

| Task | Complexity | Best Agent |
|------|:----------:|:----------:|
| `GeminiExtractionService` | High | **Claude Code** |
| `IngestionService` (JSON→DB) | Medium | **Claude Code** |
| Quote Form UI (Next.js) | Medium | **Jules** |
| Frontend Styling | Low | **Jules** |
| Rate Sheet Upload UI | Medium | **Jules** |
| Integration Tests | Medium | **Gemini CLI** |
| QuoteView→Real Data | Low | **Antigravity** |
| E2E Demo Prep | Low | **Gemini CLI** |

---

## 🧠 Claude Code - Senior Developer

```markdown
@Claude
**MISSION**: Build the AI Extraction Pipeline (Backend Brain)
**WORKSPACE**: `/home/samalabam/code/unified-cmtg/unified-platform/backend`

### Task 1: GeminiExtractionService
**File**: `ratesheets/services/processors/gemini.py`
**Requirements**:
- Import `google.generativeai` (already installed)
- Read `GOOGLE_API_KEY` from Django settings
- Define extraction prompt with JSON schema
- Parse response, handle errors gracefully

**Schema Example**:
```python
EXTRACTION_SCHEMA = {
    "programs": [{
        "name": str,
        "adjustments": [{
            "min_fico": int, "max_fico": int,
            "min_ltv": float, "max_ltv": float,
            "points": float
        }]
    }]
}
```

### Task 2: IngestionService
**File**: `ratesheets/services/ingestion.py`
**Requirements**:
- Take parsed JSON from Gemini
- Create/Update `LenderProgramOffering` records
- Create `RateAdjustment` records with proper FK links
- Use `transaction.atomic()` for safety

**VERIFICATION**: `docker compose exec backend python manage.py test ratesheets`
```

---

## 🏗️ Jules - Infrastructure & Frontend

```markdown
@Jules
**MISSION**: Build the User Interface
**WORKSPACE**: `/home/samalabam/code/unified-cmtg/unified-platform/frontend`

### Task 1: Quote Calculator Form
**File**: `app/quote/page.tsx`
**UI Components**:
- Input: Loan Amount ($)
- Input: LTV (%)
- Input: FICO Score
- Select: Property Type
- Button: "Get Quote"
- Display: Rate %, Points, APR

### Task 2: Rate Sheet Upload (Admin-like)
**File**: `app/admin/upload/page.tsx`
- File input for PDF
- POST to `/api/v1/ratesheets/upload/`
- Show processing status

### Task 3: Styling
**File**: `app/globals.css`
- Professional mortgage theme
- Dark navy + gold accents
- Mobile responsive

**VERIFICATION**: `npm run build && npm run dev`
```

---

## 🔧 Gemini CLI - Orchestration & QA

```markdown
@Gemini
**MISSION**: Monitor, Test, and Coordinate
**WORKSPACE**: `/home/samalabam/code/unified-cmtg/unified-platform`

### Task 1: Build Monitoring
- Watch: `docker compose logs -f`
- Alert on errors

### Task 2: Integration Tests
After Claude commits:
```bash
docker compose exec backend python manage.py test ratesheets --verbosity=2
```

After Jules commits:
```bash
cd frontend && npm run build
```

### Task 3: Demo Preparation
- Curl examples for Quote API
- Screenshot sequence
- Prepare sample PDFs for upload demo
```

---

## ⚡ Antigravity (Me) - Glue & Quick Fixes

I will:
1. Connect `QuoteView` to real ingested data (after Claude finishes)
2. Fix any integration issues between components
3. Update `conductor` checklist as tasks complete

---

## 🚦 Execution Flow

```
┌─────────────────────────────────────────────────────┐
│  START (Parallel)                                   │
├─────────────────────────────────────────────────────┤
│  Claude Code ──► GeminiService ──► IngestionService │
│  Jules ────────► Quote UI ──────► Upload UI         │
│  Gemini CLI ───► Monitor ────────► Tests            │
├─────────────────────────────────────────────────────┤
│  SYNC POINT: All PRs merged                         │
├─────────────────────────────────────────────────────┤
│  Antigravity ──► Connect QuoteView ──► Final Tests  │
├─────────────────────────────────────────────────────┤
│  DEMO READY                                         │
└─────────────────────────────────────────────────────┘
```
