# 🚀 Agent Prompts - Ready to Copy

Copy each block below into the respective agent's terminal.

---

## 📋 CLAUDE CODE PROMPT

```
You are working on the Unified CMTG Platform - a mortgage pricing engine.

**PROJECT CONTEXT**:
- Workspace: /home/samalabam/code/unified-cmtg/unified-platform
- Backend: Django + Wagtail + Celery
- The `google-generativeai` SDK is already installed
- Settings reads `GOOGLE_API_KEY` from environment

**YOUR MISSION**: Build the AI-powered PDF extraction pipeline

---

### TASK 1: Create GeminiExtractionService

**File**: `backend/ratesheets/services/processors/gemini.py`

**Requirements**:
1. Import `google.generativeai as genai`
2. Read API key from `django.conf.settings.GOOGLE_API_KEY`
3. Create a class `GeminiProcessor` that inherits from `BaseRateSheetProcessor`
4. Implement `process(self, file_path: str) -> dict` method
5. The method should:
   - Read the PDF file
   - Send content to Gemini with this prompt:
   
   ```
   You are a mortgage rate sheet parser. Extract all pricing adjustments from this document.
   Return ONLY valid JSON matching this schema:
   {
     "effective_date": "YYYY-MM-DD",
     "programs": [
       {
         "name": "Program Name",
         "adjustments": [
           {
             "min_fico": 740,
             "max_fico": 759,
             "min_ltv": 0.0,
             "max_ltv": 60.0,
             "adjustment_points": -0.125
           }
         ]
       }
     ]
   }
   If a cell contains "msg" or "contact", set adjustment_points to null.
   ```

6. Parse the JSON response and return it
7. Handle errors gracefully (API failures, parsing errors)

**Reference existing file**: `backend/ratesheets/services/processors/base.py`

---

### TASK 2: Update Ingestion Service

**File**: `backend/ratesheets/services/ingestion.py`

**Current State**: Contains placeholder `update_pricing_from_extraction` function

**Requirements**:
1. Add imports:
   - `from django.db import transaction`
   - `from pricing.models import Lender, LenderProgramOffering, RateAdjustment`
2. Implement real logic in `update_pricing_from_extraction(ratesheet, extracted_data)`:
   - Get or create `LenderProgramOffering` for each program
   - Create `RateAdjustment` records for each adjustment
   - Link to the `RateSheet` via `offering` FK
   - Use `transaction.atomic()` wrapper
   - Return count of records created

---

### TASK 3: Update Celery Task

**File**: `backend/ratesheets/tasks.py`

**Requirements**:
1. Import `GeminiProcessor` from `ratesheets.services.processors.gemini`
2. Import `settings` from `django.conf`
3. In `process_ratesheet` task:
   - Check if `settings.GOOGLE_API_KEY` exists
   - If yes, use `GeminiProcessor`
   - If no, fallback to `PdfPlumberProcessor`
4. Call the real `update_pricing_from_extraction` with results

---

### VERIFICATION

Run these commands to verify:
```bash
docker compose exec backend python manage.py test ratesheets --verbosity=2
```

**CONSTRAINTS**:
- Do NOT modify frontend code
- Do NOT modify models (they are complete)
- Commit after each task with descriptive message
- If you encounter errors, fix them before proceeding
```

---

## 📋 JULES PROMPT

```
You are working on the Unified CMTG Platform - a mortgage pricing engine.

**PROJECT CONTEXT**:
- Workspace: /home/samalabam/code/unified-cmtg/unified-platform
- Frontend: Next.js (in `frontend/` directory)
- Backend API: Django REST at `http://localhost:8000/api/v1/`
- Goal: Build a professional mortgage calculator UI

**YOUR MISSION**: Build the User Interface

---

### TASK 1: Quote Calculator Form

**File**: `frontend/app/quote/page.tsx`

**Create a form with**:
1. **Inputs**:
   - Loan Amount (number, formatted as currency)
   - LTV Percentage (number, 0-100)
   - FICO Score (number, 300-850)
   - Property Type (dropdown: Single Family, Condo, Multi-Family, Townhouse)
   - Loan Purpose (dropdown: Purchase, Refinance, Cash-Out)

2. **Submit Button**: "Calculate Quote"

