# Gemini CLI Orchestrator: Finalization Track Automation

**Track**: `finalization_20260114`  
**Role**: L1 Orchestrator (Command & Control)  
**Mission**: Automate execution of F.1-F.10 with minimal human intervention

---

## ORCHESTRATION STRATEGY

You are the **L1 Orchestrator** managing the finalization track. Your job is to:
1. Dispatch tasks to L2 agents (Jules, Claude Code)
2. Monitor progress via handoff files
3. Verify completion before proceeding
4. Update checklist.md after each phase
5. Escalate to L3 (Human) only when blocked

---

## EXECUTION WORKFLOW

### Phase F.1: ✅ COMPLETE
- Jules completed in 15 mins
- Skip to F.2

### Phase F.2 + F.4: WordPress Extraction + Office Import (PARALLEL)

**Dispatch to Jules** (2 concurrent tasks):

**Task 1: F.2 WordPress Extraction**
```
Read: conductor/handoffs/jules/F2_wordpress_extraction.md
Execute all tasks
Write completion to: conductor/handoffs/gemini/inbox.md
Commit: "feat(cms): F.2 WordPress content extraction"
```

**Task 2: F.4 Office Import**
```
Read: conductor/handoffs/jules/F4_office_import.md
Execute all tasks
Write completion to: conductor/handoffs/gemini/inbox.md
Commit: "feat(cms): F.4 Office model with GPS"
```

**Verification**:
```bash
# Wait for both tasks to complete
# Check handoffs/gemini/inbox.md for completion messages

# Verify F.2
ls -lh unified-platform/backend/wp_export/
jq length unified-platform/backend/wp_export/programs.json

# Verify F.4
cd unified-platform/backend
python manage.py shell -c "from cms.models import Office; print(Office.objects.count())"
```

**Update Checklist**:
```
Mark F.2 as ✅ Complete in checklist.md
Mark F.4 as ✅ Complete in checklist.md
```

---

### Phase F.3: Content Import (After F.2)

**Dispatch to Jules**:
```
Create: backend/cms/management/commands/import_wordpress.py
Map WordPress ACF fields → Wagtail ProgramPage fields
Reference: wp_export/programs.json
Run: python manage.py import_wordpress --dry-run
Review output, fix any issues
Run: python manage.py import_wordpress
Verify: ProgramPage.objects.count() >= 75
```

**Verification by Antigravity**:
```bash
# Check URL parity
cd unified-platform/backend
python scripts/verify_url_parity.py

# Verify in Wagtail admin
# Open: http://localhost:8001/admin/pages/
# Confirm programs visible
```

**Update Checklist**: Mark F.3 as ✅ Complete

---

### Phase F.5: Programmatic SEO Infrastructure (After F.4)

**Dispatch to Jules**:
```
Read: implementation_plan.md Phase F.5
Create City model (cities.py)
Create LocalProgramPage model (local_pages.py)
Create ProximityService (services/proximity.py)
Create schema_generator.py
Create import_cities.py command
Import 150 cities from SimpleMaps CSV
Test: Create 1 LocalProgramPage manually
Verify flat URL: /dscr-loan-denver-co/
```

**Verification**:
```bash
# Check models
python manage.py shell -c "from cms.models import City, LocalProgramPage; print(City.objects.count())"

# Test proximity
python manage.py shell
>>> from cms.services.proximity import ProximityService
>>> from cms.models import City
>>> city = City.objects.get(name='Denver')
>>> office = ProximityService.find_nearest_office(city)
>>> print(office)
```

**Update Checklist**: Mark F.5 as ✅ Complete

---

### Phase F.7: Next.js Integration (PARALLEL - Can start after F.1)

**Dispatch to Claude Code**:
```
Read: conductor/handoffs/claude/F7_nextjs_integration.md
Execute all tasks
Test build: npm run build
Test pages: /programs, /programs/[slug], /blog
Write completion to: conductor/handoffs/gemini/inbox.md
Commit: "feat(frontend): F.7 Next.js Wagtail CMS integration"
```

**Verification by Antigravity**:
```bash
cd unified-platform/frontend
npm run build
# Check for errors

# Test URLs
curl http://localhost:3001/programs
curl http://localhost:3001/blog

# Run Lighthouse
npx lighthouse http://localhost:3001/programs --only-categories=seo
```

**Update Checklist**: Mark F.7 as ✅ Complete

---

### Phase F.6: AI Content Generation (After F.5)

**Dispatch to Gemini CLI** (YOU):
```
Create: backend/cms/services/ai_content_generator.py
Support both OpenAI and Open-Router (via MCP)
Create: backend/cms/management/commands/generate_local_pages.py
Test with 10 cities × 5 programs = 50 pages
Verify content uniqueness
Verify schema markup
```

