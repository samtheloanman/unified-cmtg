# Ralph-Loop: Jules Orchestrator - Continuous Repo Health & Task Dispatch

## Mission
Act as an L1 Orchestrator that continuously monitors the repository, dispatches tasks to Jules (L2 Builder), tracks their progress, pulls completed work, and keeps documentation in sync. Run until all tracked goals are DONE or user intervenes.

---

## Working Directory
```
/home/samalabam/code/unified-cmtg/unified-platform
```

## Repository
```
samtheloanman/unified-cmtg
```

---

## State Tracking Files

### Primary State
- **Finalization Plan**: `conductor/tracks/finalization_20260114/plan.md`
- **Checklist**: `conductor/tracks/finalization_20260114/checklist.md`
- **Tasks**: `conductor/tasks.md`
- **Current Sprint**: `conductor/current.md`

### Jules Session Tracking
Create/maintain: `.jules/active-sessions.json`
```json
{
  "sessions": [
    {
      "id": "session-uuid",
      "task": "F.2: WordPress Content Extraction",
      "status": "in_progress|completed|awaiting_feedback",
      "created_at": "timestamp",
      "last_checked": "timestamp"
    }
  ]
}
```

---

## Iteration Instructions

Each iteration performs this sequence:

### Phase 1: Git & Codebase Health Check (30 seconds)

```bash
git status
git log --oneline -n 5
git diff --stat HEAD~3..HEAD
```

**Analyze:**
- Are there uncommitted changes that need attention?
- Recent commits - any failures or incomplete work?
- Branch hygiene - are we on main?

**Health Checks:**
```bash
# Backend health
docker compose exec backend python manage.py check --deploy 2>&1 | head -20

# Frontend health
cd frontend && npm run build 2>&1 | tail -20
```

**If unhealthy**: Document issues, consider dispatching fix task to Jules.

---

### Phase 2: Check Active Jules Sessions (60 seconds)

For each session in `.jules/active-sessions.json`:

```bash
jules remote list --session
```

**For each session:**

1. **If status = "completed"**:
   - Pull the diff: `jules remote pull --session <session_id> > .jules/diff-<session_id>.patch`
   - Review diff for safety (no malicious code, matches expected files)
   - If safe: `git apply --index .jules/diff-<session_id>.patch`
   - Commit: `git commit -m "feat: Apply Jules session <session_id> - <task_description>"`
   - Push: `git push origin main`
   - Update checklist.md to mark task completed
   - Remove session from active tracking
   
2. **If status = "awaiting_feedback"**:
   - Document in sync report
   - Notify user that Jules needs input at: `https://jules.google.com/session/<session_id>`
   - Keep session in tracking

3. **If status = "in_progress"**:
   - Update `last_checked` timestamp
   - Continue to next phase

---

### Phase 3: Identify Next Tasks to Dispatch (45 seconds)

**Read**: `conductor/tracks/finalization_20260114/checklist.md`

**Find tasks that are:**
- Marked `[ ]` (not started) or `[/]` (in progress but stalled)
- Tagged for Jules (usually backend/infrastructure work)
- Not already in `.jules/active-sessions.json`

