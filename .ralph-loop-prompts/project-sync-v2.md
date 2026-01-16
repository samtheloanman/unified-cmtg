# Ralph-Loop: Git-Driven Project Documentation Sync

## Mission
Perform a complete synchronization between git changes and project documentation/task tracking for unified-cmtg/unified-platform. Run until all tracking files accurately reflect current code state.

---

## Working Directory
```
/home/samalabam/code/unified-cmtg/unified-platform
```

---

## Iteration Instructions

Each iteration, perform these steps in sequence:

### 1. Git Status Check (30 seconds)

Read git status and recent history:
- `git status` - Check for uncommitted changes
- `git log --oneline -n 10` - Recent commits
- `git diff --stat HEAD~5..HEAD` - Files changed in last 5 commits
- `git diff --name-only` - Unstaged changes

**Analyze for:**
- New features (models, APIs, components)
- Bug fixes
- Refactorings
- Tests added/modified
- Documentation changes

### 2. Code Change Analysis (60 seconds)

For files changed in last 5-10 commits, identify:

**Backend Changes** (`backend/**/*.py`):
- New models → Feature additions
- New views/endpoints → API completions
- New tasks → Background job implementations
- Test files → Coverage improvements

**Frontend Changes** (`frontend/src/**`):
- New pages → User-facing features
- New components → UI implementations
- API client updates → Backend integrations
- Test files → Quality improvements

**Extract Signals:**
- Commit messages with `feat:`, `fix:`, `test:` → Task status changes
- TODOs in code → New pending tasks
- Test files created → Feature completion signals
- Phase tags like `[Phase 2]` → Phase associations

### 3. Task List Reconciliation (60 seconds)

**Read**: `/home/samalabam/code/unified-cmtg/unified-platform/conductor/tasks.md`

**Update based on git analysis:**

- Move tasks to "Completed ✅" if:
  - Commit message mentions feature completion
  - Tests exist for the feature
  - Code implements the full requirement

- Add to "Pending ⏳" if:
  - TODOs found in new commits
  - WIP commits without completion
  - New requirements discovered

- Update "In Progress 🟡" if:
  - Recent commits working on specific tasks
  - Incremental progress detected

**Decision Rules:**
- <3 task changes → Auto-update without asking
- 3-5 task changes → Auto-update but notify user in report
- >5 task changes → Ask user to confirm before updating

**Write back** the updated tasks.md file.

### 4. Current Sprint Status Update (45 seconds)

**Read**: `/home/samalabam/code/unified-cmtg/unified-platform/conductor/current.md`

**Update:**
- Last updated date → Current timestamp
- Active tasks → Cross-reference with tasks.md "In Progress"
- Blockers → Check for commit messages mentioning issues/blocked
- Completion % → Calculate from tasks.md ratios

**Decision Rules:**
- % change <10% → Auto-update
- % change >10% → Ask user to confirm
- New blockers detected → Auto-add and notify
- Sprint >7 days old → Ask if new sprint should start

**Write back** the updated current.md file.

### 5. Phase Checklist Validation (60 seconds)

For each phase directory in `/home/samalabam/code/unified-cmtg/unified-platform/conductor/tracks/phase*/`:

**Read**: `checklist.md`

**Check completion:**
- Compare checklist items against actual code
- Look for evidence of completion (files exist, tests pass indicators, commits mention completion)

**Update if needed:**
- Check off items with clear completion evidence
- Add new items discovered in code
- Update phase completion %

**Decision Rules:**
- Individual items with clear evidence → Auto-check
- Phase reaching 100% → Ask user to verify
- New items discovered → Auto-add if <3, else ask

**Write back** updated checklists.

### 6. Cross-Reference Validation (30 seconds)

For any modified `.md` files, check internal links:

```bash
# Extract markdown links
grep -oP '\[.*?\]\(\K[^)]+' modified-file.md

# Check if file paths exist
# Fix broken links if found
```

**Decision Rules:**
- <5 broken links → Auto-fix by updating paths
- >5 broken links → Report and ask for guidance

### 7. Project Status Summary (30 seconds)

**Read**: `/home/samalabam/code/unified-cmtg/PROJECT_STATUS_REVIEW.md`

**Update metrics:**
- Last review date
- Phase completion percentages (from checklists)
- Recent activity summary (from git log)

