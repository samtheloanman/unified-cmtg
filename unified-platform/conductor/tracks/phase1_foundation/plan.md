# Phase 1: Foundation & Legacy Verification

> **Goal**: Get legacy apps running locally on dell-brain, verify the existing pricing logic works, then initialize the unified platform stack.

---

## 📋 Task Breakdown

### Task 1.1: Verify Legacy cmtgdirect Runs

**Agent**: QA Tester  
**Priority**: P0 - Critical  
**Estimated Time**: 1-2 hours

#### Context
The cmtgdirect Django application contains the proven loan matching algorithm that we need to preserve. Before building anything new, we must confirm this legacy system still works.

#### Instructions

1. **SSH to dell-brain server**
   ```bash
   ssh dell-brain
   cd ~/code/cmtgdirect
   ```

2. **Review the Docker configuration**
   - Open `docker-compose.yml` and verify service definitions
   - Check for required environment variables in `.env.example`
   - Copy `.env.example` to `.env` if needed

3. **Start the Docker containers**
   ```bash
   docker-compose up -d
   docker-compose ps  # Verify all services are running
   ```

4. **Verify the API responds**
   ```bash
   curl http://localhost:8000/api/v1/health
   # Expected: {"status": "healthy", "version": "1.0.0"}
   ```

5. **Test the QualifyView endpoint**
   ```bash
   curl -X POST http://localhost:8000/api/v1/qualify/ \
     -H "Content-Type: application/json" \
     -d '{
       "property_state": "CA",
       "loan_amount": 500000,
       "credit_score": 720,
       "calculated_ltv": 75,
       "property_type": "residential",
       "loan_purpose": "purchase",
       "occupancy": "primary"
     }'
   ```

6. **Document the results**
   - Record any errors encountered
   - Note the response format from QualifyView
   - Verify LenderProgramOffering records exist in the database

#### Success Criteria
- [x] Docker containers start without errors
- [x] `/api/v1/health` returns 200
- [x] QualifyView returns matching programs
- [x] Database has LenderProgramOffering data
- [x] Superuser created (admin/admin)

---

### Task 1.2: Initialize Unified Platform Backend

**Agent**: Pricing Engineer  
**Priority**: P0 - Critical  
**Estimated Time**: 2-3 hours

#### Context
We need to create a fresh Django + Wagtail project that will eventually replace cmtgdirect. This should follow modern Django best practices with split settings.

#### Instructions

1. **Navigate to unified-platform/backend**
   ```bash
   cd ~/code/unified-cmtg/unified-platform/backend
   ```

2. **Create Django project structure**
   ```bash
   # If using Docker
   docker run --rm -v $(pwd):/app -w /app python:3.11 bash -c "
     pip install django wagtail django-rest-framework
     django-admin startproject config .
     python manage.py startapp api
     python manage.py startapp pricing
     python manage.py startapp cms
     python manage.py startapp ratesheets
   "
   ```

3. **Configure split settings**
   Create the following structure:
   ```
   backend/
   ├── config/
   │   ├── settings/
   │   │   ├── __init__.py
   │   │   ├── base.py      # Shared settings
   │   │   ├── dev.py       # Development settings
   │   │   └── prod.py      # Production settings
   │   ├── urls.py
   │   └── wsgi.py
   ├── api/                  # DRF endpoints
   ├── pricing/              # Loan matching logic
   ├── cms/                  # Wagtail pages
   └── ratesheets/           # Rate ingestion
   ```

4. **Install Wagtail**
   ```bash
   pip install wagtail
   # Add 'wagtail.core', 'wagtail.admin', etc. to INSTALLED_APPS
   ```

5. **Configure Docker**
   Update `Dockerfile` to use Python 3.11 and install all requirements

6. **Verify Django starts**
   ```bash
   docker-compose up backend
   curl http://localhost:8000/admin/
   ```

#### Success Criteria
- [x] Django project structure created
- [x] Split settings configured (base, dev, prod)
- [x] Wagtail installed and configured
- [x] Docker container builds and runs
- [x] `/admin/` returns Wagtail login page
- [x] Superuser created (admin/admin)

---

### Task 1.3: Initialize Next.js Frontend

**Agent**: Frontend Architect  
**Priority**: P1 - High  
**Estimated Time**: 1-2 hours

#### Context
The frontend is already scaffolded with Next.js 14. We need to configure it to fetch data from the Django backend and set up the design system.

#### Instructions

1. **Navigate to frontend directory**
   ```bash
   cd ~/code/unified-cmtg/unified-platform/frontend
   ```

2. **Verify Next.js is working**
   ```bash
   npm install
   npm run dev
   # Visit http://localhost:3000
   ```

3. **Configure API client**
   Create `lib/api.ts`:
   ```typescript
   const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
   
   export async function fetchQuote(params: QuoteParams) {
     const res = await fetch(`${API_BASE}/api/v1/quote/`, {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(params),
     });
     return res.json();
   }
   ```

4. **Set up Tailwind with design tokens**
   Update `tailwind.config.ts` with custom colors matching custommortgageinc.com

5. **Create placeholder components**
   - `components/Header.tsx`
   - `components/Footer.tsx`
   - `components/QuoteWizard.tsx`

#### Success Criteria
- [x] `npm run dev` starts without errors
- [x] API client configured for Django backend
- [x] Tailwind configured with custom theme
- [ ] Placeholder components created

---

### Task 1.4: Verify Frontend ↔ Backend Connectivity

**Agent**: QA Tester  
**Priority**: P0 - Critical  
**Estimated Time**: 30 minutes

#### Context
Before proceeding, we must confirm the Next.js frontend can successfully communicate with the Django backend.

#### Instructions

1. **Start both services**
   ```bash
   cd ~/code/unified-cmtg/unified-platform
   docker-compose up -d
   ```

2. **Configure CORS on Django**
   In `config/settings/base.py`:
   ```python
   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",
   ]
   ```

3. **Test API call from frontend**
   Create a simple test page that calls the health endpoint

4. **Verify in browser console**
   - No CORS errors
   - API response received

#### Success Criteria
- [ ] No CORS errors in browser console
- [ ] Frontend successfully fetches from backend
- [ ] Both services communicate via Docker network

---

## 📊 Progress Tracking

| Task | Status | Blocker | Notes |
|------|--------|---------|-------|
| 1.1 Legacy Verification | ✅ | - | Verified, superuser working (admin/admin) |
| 1.2 Backend Init | ✅ | - | Wagtail running, superuser created |
| 1.3 Frontend Init | ✅ | - | Already scaffolded |
| 1.4 Connectivity | ⏳ | - | Ready to verify |

---

## 🔗 Related Files

- [cmtgdirect docker-compose.yml](file:///home/samalabam/code/cmtgdirect/docker-compose.yml)
- [cmtgdirect api/views.py](file:///home/samalabam/code/cmtgdirect/api/views.py)
- [unified-platform docker-compose.yml](file:///home/samalabam/code/unified-cmtg/unified-platform/docker-compose.yml)

---

*Last Updated: 2026-01-11*
