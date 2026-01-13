# 🏗️ Jules Emergency Sprint: Get Project Browser-Testable

**Priority**: CRITICAL
**Goal**: Make the Unified CMTG Platform fully testable in a browser within 1 hour
**Repository**: `git pull origin main` first to get latest code

---

## 📋 CONTEXT

The backend and frontend have been built by multiple agents. We need you to:
1. Fix a URL routing issue preventing the Quote API from working
2. Ensure the frontend builds and runs
3. Verify the full stack is accessible via browser
4. Create seed data so there's something to see

---

## 🔧 TASK 1: Fix API URL Routing (CRITICAL)

**Problem**: The `/api/v1/quote/` endpoint returns 404, but `/api/v1/qualify/` works.

**Investigation Steps**:
```bash
cd /home/samalabam/code/unified-cmtg/unified-platform
docker compose exec backend python manage.py show_urls | grep -E "(quote|qualify)"
```

**Likely Cause**: There are multiple URL configurations. The `api/urls.py` has:
```python
path('quote/', views.QuoteView.as_view(), name='quote'),
```

But Django isn't loading it. Check these files:
1. `backend/config/urls.py` - Main URL config
2. `backend/api/urls.py` - API routes
3. Look for any other `urls.py` that includes `api.urls`

**Fix Options**:
- Option A: Ensure `api.urls` is included BEFORE any catch-all routes
- Option B: Add the quote endpoint directly to the working URL pattern
- Option C: Merge the two URL configurations

**Verification**:
```bash
curl -X POST http://localhost:8000/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{"property_state":"CA","loan_amount":500000,"credit_score":740,"property_value":650000}'
```

Expected: JSON response with quotes (even if empty array)

---

## 🎨 TASK 2: Frontend Setup & Build

**Directory**: `unified-platform/frontend/`

**Steps**:
```bash
cd /home/samalabam/code/unified-cmtg/unified-platform/frontend

# Install dependencies
npm install

# Check for TypeScript errors
npm run build

# If build fails, fix the errors

# Start dev server
npm run dev
```

**Common Issues**:
1. Missing dependencies → Run `npm install`
2. TypeScript errors → Check the error messages, fix type issues
3. API URL mismatch → Check `src/lib/api.ts` or similar for the backend URL

**Expected Result**: Frontend accessible at http://localhost:3000

---

## 🗃️ TASK 3: Database Migrations & Seed Data

**Ensure all migrations are applied**:
```bash
docker compose exec backend python manage.py migrate
```

**Create a superuser for admin access**:
```bash
docker compose exec backend python manage.py createsuperuser
# Use: admin / admin@example.com / adminpass123
```

**Create seed data** (so there's something to see):

Create file `backend/pricing/management/commands/seed_data.py`:
```python
from django.core.management.base import BaseCommand
from pricing.models import Lender, ProgramType, LenderProgramOffering, RateAdjustment

class Command(BaseCommand):
    help = 'Seed initial pricing data'

    def handle(self, *args, **options):
        # Create a lender
        lender, _ = Lender.objects.get_or_create(
            company_name="Acra Lending",
            defaults={
                'include_states': ['CA', 'TX', 'FL', 'NY', 'AZ'],
                'is_active': True
            }
        )
        self.stdout.write(f"Created lender: {lender.company_name}")

        # Create a program type
        program, _ = ProgramType.objects.get_or_create(
            name="DSCR 30-Year Fixed",
            defaults={
                'category': 'non_qm',
                'loan_type': 'dscr',
                'property_types': ['residential', 'multi_family'],
                'entity_types': ['individual', 'llc'],
                'purposes': ['purchase', 'refinance'],
                'occupancy': ['investment'],
                'base_min_fico': 660,
                'base_max_ltv': 80.0
            }
        )
        self.stdout.write(f"Created program: {program.name}")

        # Create offering
        offering, _ = LenderProgramOffering.objects.get_or_create(
            lender=lender,
            program_type=program,
            defaults={
                'min_rate': 7.25,
                'max_rate': 8.50,
                'min_points': 0,
                'max_points': 2,
                'min_fico': 660,
                'max_ltv': 80.0,
                'min_loan': 75000,
                'max_loan': 2000000,
                'is_active': True
            }
        )
        self.stdout.write(f"Created offering: {offering}")

        # Create FICO/LTV adjustments
        fico_ltv_grid = [
            (740, 779, 0, 60, -0.250),
            (740, 779, 60, 70, -0.125),
            (740, 779, 70, 75, 0.000),
            (740, 779, 75, 80, 0.125),
            (700, 739, 0, 60, 0.000),
            (700, 739, 60, 70, 0.125),
            (700, 739, 70, 75, 0.250),
            (700, 739, 75, 80, 0.375),
            (660, 699, 0, 60, 0.250),
            (660, 699, 60, 70, 0.375),
            (660, 699, 70, 75, 0.500),
            (660, 699, 75, 80, 0.750),
        ]

        for min_fico, max_fico, min_ltv, max_ltv, points in fico_ltv_grid:
            RateAdjustment.objects.get_or_create(
                offering=offering,
                adjustment_type='fico_ltv',
                row_min=min_fico,
                row_max=max_fico,
                col_min=min_ltv,
                col_max=max_ltv,
                defaults={'adjustment_points': points}
            )

        self.stdout.write(self.style.SUCCESS(f"Created {len(fico_ltv_grid)} rate adjustments"))
        self.stdout.write(self.style.SUCCESS("Seeding complete!"))
```

**Don't forget to create the directory structure**:
```bash
mkdir -p backend/pricing/management/commands
touch backend/pricing/management/__init__.py
touch backend/pricing/management/commands/__init__.py
```

**Run the seed command**:
```bash
docker compose exec backend python manage.py seed_data
```

---

## 🖥️ TASK 4: Full Stack Verification

**Checklist**:
- [ ] Backend running at http://localhost:8000
- [ ] Admin accessible at http://localhost:8000/admin/
- [ ] API health check: `curl http://localhost:8000/api/v1/health/`
- [ ] Frontend running at http://localhost:3000
- [ ] Quote form visible at http://localhost:3000/quote
- [ ] Quote API returns data (even if empty)

**Docker Status**:
```bash
docker compose ps
# All containers should be "Up" and healthy
```

**View Logs for Errors**:
```bash
docker compose logs -f backend
```

---

## 🚨 TASK 5: Fix Any Blocking Errors

If you encounter errors, prioritize fixing them in this order:
1. Import errors (missing modules)
2. Database migration issues
3. URL routing issues
4. Frontend build errors
5. API response format issues

**Common Fixes**:
- Missing package: Add to `requirements.txt`, rebuild: `docker compose up -d --build backend`
- Migration issues: `docker compose exec backend python manage.py makemigrations && python manage.py migrate`
- Frontend issues: Check `package.json`, run `npm install`

---

## ✅ SUCCESS CRITERIA

When done, I should be able to:
1. Open http://localhost:3000/quote in a browser
2. Fill out the quote form (loan amount, LTV, FICO, etc.)
3. Click submit and see a response (quotes or "no matches")
4. Open http://localhost:8000/admin/ and log in
5. See Lenders, Programs, and Rate Adjustments in the admin

**Report back with**:
- Screenshot or description of what's working
- Any remaining issues
- Git commit with your fixes
