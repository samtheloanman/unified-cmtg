# Conductor Folder Analysis & Integration Points

**Purpose:** Analyze existing conductor documentation and identify how Claude Code should integrate with it.

**Date:** 2026-01-12

---

## 📁 CONDUCTOR DIRECTORY STRUCTURE

```
conductor/
├── tracks.md                      # Track overview & dependencies
├── workflow.md                    # SOP with verification tiers
├── current.md                     # Phase 1 sprint status
├── tasks.md                       # Master task breakdown
├── product-guidelines.md          # Product requirements
├── product.md                     # Product overview
├── tech-stack.md                  # Technology specifications
├── setup_state.json              # Setup configuration (new)
│
├── code_styleguides/             # Code conventions
│   ├── general.md               # 23 lines - General conventions
│   ├── python.md                # 36 lines - Python patterns
│   ├── typescript.md            # 42 lines - TypeScript patterns
│   └── html-css.md              # 48 lines - HTML/CSS patterns
│
├── tracks/                        # 6 workflow tracks
│   ├── phase1_foundation/
│   │   └── plan.md              # Docker/Django/Wagtail setup
│   ├── phase2_pricing/
│   │   └── plan.md              # Model porting & API
│   ├── phase3_content/
│   │   └── plan.md              # WordPress to Wagtail migration
│   ├── phase3a_seo/             # (inferred from tracks.md)
│   ├── ratesheet_agent/
│   │   └── plan.md              # PDF extraction pipeline
│   └── phase5_floify/
│       └── plan.md              # Lead capture integration
│
├── temp_marketing/               # Marketing/SEO content (temporary)
└── .DS_Store, ._files            # macOS system files (can be ignored)
```

---

## 🎯 KEY CONDUCTOR DOCUMENTS

### 1. tracks.md - Workflow Overview

**Contains:**
- Track status table (9 phases)
- Agent assignments (8 roles)
- Dependency mermaid diagram
- Research tasks queue

**Key Info:**
```
Phase 1 (Foundation):    🟡 In Progress
Phase 2 (Pricing):       ⏳ Pending
Phase 3 (Content):       ⏳ Pending
Phase 3a (SEO):          ⏳ Pending
Phase 4 (Rate Sheets):   ⏳ Pending
Phase 5 (Floify):        ⏳ Pending
Phase 6 (AI Blog):       ⏳ Pending
Phase 7 (Affiliate):     ⏳ Pending
Phase 8 (Investment):    ⏳ Pending
Phase 9 (Forum):         ⏳ Deferred
```

**Agent Roles Defined:**
- Pricing Engineer (Phase 2, 4, 7, 8)
- Wagtail Expert (Phase 3, 3a)
- Frontend Architect (Phase 3, 5, 9)
- Rate Sheet Agent (Phase 4)
- QA Tester (Phase 1)
- Content Agent (Phase 6)
- Marketing Agent (Phase 7)
- Research Agent (Phase 8, 9)

**❌ Gap:** No explicit L2 Agent mapping in conductor (Claude, Jules, Ralph undefined here)

---

### 2. workflow.md - Standard Operating Procedures

**Contains:**
- Quality requirements (>80% test coverage)
- Test-driven default (TDD model)
- Commit frequency (after each task)
- Git notes for detailed tracking
- **Verification Tiers:**
  - Tier 1: Automated (run tests, proceed if pass, escalate if fail)
  - Tier 2: Manual (present artifacts, await approval)

**Key Rules:**
1. "Task complete only when tests pass" ✅
2. Commit after each verifiable task
3. Use Git Notes for detailed summaries
4. Automated or Manual verification depending on phase type
5. Ralph handles test loops
6. Escalate to L3 (Human) if Ralph can't resolve

**✅ Alignment:** Perfectly matches Command & Control doctrine

---

### 3. current.md - Phase 1 Sprint Status

**Contains:**
- Immediate tasks (3 items, all ⏳ Pending)
- Completed items (6 checkboxes ✅)
- Blockers and resolutions
- Phase 1 checklist (~70% complete)
- This week's schedule
- Next action

**Immediate Tasks:**
1. Verify legacy cmtgdirect on 8000 → `curl localhost:8000/admin/` → 200
2. Frontend connectivity test → Visit `localhost:3001/test` → "API ok"
3. Create Wagtail superuser → Login to `localhost:8001/admin/`

**Status:** Docker running, Health API working, migrations pending, Superuser pending

**⚠️ Note:** Document is somewhat manual - could be automated with better integration

