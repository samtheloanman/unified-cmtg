# Integration Map: Conductor Workflow → Agent Skills

> **Purpose**: Maps how the Conductor orchestration system connects to L2 Agent skills and defines handoff protocols.

---

## 🔗 Agent-to-Track Mapping

| Track | Primary Agent | Skills Used | Support Agent |
|:------|:--------------|:------------|:--------------|
| Phase 1: Foundation | QA Tester | Codebase Structure Analyzer | Pricing Engineer |
| Phase 2: Pricing | Claude/Generator | Legacy Code Mapping Translator, Pattern Recognition | Ralph/Closer |
| Phase 3: Content | Wagtail Expert | Dependency Graph Mapper | Frontend Architect |
| Phase 3a: SEO | Wagtail Expert | Pattern Recognition | Rate Sheet Agent |
| Phase 4: Rate Sheets | Rate Sheet Agent | Legacy Code Mapping Translator | Pricing Engineer |
| Phase 5: Floify | Frontend Architect | Codebase Structure Analyzer | Pricing Engineer |

---

## 🤖 L2 Agent Skill Inventory

### The Generator (Claude Code)

| Skill ID | Skill Name | Use Case |
|:---------|:-----------|:---------|
| T1-1 | Codebase Structure Analyzer | Map project architecture before modifications |
| T1-2 | Pattern Recognition Engine | Identify design patterns in legacy code |
| T1-3 | Legacy Code Mapping Translator | Port cmtgdirect logic to unified-platform |
| T1-4 | Dependency Graph Mapper | Trace model relationships |

### The Closer (Ralph Loop)

| Capability | Description |
|:-----------|:------------|
| Test Runner | Execute pytest, Jest, Playwright suites |
| Fix Loop | Iteratively modify code until tests pass |
| Verification | Confirm success criteria met |

### The Builder (Jules)

| Capability | Description |
|:-----------|:------------|
| Environment Setup | Docker, dependencies, pre-commit |
| Scaffolding | django-admin, npx create-next-app |
| DevOps | CI/CD, deployment scripts |

---

## 📋 Task-to-Agent Assignment Rules

### Decision Matrix

```
IF task requires:
  - Code generation from analysis → Claude (Generator)
  - Test execution/fix loops → Ralph (Closer)
  - Environment/DevOps setup → Jules (Builder)
  - Orchestration/tracking → Gemini CLI (Orchestrator)
  - Direct command execution → Antigravity
```

### Priority Order

1. **Blocking tasks** → Highest priority agent available
2. **Code generation** → Claude (daytime hours for large context)
3. **Test verification** → Ralph (can run overnight)
4. **Infrastructure** → Jules (async, low priority)

---

## 🔄 Handoff Protocol

### Claude → Ralph Handoff

```markdown
## Handoff Report: [Task Name]
**From**: Claude (Generator)
**To**: Ralph (Closer)
**Track**: [track_id]

### Completed Work
- [x] Item 1
- [x] Item 2

### Files Modified
- `path/to/file1.py` - Description
- `path/to/file2.py` - Description

### Tests to Run
```bash
pytest pricing/tests/test_models.py -v
```

### Success Criteria
- [ ] All tests pass
- [ ] No lint errors
- [ ] Coverage > 80%
```

### Ralph → L1 Orchestrator Handoff

```markdown
## Verification Report: [Task Name]
**Status**: ✅ PASSED | ❌ FAILED

### Test Results
- Tests run: 12
- Passed: 12
- Failed: 0
- Coverage: 87%

### Issues Found
None

### Ready for Next Phase
Yes
```

---

## ✅ Success Criteria Taxonomy

### Tier 1: Automated (Default)

| Criteria | Test Command | Expected |
|:---------|:-------------|:---------|
| Django migrations | `python manage.py makemigrations --check` | No output |
| Unit tests | `pytest -v` | All pass |
| Lint | `flake8 .` | No errors |
| Type check | `mypy .` | No errors |

### Tier 2: Manual

| Criteria | Verifier | Method |
|:---------|:---------|:-------|
| Design approval | L3 Human | Visual review |
| API contract | L3 Human | Swagger review |
| UX flow | L3 Human | Browser walkthrough |

---

## 📁 Checklist Format Standard

All track checklists follow this format:

```markdown
# [Track Name] Checklist

## Phase X: [Phase Name]

- [ ] Task description
  - **Agent**: [Agent Name]
  - **Test**: `command or verification step`
  - **Output**: Expected file or result
```

---

## 🔗 Related Documents

- [workflow.md](file:///home/samalabam/code/unified-cmtg/unified-platform/conductor/workflow.md) - Verification protocols
- [tracks.md](file:///home/samalabam/code/unified-cmtg/unified-platform/conductor/tracks.md) - Track overview
- [tasks.md](file:///home/samalabam/code/unified-cmtg/unified-platform/conductor/tasks.md) - Master task list

---

**Last Updated**: 2026-01-13 00:25 PST
