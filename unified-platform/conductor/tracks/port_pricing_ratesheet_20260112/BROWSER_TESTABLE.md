# 🎯 Track Update: Browser-Testable MVP

**Track ID**: `port_pricing_ratesheet_20260112`
**Updated**: 2026-01-13 12:05 PST
**Goal**: Get the mortgage quote form working in browser at localhost:3001

---

## 🔑 Google API Recommendation

**Use: Gemini API via Google AI Studio** (your current key works!)

| Option | Best For | Our Use Case |
|--------|----------|--------------|
| **AI Studio API** ✅ | Simple integration, PDF extraction | ✅ Perfect fit |
| Vertex AI | Enterprise, custom models | Overkill |
| Document AI | Structured forms (invoices) | Not needed |

**Why Gemini AI Studio:**
- Handles visually complex PDFs (rate sheets with tables, charts)
- 30-50% cheaper than Document AI
- Simple API integration (already coded in `gemini_ai.py`)
- Up to 50MB PDF / 1000 pages

---

## 🚧 Current Blockers

| Issue | Status | Fix |
|-------|--------|-----|
| Frontend shows default page | 🔴 | Create `/quote` route OR merge Jules PR |
| `/api/v1/quote/` returns 404 | 🔴 | Fix URL routing |
| GOOGLE_API_KEY not set | 🟡 | Add to `.env` |
| `httpx` missing | 🟡 | Add to requirements |

---

## 📋 Phase 3.5: Browser-Testable (UPDATED)

### Option A: Quick Fix (Recommended - 30 min)

**Agent: Antigravity (me)**

1. **Fix URL Routing** - Add `/quote` directly to `config/urls.py`
2. **Create Quote Page** - Add `frontend/src/app/quote/page.tsx`
3. **Set Google API Key** - Add to docker-compose.yml
4. **Add httpx** - Add to requirements.txt

### Option B: Merge Jules PR (1 hour)

**Agent: Claude Code**

1. Merge `origin/jules/phase1-foundation-10297780927730413954`
2. Resolve 11 file conflicts
3. Rebuild containers
4. Run tests

---

## 🎯 V1 Requirements (From PRD)

| Feature | Status | Needed For Browser Test |
|---------|--------|------------------------|
| Quote Calculator Form | ❌ Missing | **YES** |
| Display matching programs | ✅ Backend ready | YES |
| Rate adjustments by FICO/LTV | ✅ Backend ready | YES |
| PDF Upload | ❌ Missing | No (Phase 4) |
| Gemini AI Extraction | ✅ Backend ready | No (Phase 4) |

---

## 🏃 Immediate Actions (For Browser Test)

### 1. Fix Backend URL (5 min)
```python
# Add to config/urls.py:
from api.views import QuoteView
path("api/v1/quote/", QuoteView.as_view(), name="quote"),
```

### 2. Create Frontend Quote Page (15 min)
```bash
# Create frontend/src/app/quote/page.tsx
# See Jules PR for reference UI
```

### 3. Set Google API Key (2 min)
```yaml
# In docker-compose.yml under backend environment:
GOOGLE_API_KEY: "your-ai-studio-key"
```

### 4. Rebuild and Test (5 min)
```bash
docker compose up -d --build
curl http://localhost:8000/api/v1/quote/ -X POST -H "Content-Type: application/json" -d '{"property_state":"CA","loan_amount":500000,"credit_score":740,"property_value":650000}'
# Open http://localhost:3001/quote
```

---

## ✅ Success Criteria

- [ ] http://localhost:3001/quote shows quote form
- [ ] Form submits and displays results
- [ ] http://localhost:8000/api/v1/quote/ returns JSON
- [ ] All tests pass