---

### 4. code_styleguides/ - Code Conventions (149 lines total)

#### general.md (23 lines)
```
❓ Incomplete - checked into git but minimal content
Topics: Not detailed in provided excerpt
```

#### python.md (36 lines)
```
❓ Incomplete - needs full review
Expected topics: Naming, imports, PEP 8, Django patterns, type hints?
```

#### typescript.md (42 lines)
```
❓ Incomplete - needs full review
Expected topics: Naming, types, interfaces, React patterns?
```

#### html-css.md (48 lines)
```
❓ Incomplete - needs full review
Expected topics: BEM, tailwind patterns, accessibility, mobile-first?
```

**Assessment:**
- ✅ Structure exists (4 files)
- ❌ Content is brief (total 149 lines)
- ❌ No integration with Claude's style enforcement
- ❌ Missing: Linting config, formatters, pre-commit hooks
- ❌ Missing: Tools/automation references

---

### 5. product-guidelines.md - Product Requirements

**Contains:**
- Product vision
- Design principles
- UI/UX guidelines
- Content strategy
- Target audience
- Success metrics

**Assessment:** Comprehensive product-level guidance

---

### 6. Phase Track Plans

**phase1_foundation/plan.md:**
- Docker container setup
- Django project initialization
- Wagtail CMS configuration
- Health check endpoint
- Database migrations
- Frontend connectivity

**phase2_pricing/plan.md:**
- Model porting (cmtgdirect → Django 5.0)
- ORM conversions
- Pricing logic translation
- API endpoint creation
- Rate adjustment grids
- Quote generation

**phase3_content/plan.md:**
- WordPress ACF export
- Wagtail model design
- Content migration script
- URL verification
- Bulk import

**ratesheet_agent/plan.md:**
- PDF download automation
- OCR + Gemini parsing
- CSV data extraction
- Validation & staging
- Database import

**phase5_floify/plan.md:**
- Webhook setup
- Lead capture
- Application status tracking
- Dashboard updates

---

## 🎨 DESIGNOS INTEGRATION (NEW)

**Role:** designOS acts as the **Visual Specification Engine** (The "What").
**Input:** `custommortgageinc.com` design analysis and PRD.
**Output:** `product-plan/` handoff package containing atomic React components, design tokens, and page templates.

### Workflow Alignment
1. **Design Agent** (in designOS project) creates the specs and components.
2. **Orchestrator** exports and copies the package to `unified-platform/product-plan/`.
3. **Frontend Architect** (in unified-cmtg) implements the build using this package as the source of truth.

