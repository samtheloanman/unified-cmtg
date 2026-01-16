# Gemini CLI Meta-Orchestration: Cross-Agent Coordination

**Track**: `finalization_20260114`  
**Role**: L1 Meta-Orchestrator (Cross-System Coordination)  
**Strategy**: Coordinate Jules (backend), Claude Code (frontend), and handle verification/deployment

---

## REVISED ORCHESTRATION ARCHITECTURE

### L1 Orchestration (Two-Tier):

**Jules** = **Backend Orchestrator** (F.1-F.6, F.8)
- Self-orchestrates all backend work
- Executes concurrently in cloud
- Updates checklist.md directly
- Escalates to Gemini CLI only when blocked

**Gemini CLI** = **Meta-Orchestrator** (Cross-Agent Coordination)
- Coordinates Jules (backend) ↔ Claude Code (frontend)
- Handles F.6 (AI content - your task)
- Orchestrates F.9 (testing - requires all agents)
- Manages F.10 (deployment - cross-system)

---

## GEMINI CLI RESPONSIBILITIES

### 1. Monitor Jules Progress

Watch for Jules handoffs:
```bash
watch -n 10 cat conductor/handoffs/gemini/inbox.md
```

When Jules completes F.5, dispatch F.6.

---

### 2. F.6: AI Content Generation (YOUR TASK)

**After**: F.5 complete (Jules confirms LocalProgramPage infrastructure ready)

**Your Task**:
```python
# Create: backend/cms/services/ai_content_generator.py
# Support OpenAI + Open-Router (via MCP)

class AIContentGenerator:
    def __init__(self):
        # Use MCP server for Open-Router config
        self.provider = settings.AI_CONTENT_PROVIDER
        
    def generate_local_intro(self, program, city, office):
        # Call OpenAI or Open-Router via MCP
        pass
    
    def generate_local_faqs(self, program, city):
        pass
```

**Create Command**:
```python
# backend/cms/management/commands/generate_local_pages.py
# Bulk generation with --programs, --cities, --use-openai
```

**Test**:
```bash
python manage.py generate_local_pages \
  --programs dscr-loan fha-loan \
  --cities "Los Angeles,CA;Denver,CO" \
  --use-openai
```

**Verify**:
- 50 pages generated (10 cities × 5 programs)
- Content is unique per page
- Schema markup present

---

### 3. Coordinate Frontend (F.7)

**Dispatch to Claude Code** after F.1 complete:

```
Read: conductor/handoffs/claude/F7_nextjs_integration.md
Execute all tasks
Test: npm run build
Verify: /programs, /blog pages work
Write completion to: conductor/handoffs/gemini/inbox.md
```

**Monitor**: Check for completion message in inbox

---

### 4. F.9: Testing & Hardening Orchestration

**After**: F.1-F.8 all complete

**Coordinate**:
- Jules: Security audit, performance optimization
- Antigravity (you): E2E testing, SEO verification
- Gemini CLI: Load testing

**Tasks**:

**Security Audit** (Dispatch to Jules):
```
python manage.py check --deploy
Fix all warnings
Add database indexes
Configure Redis caching
```

**E2E Testing** (Antigravity - Browser):
```
Test Quote Wizard: /quote
Test Apply flow
Test program pages
Test local pages
Test blog pages
```

**SEO Verification** (You):
```bash
# Generate sitemap
# Check robots.txt
# Run Lighthouse on key pages
npx lighthouse http://localhost:3001/programs --only-categories=seo
```

**Load Testing** (You):
```python
# Install Locust
# Test /api/v1/quote/ with 100 concurrent users
# Verify response times < 500ms
```

---

### 5. F.10: Deployment Orchestration

**Coordinate with Jules**:

**Staging** (Jules):
```
Deploy backend to staging
Deploy frontend to staging
Run smoke tests
```

**Verification** (You):
```
Test staging URLs
Verify DNS
Check SSL certificates
Run final E2E tests
```

**Production** (Jules + You):
```
Configure DNS: cmre.c-mtg.com
Deploy to production
Set up monitoring (Sentry, UptimeRobot)
Monitor for 24 hours
```

---

## HANDOFF PROTOCOL

### From Jules → Gemini CLI

Jules writes to `conductor/handoffs/gemini/inbox.md`:
```
FX Complete: [Description]
- [Key metrics]
- [Verification results]
Ready for: [Next phase]
```

### From Gemini CLI → Jules

You write to `conductor/handoffs/jules/inbox.md`:
```
FX Dispatched: [Task description]
Read: [Prompt file]
Execute: [Commands]
Report back when complete.
```

### From Gemini CLI → Claude Code

You write to `conductor/handoffs/claude/inbox.md`:
```
F.7 Dispatched: Next.js CMS Integration
Read: conductor/handoffs/claude/F7_nextjs_integration.md
Execute all tasks
Report back when build passes.
```

---

## MONITORING DASHBOARD

Track overall progress:

```bash
# Watch checklist
watch -n 5 cat conductor/tracks/finalization_20260114/checklist.md

# Watch Jules handoffs
tail -f conductor/handoffs/gemini/inbox.md

# Watch Claude handoffs
tail -f conductor/handoffs/claude/inbox.md

# Check git activity
git log --oneline --since="1 day ago" --all
```

---

## ESCALATION FROM JULES

If Jules writes:
```
ESCALATION: FX Blocked
Issue: [Problem]
Need: [Help needed]
```

**Your response**:
1. Read the issue
2. Investigate (check logs, review code, test)
3. Provide solution OR escalate to human
4. Write back to `conductor/handoffs/jules/inbox.md`

---

## SUCCESS CRITERIA

Track is complete when:
- ✅ Jules completes F.1-F.5, F.8
- ✅ You complete F.6 (AI content)
- ✅ Claude completes F.7 (Next.js)
- ✅ You orchestrate F.9 (testing)
- ✅ You + Jules complete F.10 (deployment)
- ✅ `cmre.c-mtg.com` is live and functional

---

## EXECUTION

**You don't need to run a command** - just monitor handoffs and execute your phases (F.6, F.9, F.10) when Jules signals readiness.

Stay responsive to inbox messages and coordinate across agents!
