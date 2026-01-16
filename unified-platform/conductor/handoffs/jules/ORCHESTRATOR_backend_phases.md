# Jules Self-Orchestration: Finalization Track (F.1-F.6, F.8)

**Track**: `finalization_20260114`  
**Role**: L1 Backend Orchestrator + L2 Executor  
**Strategy**: Self-orchestrate backend phases with concurrent cloud execution

---

## MISSION

You (Jules) are the **primary orchestrator** for all backend phases of the finalization track. Execute phases F.1-F.6 and F.8 concurrently in the cloud, updating the checklist as you complete each phase.

---

## WHY JULES AS ORCHESTRATOR?

1. **Direct repo access** - You're already in unified-cmtg
2. **Concurrent execution** - Cloud workers can run F.2 + F.4 in parallel
3. **No handoff overhead** - Execute, verify, and update in one flow
4. **Faster iteration** - No waiting for L1 to dispatch next task

---

## ORCHESTRATION WORKFLOW

### Phase Execution Pattern

For each phase:
```
1. Read prompt: conductor/handoffs/jules/FX_*.md
2. Execute all tasks in prompt
3. Run verification commands
4. Update checklist.md: Mark FX as ✅ Complete
5. Commit: git commit -m "feat(cms): FX description"
6. Move to next phase OR escalate if blocked
```

### Concurrent Execution Strategy

**Wave 1** (Already Complete):
- ✅ F.1: Wagtail Models (15 mins)

**Wave 2** (Run in Parallel - 2-3 hours each):
```bash
# Start both simultaneously
jules --cloud execute F2_wordpress_extraction.md &
jules --cloud execute F4_office_import.md &

# Wait for both to complete
# Update checklist: F.2 ✅, F.4 ✅
```

**Wave 3** (Run in Parallel - after Wave 2):
```bash
# F.3 needs F.2, F.5 needs F.4, but they can run in parallel
jules --cloud execute F3_content_import.md &
jules --cloud execute F5_seo_infrastructure.md &

# Wait for both
# Update checklist: F.3 ✅, F.5 ✅
```

**Wave 4** (After Wave 3):
```bash
# F.8 can run anytime after F.1
jules --cloud execute F8_floify_testing.md

# Update checklist: F.8 ✅
```

---

## DETAILED PHASE EXECUTION

### F.2: WordPress Extraction (2-3 hours)

**Read**: `conductor/handoffs/jules/F2_wordpress_extraction.md`

**Execute**:
```bash
cd unified-platform/backend
# Create wp_extractor.py
python scripts/wp_extractor.py
```

**Verify**:
```bash
jq length wp_export/programs.json  # Should be 75+
jq '.[0].acf | keys' wp_export/programs.json  # Check ACF fields
```

**Update Checklist**:
```python
# Update conductor/tracks/finalization_20260114/checklist.md
# Mark F.2 tasks as [x] Complete
# Update status: "F.2 ✅ | F.3-F.10 ⏳"
```

**Commit**:
```bash
git add -A
git commit -m "feat(cms): F.2 WordPress content extraction - ${count} programs"
git push
```

---

### F.4: Office Import (2-3 hours) - PARALLEL WITH F.2

**Read**: `conductor/handoffs/jules/F4_office_import.md`

**Execute**:
```bash
cd unified-platform/backend
# Create Office model, import command
python manage.py makemigrations cms
python manage.py migrate
python manage.py import_offices
```

**Verify**:
```bash
python manage.py shell -c "from cms.models import Office; print(Office.objects.count())"
python manage.py shell -c "from cms.models import Office; print(Office.objects.get(is_headquarters=True))"
```

**Update & Commit**: Same pattern as F.2

---

### F.3: Content Import (4-6 hours) - AFTER F.2

**Read**: `conductor/handoffs/jules/F3_content_import.md`

**Execute**:
```bash
cd unified-platform/backend
# Create import_wordpress.py
python manage.py import_wordpress --dry-run
python manage.py import_wordpress
python scripts/verify_url_parity.py
```

**Verify**:
```bash
python manage.py shell -c "from cms.models import ProgramPage; print(ProgramPage.objects.count())"
# Should be 75+
```

**Critical**: URL parity must be 100%. If not, escalate to Gemini CLI.

---

### F.5: SEO Infrastructure (6-8 hours) - AFTER F.4, PARALLEL WITH F.3

**Read**: `conductor/handoffs/jules/F5_seo_infrastructure.md`

**Execute**:
```bash
cd unified-platform/backend
# Create City, LocalProgramPage models
# Create ProximityService, SchemaGenerator
python manage.py makemigrations cms
python manage.py migrate
python manage.py import_cities
```