**Auto-update** - this is a generated file.

### 8. Generate Sync Report (30 seconds)

**Create**: `/home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md`

Include:
```markdown
# Project Sync Report - [Timestamp]

## Git Changes Analyzed
- Commits: [count]
- Files changed: [count]
- Backend changes: [count]
- Frontend changes: [count]

## Documentation Updates Made
- tasks.md: [changes summary]
- current.md: [changes summary]
- Checklists: [list of updated phases]

## Task Status Changes
### Completed ✅
- [list tasks moved to completed]

### Added ⏳
- [list new tasks discovered]

### Updated 🟡
- [list tasks updated]

## Phase Completion Updates
| Phase | Old % | New % | Change |
|-------|-------|-------|--------|
| Phase 1 | X% | Y% | ±Z% |

## Issues Detected
- [Any blockers, broken links, uncertainties]

## Questions for User
[Only if decision framework triggered "ask user"]
1. [Question with context]

## Next Iteration Focus
[What to check next, if not complete]
```

---

## Completion Criteria

Output `<promise>SYNC_COMPLETE</promise>` when **ALL** of the following are true:

1. ✅ All git changes from last 10 commits have been analyzed
2. ✅ tasks.md accurately reflects code state (no missed completions)
3. ✅ current.md has current timestamp and accurate status
4. ✅ All phase checklists match actual code implementation
5. ✅ No broken internal links in modified .md files
6. ✅ PROJECT_STATUS_REVIEW.md has current metrics
7. ✅ Sync report generated with summary
8. ✅ No uncertainty requiring user input (OR questions documented in report)

**If ANY criterion is not met**, continue to next iteration and address gaps.

---

## Self-Correction Rules

If previous iteration had issues:

- **Read failed** → Try alternative file paths
- **Git command failed** → Verify working directory is correct
- **Uncertain about task status** → Check for more evidence (tests, commit messages)
- **Can't determine completion** → Document in sync report, mark as needs-review
- **File write failed** → Check permissions, try again
- **Too many changes** → Break into smaller chunks, ask user

---

## Safety Limits

- **Max iterations**: 10 (set via --max-iterations flag)
- **Max file reads per iteration**: 20 files
- **Timeout per iteration**: 5 minutes
- **Auto-update threshold**: <3 changes (higher = ask user)

---

## Output Format

Each iteration should output:

```
=== Iteration N ===

[Step 1] Git Status Check... [DONE]
- X commits analyzed
- Y files changed

[Step 2] Code Analysis... [DONE]
- Z backend changes
- W frontend changes

[Step 3] Task Reconciliation... [DONE]
- A tasks completed
- B tasks added

[Step 4] Sprint Update... [DONE]
- current.md updated (85% → 92%)

[Step 5] Checklist Validation... [DONE]
- Phase 2 checklist updated

[Step 6] Link Validation... [DONE]
- 0 broken links

[Step 7] Status Summary... [DONE]
- PROJECT_STATUS_REVIEW.md updated

[Step 8] Report Generation... [DONE]
- Report: SYNC_REPORTS/sync-latest.md

=== Status ===
✅ Criteria met: 7/8
❌ Remaining: User confirmation needed for Phase 2 completion

Continuing to next iteration...
```

**Final iteration outputs:**
```
=== Iteration N ===
[All steps DONE]

=== Status ===
✅ All criteria met: 8/8

<promise>SYNC_COMPLETE</promise>
```

---

## Usage

```bash
# Run the sync loop (max 10 iterations, safety limit)
/ralph-loop "$(cat /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync-v2.md)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"

# Or if file is too long, use a reference prompt:
/ralph-loop "Execute the project sync workflow defined in /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync-v2.md. Follow all steps and output <promise>SYNC_COMPLETE</promise> when all criteria are met." --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

---

## Expected Behavior

- **Iteration 1**: Read git changes, analyze code, update tasks.md and current.md
- **Iteration 2**: Review what was updated, validate accuracy, update checklists
- **Iteration 3**: Cross-check everything, fix any inconsistencies
- **Iterations 4-5**: Handle edge cases, user questions, final validation
- **Iteration 6**: Generate final report and output SYNC_COMPLETE

Typical completion: **3-6 iterations**

---

## Version
v2.0 - Ralph-Loop Optimized (2026-01-15)