**Key Files:**
- [implementation_plan.md](file:///home/samalabam/.gemini/antigravity/brain/969d8981-5a6e-4d06-a2dc-6044e954466b/implementation_plan.md)
- [designOS_instructions.md](file:///home/samalabam/.gemini/antigravity/brain/969d8981-5a6e-4d06-a2dc-6044e954466b/designOS_instructions.md)

---

## 🔗 INTEGRATION POINTS: CONDUCTOR → CLAUDE CODE

### 1. Pattern Library Integration

**Current State:**
- Conductor has `code_styleguides/` (brief, 149 lines)
- Claude has `Pattern Recognition Engine` (comprehensive)
- Gemini created a pattern library (external, needs review)

**Action Item:**
1. Read all 4 code_styleguides files fully
2. Expand them with details from Pattern Recognition Engine
3. Add tool references (black, prettier, eslint, mypy)
4. Create unified `claude/plugins/reference/pattern-library.md`
5. Cross-link from conductor

**Integration Goal:**
```
conductor/code_styleguides/python.md
  → Links to: claude/plugins/reference/pattern-library.md
  → Enforced by: claude/skills/tier-5-workflow/task-spec-parser.md
```

---

### 2. Phase Track Planning

**Current State:**
- Conductor has detailed `phase*/plan.md` files
- Each plan has: Overview, Tasks, Success Criteria, Blockers

**Action Item:**
1. Extract success criteria from each phase plan
2. Create test specifications for Ralph
3. Link from Conductor checklist.md → Claude Tier 4 Verification Skills

**Integration Goal:**
```
conductor/tracks/phase2_pricing/plan.md
  → Success Criteria: "Models validate, API returns 200"
  → Ralph Test Spec: (generated by Claude Tier 4)
  → Verification: pytest backend/tests/test_models.py
```

---

### 3. Task Status Tracking

**Current State:**
- Conductor has `current.md` (manual updates)
- Workflow defines "Task complete when tests pass"
- No automation connecting tests → checklist status

**Action Item:**
1. Create integration between Ralph (test runner) and Conductor checklist
2. Use Claude's Handoff Report Generator to update checklist.md
3. Reference Git commits in checklist updates

**Integration Goal:**
```
Ralph runs tests → Tests Pass → Claude creates Handoff Report
  → Handoff Report marks checklist item Complete
  → Git notes added with verification evidence
  → Next phase automatically ready
```

---

### 4. Code Style Enforcement

**Current State:**
- Style guides exist (thin documentation)
- No enforcement tools configured
- No pre-commit hooks

**Action Item:**
1. Expand code_styleguides with tool configuration
2. Add `.pre-commit-config.yaml` to root
3. Reference from Claude's `Architecture Normalizer` skill
4. Add to Phase 1 completion criteria

**Tools to Add:**
- Python: black, flake8, isort, mypy, pylint
- TypeScript: prettier, eslint, type-checking
- HTML/CSS: htmlhint, stylelint, prettier
- General: editorconfig, pre-commit

---

### 5. Agent Role Mapping

**Current State in Conductor:**
```
Pricing Engineer, Wagtail Expert, Frontend Architect, Rate Sheet Agent,
QA Tester, Content Agent, Marketing Agent, Research Agent
```

**Current State in Command & Control:**
```
L2 Claude (Generator), L2 Jules (Builder), L2 Ralph (Closer), L1 Orchestrator
```

**Gap:** Conductor tracks don't know about L2 roles

**Action Item:**
1. Map Conductor agent roles to L2 agents:
   - Pricing Engineer → Claude (generation) + Ralph (testing)
   - Wagtail Expert → Claude (generation)
   - Frontend Architect → Claude (generation)
   - Rate Sheet Agent → Claude (parser plugins) + Jules (setup)
   - QA Tester → Ralph (test runner, closer)
   - Content Agent → Claude (generation)
   - Etc.

2. Update `conductor/workflow.md` to reference L2 agents
3. Create mapping in `claude/README.md`

---

### 6. Verification & Escalation

**Current State:**
- Conductor defines Tier 1 (Automated) and Tier 2 (Manual)
- Ties to Ralph for automated tests
- No clear escalation when tests fail repeatedly

**Action Item:**
1. Claude's Handoff Report → Ralph's test results → Escalation to L3
2. Define "repeated failures" threshold (e.g., >3 attempts)
3. Create escalation template in `claude/skills/tier-5-workflow/`
4. Reference in conductor/workflow.md

---

## 📋 CONDUCTOR FILES TO ENHANCE

### High Priority

**1. code_styleguides/python.md** - Currently 36 lines
```markdown
Current (assumed): Basic PEP 8 guidelines
Needed Additions:
- Django ORM patterns (Manager, QuerySet, validation)
- Model structure (field ordering, Meta options)
- Serializer patterns (nested, custom validators)
- View/ViewSet patterns (mixins, permissions)
- Testing patterns (fixtures, mocking, assertions)
- Import organization (stdlib → django → local)
- Type hints (mypy configuration)
- Tools config (.flake8, setup.cfg)
- Black formatter rules
- Linting setup (pre-commit)
```

**2. code_styleguides/typescript.md** - Currently 42 lines
```markdown
Current (assumed): Basic TS guidelines
Needed Additions:
- Next.js App Router conventions
- React component patterns (hooks, composition)
- Type definitions (interfaces vs types)
- Error handling patterns
- API client patterns (fetch, error states)
- Testing patterns (jest, react-testing-library)
- File organization (components, hooks, utils)
- Import organization
- ESLint rules (airbnb or similar)
- Prettier configuration
- Pre-commit hooks
```

**3. workflow.md** - Add L2 Agent References
```markdown
Current: Tier 1/Tier 2 verification
Add:
- L2 Agent role assignments
- How Claude.Generator contributes
- How Jules.Builder supports
- How Ralph.Closer verifies
- Escalation to L3 Human
- Handoff report template
```

**4. current.md** - Add Automation
```markdown
Current: Manual status updates
Add:
- Link to latest commits
- Latest test results (from Ralph)
- Automated blockers list
- Next auto-proceeding phase (if tests pass)
```

### Medium Priority

**5. tasks.md** - Align with L2 Agents
```markdown
Current: Task breakdown
Add:
- Owner assignment (Claude vs Jules vs Ralph)
- Expected deliverables
- Success criteria (test names)
- Estimated effort
```

**6. Create conductor/checklists/phase*.checklist.md**
```markdown
New files for each track:
- One checklist per phase
- Format: [ ] Task Name (Owner: [Claude/Jules/Ralph])
- References to test names
- Links to related files
- Status updates (automated by Handoff Reports)
```

---

## 🔄 PROPOSED INTEGRATION WORKFLOW

```
1. Phase Starts
   └─> L1 Orchestrator reads: conductor/tracks/phaseN/plan.md
       └─> Creates: conductor/tracks/phaseN/checklist.md
           └─> Delegates to L2 Claude

2. Claude Receives Task
   └─> Uses: Codebase Structure Analyzer + Pattern Recognition
       └─> Generates: Code + Docstrings + Tests
           └─> Creates: Handoff Report (Tier 4 skill)
               └─> L1 reviews, approves, delegates to Ralph

3. Ralph (Closer) Tests
   └─> Runs: Tests from Handoff Report
       └─> If Pass: Creates Success Report
           └─> Marks checklist.md ✅ Complete
               └─> Git commit with notes
                   └─> L1 auto-proceeds to next task
       └─> If Fail: Enters test-and-fix loop
           └─> After N attempts → Escalate to L3 Human

4. L3 Human Review
   └─> Reviews: Escalation report + evidence
       └─> Decision: Fix / Skip / Replan
           └─> Updates: conductor/current.md
               └─> Resumes workflow
```

---

## ✅ ACTIONABLE RECOMMENDATIONS

### Immediate (This Week)

1. **Expand code_styleguides/** (1-2 hours)
   - Add detailed patterns for each language
   - Link to Claude's Pattern Recognition Engine
   - Add tool configurations

2. **Create conductor/checklists/** (1 hour)
   - One checklist per phase
   - Template: `[ ] Task (Owner: Claude) (Test: test_*.py) (Status: ⏳)`
   - Auto-update from Handoff Reports

3. **Update conductor/workflow.md** (30 min)
   - Add L2 Agent references
   - Link to Claude skills
   - Add escalation flowchart

4. **Read & integrate Gemini pattern library** (1-2 hours)
   - Merge into Claude's Pattern Recognition Engine
   - Update conductor/code_styleguides
   - Cross-reference both

### This Week

5. **Create conductor/integration-map.md**
   - Maps conductor phases → Claude skills
   - Maps success criteria → Test specs
   - Defines what Ralph validates

6. **Add pre-commit configuration**
   - `.pre-commit-config.yaml` at root
   - Style enforcement hooks
   - Test verification hooks

7. **Update Phase 1 success criteria**
   - Define exact tests Ralph must run
   - Test file locations
   - Expected outputs

### Later (Foundation for Future Phases)

8. **Create Handoff Report template**
   - What Claude produces
   - Format Ralph consumes
   - Checklist.md updates

9. **Create Escalation template**
   - What triggers escalation
   - Information to include
   - L3 decision options

10. **Document L2-L3 integration**
    - When to escalate
    - How to escalate
    - Resolution process

---

## 🎯 SUCCESS METRICS

**After Integration:**
- ✅ Conductor 100% aligned with Command & Control doctrine
- ✅ Code styleguides > 500 lines (detailed, tool-integrated)
- ✅ Checklists auto-updated from Handoff Reports
- ✅ No manual status updates needed
- ✅ Claude skills directly support conductor phases
- ✅ Clear test specifications for each task
- ✅ Escalation process defined and documented

---

## 📊 FILES TO CREATE/UPDATE

| File | Action | Owner | Priority |
|------|--------|-------|----------|
| code_styleguides/python.md | Expand (36→200 lines) | Claude | High |
| code_styleguides/typescript.md | Expand (42→250 lines) | Claude | High |
| code_styleguides/html-css.md | Expand (48→150 lines) | Claude | High |
| code_styleguides/general.md | Expand (23→100 lines) | Claude | High |
| conductor/workflow.md | Add L2 refs | Claude | High |
| conductor/checklists/phase*.md | Create | Claude | High |
| conductor/integration-map.md | Create | Claude | Medium |
| .pre-commit-config.yaml | Create | Jules | Medium |
| conductor/escalation.md | Create | L1 | Medium |
| claude/plugins/reference/pattern-library.md | Create/merge | Claude | High |

---

**Analysis Complete**
**Date:** 2026-01-12
**Reviewer:** Claude Code (L2 Generator)
**Status:** Ready for integration planning