**Verify**:
```bash
# Test proximity service
python manage.py shell
>>> from cms.services.proximity import ProximityService
>>> from cms.models import City
>>> city = City.objects.get(name='Denver')
>>> office = ProximityService.find_nearest_office(city)
>>> print(office)

# Create test LocalProgramPage
>>> from cms.models import ProgramPage, LocalProgramPage
>>> program = ProgramPage.objects.first()
>>> local = LocalProgramPage(program=program, city=city, assigned_office=office)
>>> from wagtail.models import Page
>>> Page.objects.get(slug='home').add_child(instance=local)
>>> print(local.url)  # Should be /program-slug-city-state/
```

---

### F.8: Floify Testing (3-4 hours) - CAN RUN ANYTIME AFTER F.1

**Execute**:
```bash
# Test lead submission
curl -X POST http://localhost:8001/api/v1/leads/ \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Test","last_name":"User","email":"test@example.com","phone":"555-0100","loan_amount":500000}'

# Test webhook
curl -X POST http://localhost:8001/api/v1/webhooks/floify/ \
  -H "Content-Type: application/json" \
  -d '{"event":"application.created","payload":{"id":"test-123","email":"test@example.com"}}'

# Verify Application model
python manage.py shell -c "from applications.models import Application; print(Application.objects.count())"
```

**Fix issues**: CORS, Decimal serialization, etc.

---

## ESCALATION TO GEMINI CLI

Call Gemini CLI (Antigravity) if:

### Blocking Issues:
- ❌ WordPress API returns 0 programs
- ❌ ACF fields missing from export
- ❌ URL parity < 100%
- ❌ Migrations fail
- ❌ Model conflicts

### Cross-Agent Coordination:
- Need Claude Code to start F.7 (frontend)
- Need Gemini CLI for F.6 (AI content generation)
- Ready for F.9 (testing requires Antigravity orchestration)

### Escalation Method:
```
Write to: conductor/handoffs/gemini/inbox.md

Format:
---
ESCALATION: FX Blocked

Issue: [Describe problem]
Attempted: [What you tried]
Error: [Error message]
Need: [What you need from Gemini CLI]
---
```

---

## GEMINI CLI COORDINATION POINTS

Gemini CLI handles:

1. **F.6: AI Content Generation** (Gemini's task)
   - After F.5 complete
   - OpenAI/Open-Router integration
   - Generate 50-100 test pages

2. **F.7: Next.js Integration** (Claude Code)
   - Can start after F.1
   - Gemini CLI dispatches to Claude

3. **F.9: Testing & Hardening** (All agents)
   - After F.1-F.8 complete
   - Gemini CLI coordinates E2E tests
   - Jules handles security audit

4. **F.10: Deployment** (Gemini + Jules)
   - Final production deployment
   - DNS, monitoring, cutover

---

## AUTO-UPDATE CHECKLIST

After each phase completion:

```python
# Read checklist
with open('conductor/tracks/finalization_20260114/checklist.md', 'r') as f:
    content = f.read()

# Update phase status
content = content.replace('**Status**: ⏳ Pending', '**Status**: ✅ Complete', 1)
content = content.replace('- [ ]', '- [x]', task_count)
content = content.replace('**Progress**: F.X ✅', f'**Progress**: F.{X+1} ✅')

# Write back
with open('conductor/tracks/finalization_20260114/checklist.md', 'w') as f:
    f.write(content)
```

Or use sed:
```bash
sed -i 's/\*\*Status\*\*: ⏳ Pending/\*\*Status\*\*: ✅ Complete/' checklist.md
```

---

## SUCCESS CRITERIA

Complete F.1-F.5, F.8 autonomously:
- ✅ All verification tests pass
- ✅ Checklist updated after each phase
- ✅ Code committed and pushed
- ✅ No blocking errors
- ✅ Handoff to Gemini CLI for F.6, F.9, F.10

---

## EXECUTION COMMAND

Start autonomous backend execution:

```bash
jules orchestrate finalization_20260114 \
  --phases F2,F3,F4,F5,F8 \
  --concurrent \
  --auto-verify \
  --update-checklist
```

This will:
1. Execute F.2 + F.4 in parallel
2. Wait for completion
3. Execute F.3 + F.5 in parallel
4. Execute F.8
5. Verify each phase
6. Update checklist automatically
7. Escalate only if blocked

---

## FINAL HANDOFF

When F.1-F.5, F.8 complete, write to Gemini CLI:

```
conductor/handoffs/gemini/inbox.md:

Backend phases complete!
✅ F.1: Wagtail Models
✅ F.2: WordPress Extraction ([X] programs)
✅ F.3: Content Import (URL parity: 100%)
✅ F.4: Office Import ([Y] offices)
✅ F.5: SEO Infrastructure ([Z] cities)
✅ F.8: Floify Testing (working)

Ready for:
- F.6: AI Content Generation (Gemini CLI)
- F.7: Next.js Integration (Claude Code - can start now)
- F.9: Testing (All agents)
- F.10: Deployment
```