**Implementation**:
```python
# ai_content_generator.py
import openai
from django.conf import settings

class AIContentGenerator:
    def __init__(self):
        self.provider = settings.AI_CONTENT_PROVIDER  # 'openai' or 'openrouter'
        if self.provider == 'openrouter':
            # Use MCP server config
            self.api_key = settings.OPENROUTER_API_KEY
            self.base_url = "https://openrouter.ai/api/v1"
        else:
            self.api_key = settings.OPENAI_API_KEY
            self.base_url = "https://api.openai.com/v1"
    
    def generate_local_intro(self, program, city, office):
        """Generate 200-word localized intro."""
        prompt = f"""Write a 200-word introduction about {program.title} in {city.name}, {city.state_name}.
        Mention the local office at {office.address}.
        Write professionally for homebuyers."""
        
        # Use OpenAI or Open-Router
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            api_key=self.api_key,
            base_url=self.base_url
        )
        return response.choices[0].message.content
```

**Verification**:
```bash
# Generate test pages
python manage.py generate_local_pages \
  --programs dscr-loan fha-loan \
  --cities "Los Angeles,CA;Denver,CO;Phoenix,AZ" \
  --use-openai

# Check generated pages
python manage.py shell
>>> from cms.models import LocalProgramPage
>>> LocalProgramPage.objects.count()
>>> page = LocalProgramPage.objects.first()
>>> print(page.local_intro)
```

**Update Checklist**: Mark F.6 as ✅ Complete

---

### Phase F.8: Floify Integration Testing (PARALLEL with F.7)

**Dispatch to Jules**:
```
Test lead submission: POST /api/v1/leads/
Test webhook: POST /api/v1/webhooks/floify/
Verify Application model creates records
Fix any CORS/serialization issues
End-to-end test: Quote → Apply → Email
```

**Verification**:
```bash
# Test lead submission
curl -X POST http://localhost:8001/api/v1/leads/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Test",
    "last_name": "User",
    "email": "test@example.com",
    "phone": "555-0100",
    "loan_amount": 500000
  }'

# Check Floify dashboard for prospect
# Check Application model
python manage.py shell -c "from applications.models import Application; print(Application.objects.count())"
```

**Update Checklist**: Mark F.8 as ✅ Complete

---

### Phase F.9: Production Hardening & Testing (After F.1-F.8)

**Dispatch to All Agents**:

**Jules - Security Audit**:
```
Set DEBUG=False in production settings
Verify SECRET_KEY from environment
Run: python manage.py check --deploy
Fix all warnings
Add database indexes
Configure Redis caching
```

**Antigravity - E2E Testing**:
```
Test: Quote Wizard flow
Test: Apply flow (Floify)
Test: Program pages load
Test: Local pages load
Test: Blog pages load
Generate sitemap.xml
Configure robots.txt
Run Lighthouse on all page types
```

**Gemini CLI - Load Testing**:
```
Install Locust
Create load test script
Test /api/v1/quote/ with 100 concurrent users
Test page loads with 100 concurrent users
Verify response times < 500ms
```

**Update Checklist**: Mark F.9 as ✅ Complete

---

### Phase F.10: Deployment (After F.9)

**Dispatch to Jules + Antigravity**:
```
Deploy to staging environment
Run smoke tests
Deploy to production
Configure DNS for cmre.c-mtg.com
Set up monitoring (Sentry, UptimeRobot)
Monitor for 24 hours
```

**Update Checklist**: Mark F.10 as ✅ Complete

---

## AUTOMATION RULES

### Auto-Proceed Conditions
Proceed to next phase automatically if:
- ✅ All tasks in current phase marked complete
- ✅ Verification tests pass
- ✅ No errors in handoff messages
- ✅ Commits pushed successfully

### Escalate to Human If:
- ❌ Verification tests fail after 2 retries
- ❌ Agent reports blocking error
- ❌ Data quality issues (e.g., missing ACF fields)
- ❌ Integration failures (Floify, WordPress API)

### Handoff Protocol
After each phase:
1. Agent writes to `conductor/handoffs/gemini/inbox.md`
2. Gemini CLI reads inbox
3. Runs verification commands
4. Updates `checklist.md`
5. Dispatches next task OR escalates

---

## MONITORING DASHBOARD

Track progress in real-time:
```bash
# Watch checklist
watch -n 5 cat conductor/tracks/finalization_20260114/checklist.md

# Watch handoffs
tail -f conductor/handoffs/gemini/inbox.md

# Check git commits
git log --oneline --since="1 day ago"
```

---

## EXECUTION COMMAND

To start automated execution:
```bash
# Gemini CLI
gemini conductor execute finalization_20260114 --auto-proceed --escalate-on-error
```

This will:
1. Read checklist.md
2. Identify next pending phase
3. Dispatch to appropriate agent
4. Monitor for completion
5. Verify and proceed
6. Repeat until F.10 complete

---

## SUCCESS CRITERIA

Track is complete when:
- ✅ All phases F.1-F.10 marked complete in checklist.md
- ✅ `cmre.c-mtg.com` is live and functional
- ✅ All verification tests pass
- ✅ No critical errors in 24-hour monitoring period