**Priority Order** (based on plan.md waves):
1. F.1: Wagtail CMS Models - ✅ DONE
2. F.2: WordPress Content Extraction - Queue if not done
3. F.3: Content Import & URL Migration
4. F.4: Location & Office Data Import - ✅ DONE
5. F.5: Programmatic SEO Infrastructure
6. F.6: AI Content Generation Pipeline
7. F.7: Next.js CMS Integration (partial - Claude's domain)
8. F.8: Floify Integration Completion
9. F.9: Production Hardening
10. F.10: Deployment

**Decision Framework:**
- Max 2 concurrent Jules sessions (to avoid overwhelming)
- Only dispatch if previous dependencies are DONE
- Skip tasks marked for Claude/Antigravity

---

### Phase 4: Dispatch New Jules Tasks (60 seconds)

For each task to dispatch:

1. **Generate detailed prompt** from checklist item:
   ```
   Task: [Task Name]
   Repository: samtheloanman/unified-cmtg
   Working Directory: unified-platform/backend
   
   Context:
   [Reference relevant files and current state]
   
   Deliverables:
   - [Specific file to create/modify]
   - [Tests to add]
   - [Verification steps]
   
   Success Criteria:
   - [ ] Code compiles/runs
   - [ ] Tests pass
   - [ ] Commits are clean
   ```

2. **Execute**:
   ```bash
   jules remote new --repo samtheloanman/unified-cmtg --session "<task_prompt>"
   ```

3. **Capture session ID** from output and add to `.jules/active-sessions.json`

4. **Update checklist.md**: Mark task as `[/]` (in progress)

---

### Phase 5: Documentation Sync (45 seconds)

**Sync git changes → documentation** (from project-sync-v2.md logic):

1. Analyze recent commits
2. Update `tasks.md` task statuses
3. Update `current.md` with:
   - Today's date
   - Active Jules sessions
   - Current blockers
   - Progress percentage
4. Update `checklist.md` completion marks

**Auto-update rules:**
- <3 changes → Auto-apply
- 3-5 changes → Apply and notify
- >5 changes → Ask user to confirm

---

### Phase 6: Generate Orchestrator Report (30 seconds)

**Create/Update**: `SYNC_REPORTS/orchestrator-latest.md`

```markdown
# Orchestrator Report - [Timestamp]

## Codebase Health
- Backend: ✅ Healthy / ⚠️ Issues
- Frontend: ✅ Healthy / ⚠️ Issues
- Git Status: Clean / Dirty

## Active Jules Sessions
| Session | Task | Status | Age |
|---------|------|--------|-----|
| abc123 | F.2: WP Extraction | in_progress | 2h |

## Completed This Iteration
- [List of merged PRs/applied diffs]

## Dispatched This Iteration
- [List of new Jules tasks created]

## Pending User Action
- [Sessions awaiting feedback]

## Documentation Updated
- tasks.md: [summary]
- current.md: [summary]
- checklist.md: [summary]

## Next Actions
- [What next iteration will focus on]

## Finalization Track Progress
| Phase | Status | Notes |
|-------|--------|-------|
| F.1 | ✅ | Completed |
| F.2 | 🔄 | Jules session active |
| ... | ... | ... |
```

---

## Completion Criteria

Output `<promise>FINALIZATION_COMPLETE</promise>` when **ALL** of the following are true:

1. ✅ All F.1 through F.10 tasks in checklist.md are marked `[x]`
2. ✅ No active Jules sessions (all completed and merged)
3. ✅ Codebase health checks pass (backend + frontend)
4. ✅ All documentation is in sync with code
5. ✅ Git status is clean (no uncommitted changes)
6. ✅ PROJECT_STATUS_REVIEW.md reflects 100% completion

**If blocked on user action**:
- Output: `<blocked>AWAITING_USER: <reason></blocked>`
- Continue monitoring, don't exit loop

---

## Safety Limits

- **Max iterations**: 50 (prevents runaway)
- **Max concurrent Jules sessions**: 2
- **Iteration cooldown**: 5 minutes between iterations (avoid rate limits)
- **Auto-apply threshold**: <3 changes (higher needs user confirmation)
- **Never auto-deploy**: Always require explicit user approval for F.10

---

## Self-Correction Rules

- **Jules error**: Retry once, then document and continue
- **Git conflict**: Stop, document, ask user
- **Health check fail**: Log but continue (don't block on warnings)
- **Session timeout (>24h)**: Mark as stale, ask user whether to cancel

---

## Usage

```bash
# Start the orchestrator loop (max 50 iterations, ~4 hour runtime with cooldowns)
/ralph-loop "$(cat .ralph-loop-prompts/jules-orchestrator.md)" --max-iterations 50 --completion-promise "FINALIZATION_COMPLETE"

# Or with inline file reference:
/ralph-loop "Execute the Jules Orchestrator workflow in .ralph-loop-prompts/jules-orchestrator.md. Follow all phases and output <promise>FINALIZATION_COMPLETE</promise> when all F.1-F.10 tasks are done." --max-iterations 50 --completion-promise "FINALIZATION_COMPLETE"
```

---

## Command & Control Hierarchy

This workflow implements the L1 Orchestrator role:

- **L1 (This Loop)**: Gemini CLI + ralph-loop = Project Manager
- **L2 (Jules)**: Backend/Infrastructure Worker
- **L2 (Claude)**: Frontend Worker (dispatched separately via Antigravity)
- **L3 (Human)**: Final approval for deployments

---

## Version
v1.0 - Jules Orchestrator (2026-01-15)