3. **API Call on Submit**:
   ```javascript
   const response = await fetch('http://localhost:8000/api/v1/quote/', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       loan_amount: loanAmount,
       ltv: ltv / 100,
       fico_score: ficoScore,
       property_type: propertyType,
       purpose: loanPurpose
     })
   });
   ```

4. **Display Results**:
   - Interest Rate (%)
   - Points/Credits
   - APR
   - Monthly Payment estimate

5. **States**: Loading spinner, Error message display

---

### TASK 2: Global Styling

**File**: `frontend/app/globals.css`

**Theme Requirements**:
- Primary: Navy Blue (#1a365d)
- Accent: Gold (#d4af37)
- Background: Dark (#0f172a)
- Text: White/Light Gray
- Cards: Slightly lighter dark (#1e293b)
- Inputs: Dark with light borders
- Buttons: Gold with navy text

**Typography**:
- Font: Inter or system-ui
- Headings: Bold, slightly larger
- Professional, trustworthy feel

**Layout**:
- Centered card on dark background
- Max-width 600px for the form
- Mobile responsive

---

### TASK 3: Rate Sheet Upload Page (Optional if time permits)

**File**: `frontend/app/admin/upload/page.tsx`

**Simple upload form**:
1. File input (accept=".pdf")
2. Lender name input
3. Submit to `/api/v1/ratesheets/upload/`
4. Show success/error status

---

### VERIFICATION

```bash
cd frontend
npm install
npm run build
npm run dev
```

Visit http://localhost:3000/quote and verify the form renders.

**CONSTRAINTS**:
- Do NOT modify backend code
- Use fetch() for API calls, not axios
- Ensure all TypeScript types are correct
- No external UI libraries unless already installed
```

---

## 📋 GEMINI CLI PROMPT

```
You are the Orchestrator for the Unified CMTG Platform build.

**PROJECT CONTEXT**:
- Workspace: /home/samalabam/code/unified-cmtg/unified-platform
- Docker Compose manages: backend, db, redis, frontend
- Other agents (Claude, Jules) are working in parallel

**YOUR MISSION**: Monitor, Test, and Coordinate

---

### TASK 1: Monitor Docker Services

Run and watch for errors:
```bash
cd /home/samalabam/code/unified-cmtg/unified-platform
docker compose logs -f backend
```

Alert if you see:
- ImportError
- ModuleNotFoundError
- Database connection errors
- Redis connection errors

---

### TASK 2: Run Backend Tests (After Claude Commits)

```bash
docker compose exec backend python manage.py test ratesheets --verbosity=2
```

Expected: All tests pass
If failures:
1. Read the error
2. Identify which file is broken
3. Report back with specific fix needed

---

### TASK 3: Verify Frontend Build (After Jules Commits)

```bash
cd frontend
npm install
npm run build
```

Expected: Build succeeds with no TypeScript errors
If failures:
1. Read the error
2. Identify the line/file
3. Report back

---

### TASK 4: Integration Smoke Test

After both agents complete, run:

```bash
# Test Quote API
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{"loan_amount": 500000, "ltv": 0.8, "fico_score": 740, "property_type": "single_family", "purpose": "purchase"}'

# Check Django Admin
echo "Visit http://localhost:8000/admin/ (user: admin, pass: check .env)"
```

---

### TASK 5: Demo Preparation

Create a demo script:
1. List all curl commands
2. Screenshot the Quote form
3. List sample PDFs to upload
4. Document the full flow

---

**CONSTRAINTS**:
- Do NOT edit code directly (that's Claude's and Jules's job)
- Focus on monitoring and testing
- Report issues clearly with file paths and line numbers
- Update the conductor checklist when tasks complete
```

---

## 📋 ANTIGRAVITY PROMPT (For Me)

```
Continue the Unified CMTG sprint.

**YOUR TASK**: QuoteView Integration

After Claude finishes the GeminiProcessor and IngestionService:

1. Update `backend/api/views.py` QuoteView:
   - Instead of returning mock data, query real `RateAdjustment` records
   - Filter by FICO range and LTV range from request
   - Return actual rate/points from database

2. Update conductor checklist as tasks complete

3. Fix any integration issues between components

4. Prepare final commit with all changes
```

---

# ✅ Copy Order

1. **First**: Claude Code prompt (critical path)
2. **Second**: Jules prompt (parallel)
3. **Third**: Gemini CLI prompt (monitoring)
4. **Antigravity**: I'll start automatically after dependencies are ready
