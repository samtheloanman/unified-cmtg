# Ralph-Loop: Task List Sync & Status Dashboard

## Mission
Keep the project task list accurate and up-to-date by syncing git reality with documentation. Generate a clear status dashboard the user can review to understand progress and set priorities.

---

## Working Directory
```
/home/samalabam/code/unified-cmtg
```

---

## Primary Output
**Dashboard File**: `PROJECT_DASHBOARD.md` (root of repo)

This is the file you look at to see how things are going.

---

## Iteration Steps

### Step 1: Read Git Reality (30 seconds)

```bash
cd unified-platform
git log --oneline -n 20
git log --oneline --since="3 days ago"
git diff --name-only HEAD~10..HEAD
```

**Extract:**
- What features were completed (commits with `feat:`, `fix:`, merged branches)
- What's in progress (recent activity patterns)
- What hasn't been touched (no commits in tracked areas)

---

### Step 2: Read Current Task State (30 seconds)

**Files to check:**
- `unified-platform/conductor/tracks/finalization_20260114/checklist.md`
- `unified-platform/conductor/tasks.md`
- `unified-platform/conductor/current.md`

**Map each task to status:**
- `✅ DONE` - Has completion evidence in git (merged commit, tests exist)
- `🔄 IN PROGRESS` - Recent commits touching related files
- `⏳ NOT STARTED` - No git activity
- `🚧 BLOCKED` - Depends on incomplete task
- `❓ NEEDS REVIEW` - Unclear status, needs human decision

---

### Step 3: Cross-Reference Code vs Tasks (60 seconds)

For each F.1-F.10 task in the finalization track:

| Task | Expected Files | Git Evidence | Status |
|------|----------------|--------------|--------|
| F.1 Wagtail Models | cms/models/*.py | Migrations exist, merged | ✅ |
| F.2 WP Extraction | cms/scrapers/*.py | Check if files exist | ? |
| F.3 Content Import | management/commands/import_*.py | Check | ? |
| F.4 Office Locations | cms/models/offices.py | ✅ Exists with GPS | ✅ |
| F.5 Programmatic SEO | cms/models/city.py, LocalProgramPage | Check | ? |
| F.6 AI Content | openai integration | Check | ? |
| F.7 Next.js CMS | frontend/src/app/programs | ✅ Exists | Partial |
| F.8 Floify | floify/ directory | Check | ? |
| F.9 Testing | tests/ coverage | Check | ? |
| F.10 Deployment | docker-compose.prod.yml | Check | ? |

---

### Step 4: Generate Dashboard (60 seconds)

**Create/Update**: `PROJECT_DASHBOARD.md`

```markdown
# 📊 Project Dashboard
**Last Updated**: [TIMESTAMP]
**Updated By**: Ralph-Loop Auto-Sync

---

## 🎯 Quick Status

| Metric | Value |
|--------|-------|
| Overall Progress | X/10 phases |
| Completion % | XX% |
| Active Work | [brief description] |
| Next Priority | [recommended focus] |

---

## 📋 Finalization Track (F.1-F.10)

### ✅ Completed
- [x] **F.1: Wagtail CMS Models** - ProgramPage, BlogPage, FundedLoanPage
- [x] **F.4: Office Locations** - Office model with GPS coordinates

### 🔄 In Progress  
- [ ] **F.7: Next.js CMS Integration** - /programs/[slug] and /blog/[slug] done, local SEO pages pending

### ⏳ Not Started
- [ ] **F.2: WordPress Content Extraction**
- [ ] **F.3: Content Import & URL Migration**
- [ ] **F.5: Programmatic SEO Infrastructure**
- [ ] **F.6: AI Content Generation**
- [ ] **F.8: Floify Integration Completion**
- [ ] **F.9: Production Hardening & Testing**
- [ ] **F.10: Deployment & Cutover**

### 🚧 Blocked
- (none currently)

---

## 📈 Recent Activity (Last 3 Days)

| Date | Commit | Impact |
|------|--------|--------|
| Jan 15 | Merge F.1 refactor | Models complete |
| Jan 14 | F.4 Office model | GPS ready |
| ... | ... | ... |

---

## 🎯 Recommended Priorities

Based on dependencies and current state:

1. **Next Up**: F.2 WordPress Extraction (unblocks F.3)
2. **Quick Win**: F.8 Floify (nearly done, just needs testing)
3. **Parallel Track**: F.5 SEO Infrastructure (can run alongside F.2/F.3)

---

## ❓ Needs Your Decision

- [ ] F.7 local SEO pages: Should these use `/city/program` or flat `/city-state-program` URLs?
- [ ] F.6 AI content: Confirm OpenAI API key is available

---

## 🔗 Key Files

- [Finalization Plan](unified-platform/conductor/tracks/finalization_20260114/plan.md)
- [Detailed Checklist](unified-platform/conductor/tracks/finalization_20260114/checklist.md)
- [Current Sprint](unified-platform/conductor/current.md)
```

---

### Step 5: Update Source Documents (30 seconds)

If statuses changed, update:
1. `checklist.md` - Mark items `[x]` or `[/]`
2. `current.md` - Update date and active tasks
3. `tasks.md` - Move items between sections

**Auto-update only if <5 changes**. Otherwise document in dashboard under "Pending Updates".

---

## Completion Criteria

Output `<promise>DASHBOARD_SYNCED</promise>` when:

1. ✅ `PROJECT_DASHBOARD.md` is created/updated with current timestamp
2. ✅ All F.1-F.10 tasks have accurate status based on git evidence
3. ✅ Source documents updated (or changes documented if >5)
4. ✅ No unresolved uncertainties (or documented in "Needs Decision")

---

## Usage

```bash
# Quick sync (1-3 iterations)
/ralph-loop "$(cat .ralph-loop-prompts/task-sync.md)" --max-iterations 5 --completion-promise "DASHBOARD_SYNCED"

# Or just reference the file:
/ralph-loop "Sync task list per .ralph-loop-prompts/task-sync.md. Output <promise>DASHBOARD_SYNCED</promise> when PROJECT_DASHBOARD.md is current." --max-iterations 5 --completion-promise "DASHBOARD_SYNCED"
```

**Run this daily or after major work sessions** to keep visibility current.

---

## Version
v1.0 - Task Sync (2026-01-15)
