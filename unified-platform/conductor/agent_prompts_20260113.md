# Agent Prompts - 2026-01-13 01:51 PST (Post-Claude Models)

## 📊 Current State
- **Claude**: ✅ Completed 11 models, 150+ fields
- **Gemini CLI**: ✅ Verified services (backend/frontend 200 OK)
- **Jules**: ⏳ Needs to run migrations
- **Migrations**: ❌ Not yet created

---

## 🔴 URGENT: Prompt for Jules (Run Migrations NOW)

```
# MISSION: Run Phase 2 Migrations IMMEDIATELY
# ROLE: The Builder
# CONTEXT:
Claude has completed the pricing models. They are ready for migration.
Gemini CLI verified all services are running.

# STEP 1: Commit Claude's Work (if not already)
cd ~/code/unified-cmtg
git add -A
git commit -m "[phase2] Add pricing models, services, and common fields"
git push origin main

# STEP 2: Verify Files Exist
ls -la unified-platform/backend/pricing/models/
# Expected:
#   __init__.py
#   programs.py
#   program_types.py
#   adjustments.py

ls -la unified-platform/backend/common/
# Expected:
#   __init__.py
#   fields.py

# STEP 3: Update Django Settings
# Add 'common' to INSTALLED_APPS in config/settings/base.py

# STEP 4: Install Dependencies
docker compose exec backend pip install django-localflavor phonenumbers django-phonenumber-field

# STEP 5: Run Migrations
docker compose exec backend python manage.py makemigrations pricing
docker compose exec backend python manage.py migrate

# STEP 6: Verify
docker compose exec backend python manage.py showmigrations pricing
curl http://localhost:8001/api/v1/health/

# SUCCESS CRITERIA:
- [ ] Migrations created for pricing app
- [ ] Migrations applied without error
- [ ] Health endpoint returns 200

# HANDOFF:
Commit and push: git add -A && git commit -m "[phase2] Applied migrations" && git push origin main
```

---

## 🟢 Prompt for Claude (Create Quote API)

```
# MISSION: Create Quote API Endpoint
# ROLE: The Generator
# CONTEXT:
Your pricing models are complete and ready. 
Jules is running migrations now.

# NEXT TASK: Create the Quote API
After migrations succeed, create:

## 1. Update api/views.py
Add QuoteView using your LoanMatchingService:

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from pricing.services.matching import LoanMatchingService, QualifyingInfo

class QuoteView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        data = request.data
        ltv = (data['loan_amount'] / data['property_value']) * 100
        
        scenario = QualifyingInfo(
            state=data['property_state'],
            property_type=data.get('property_type', 'sfr'),
            entity_type=data.get('entity_type', 'individual'),
            purpose=data.get('loan_purpose', 'purchase'),
            occupancy=data.get('occupancy', 'primary'),
            loan_amount=data['loan_amount'],
            ltv=ltv,
            estimated_credit_score=data['credit_score']
        )
        
        service = LoanMatchingService(scenario)
        matches = service.get_matches()[:10]
        
        results = [{
            'lender': m.lender.company_name,
            'program': m.program_type.name,
            'rate_range': m.rate_range,
        } for m in matches]
        
        return Response({'quotes': results})

## 2. Update api/urls.py
Add: path('v1/quote/', QuoteView.as_view(), name='quote'),

# SUCCESS CRITERIA:
curl -X POST http://localhost:8001/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{"property_state":"CA","loan_amount":500000,"credit_score":720,"property_value":650000}'
# Should return JSON with quotes array
```

---

## 🟡 Prompt for Gemini CLI (Re-verify After Migrations)

```
# MISSION: Verify Phase 2 After Migrations
# ROLE: Verification Agent

# WAIT for Jules to complete migrations, then:

## 1. Sync Latest
cd ~/code/unified-cmtg
git pull origin main

## 2. Verify Migrations Applied
docker compose exec backend python manage.py showmigrations pricing
# Expected: [X] 0001_initial (or similar)

## 3. Test Quote API (after Claude adds it)
curl -X POST http://localhost:8001/api/v1/quote/ \
  -H "Content-Type: application/json" \
  -d '{"property_state":"CA","loan_amount":500000,"credit_score":720,"property_value":650000}'

# REPORT:
✅ PASS or ❌ FAIL for each step
```

---

## 🔵 Antigravity Status

```
CURRENT: Coordinating migration handoff

CLAUDE: ✅ Models complete (11 models, 150+ fields)
  - pricing/models/programs.py (602 lines)
  - pricing/models/program_types.py (308 lines) 
  - pricing/models/adjustments.py (120 lines)
  - pricing/services/matching.py (188 lines)
  - common/fields.py (100 lines)
  - HANDOFF_TO_JULES.md created

JULES: ⏳ Run migrations
GEMINI: ✅ Services verified, awaiting migration verification

NEXT: Monitor Jules → then Claude Quote API → Gemini verify
```

---

## 📋 Execution Order (Updated)

1. ✅ **Claude**: Models complete
2. 🔄 **Jules**: Commit & run migrations ← **CURRENT**
3. ⏳ **Claude**: Create Quote API
4. ⏳ **Gemini CLI**: Verify migrations + API
5. ⏳ **Antigravity**: Update checklist, Phase 2 complete
