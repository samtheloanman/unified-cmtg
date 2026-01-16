# Ralph-Loop Project Sync - Usage Guide

## Quick Start

### Run a Full Sync
```bash
/ralph-loop "Execute the project sync workflow from /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync-v2.md" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

This will:
1. Analyze git changes since last sync
2. Update conductor/tasks.md with completed/new tasks
3. Update conductor/current.md with current sprint status
4. Validate and update phase checklists
5. Fix broken links in documentation
6. Generate a sync report
7. Continue iterating until everything is synchronized

**Typical duration**: 3-6 iterations (~5-10 minutes)

---

## When to Run

### Recommended Schedule
- **After major commits**: When you complete a feature or phase
- **Before status meetings**: To have up-to-date task lists
- **After pulling changes**: When other agents (jules, gemini) pushed updates
- **Hourly during active dev**: If lots of changes happening

### Manual Trigger
```bash
# Just type in Claude Code:
/ralph-loop "Execute the project sync workflow from /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync-v2.md" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

### Cancel If Needed
```bash
/cancel-ralph
```

---

## What It Does

### Phase 1: Git Analysis
- Reads last 10 commits
- Identifies changed files (backend, frontend, conductor docs)
- Extracts task signals from commit messages
- Detects TODOs and WIP markers

### Phase 2: Task Updates
- **Reads**: `conductor/tasks.md`
- **Updates**: Moves completed tasks, adds new tasks, updates in-progress
- **Writes**: Updated tasks.md

### Phase 3: Sprint Status
- **Reads**: `conductor/current.md`
- **Updates**: Timestamp, active tasks, completion %, blockers
- **Writes**: Updated current.md

### Phase 4: Checklist Validation
- **Reads**: Each `conductor/tracks/phase*/checklist.md`
- **Checks**: Does code evidence support checklist items?
- **Writes**: Updated checklists with accurate completion status

### Phase 5: Link Validation
- **Checks**: All internal links in modified .md files
- **Fixes**: Broken paths, updates references
- **Writes**: Fixed markdown files

### Phase 6: Status Summary
- **Reads**: `PROJECT_STATUS_REVIEW.md`
- **Updates**: Metrics, phase percentages, activity summary
- **Writes**: Updated status review

### Phase 7: Report Generation
- **Creates**: `SYNC_REPORTS/sync-latest.md`
- **Contains**: Summary of all changes, questions for user, next steps

---

## Understanding the Output

### Iteration Progress
```
=== Iteration 3 ===

[Step 1] Git Status Check... [DONE]
- 5 commits analyzed
- 12 files changed

[Step 2] Code Analysis... [DONE]
- 6 backend changes (models, views, tests)
- 4 frontend changes (components, pages)

[Step 3] Task Reconciliation... [DONE]
- 2 tasks completed (moved to ✅)
- 1 new task added (TODO found)

[Step 4] Sprint Update... [DONE]
- current.md updated (85% → 89%)

[Step 5] Checklist Validation... [DONE]
- Phase 2 checklist: 3 items checked off

[Step 6] Link Validation... [DONE]
- 2 broken links fixed

[Step 7] Status Summary... [DONE]
- PROJECT_STATUS_REVIEW.md updated

[Step 8] Report Generation... [DONE]
- Report: SYNC_REPORTS/sync-latest.md

=== Status ===
✅ Criteria met: 7/8
❌ Remaining: Phase 2 showing 100% complete - needs user verification

Continuing to next iteration...
```

### Completion
```
=== Iteration 4 ===
[All steps DONE]

=== Status ===
✅ All criteria met: 8/8

<promise>SYNC_COMPLETE</promise>
```

When you see `<promise>SYNC_COMPLETE</promise>`, the sync is done!

---

## Reading the Sync Report

After completion, check:
```bash
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md
```

### Key Sections

**Git Changes Analyzed**
- Shows what commits were reviewed
- Files changed counts

**Documentation Updates Made**
- Which files were modified
- Summary of changes

**Task Status Changes**
- Tasks moved to completed
- New tasks discovered
- Tasks updated

**Phase Completion Updates**
- Table showing % changes per phase

**Questions for User** (if any)
- Items that need your decision
- Uncertainties that couldn't be auto-resolved

---

## Decision Framework

### Auto-Updated (No Questions)
- <3 task changes
- Completion % changes <10%
- <5 broken links
- Clear completion evidence (tests exist, commits confirm)
- Routine status updates

### Asks User
- >5 new tasks discovered
- Completion % jumps >10%
- Phase marked 100% complete
- Task stuck in progress >14 days
- >5 broken links
- Uncertain about completion status

### Never Auto-Updates
- Archiving files
- Deleting content
- Changing phase priorities
- Marking phases complete without test evidence

---

## Troubleshooting

### Loop Doesn't Complete
**Symptom**: Hits max-iterations without SYNC_COMPLETE

**Causes**:
- User questions pending (check sync report "Questions for User" section)
- Criteria not met (check final iteration output for ❌ items)
- Files couldn't be read/written

**Fix**:
1. Read sync-latest.md to see what's blocking
2. Answer questions or fix issues manually
3. Run ralph-loop again

### Too Many Questions
**Symptom**: Loop keeps asking for user input

**Causes**:
- Many changes since last sync (>5 tasks)
- Large completion % jumps
- Multiple phases nearing completion

**Fix**: This is normal! Answer questions, or adjust decision thresholds in project-sync-v2.md

### Wrong Files Updated
**Symptom**: Updates made to wrong phase or tasks

**Causes**:
- Commit messages unclear
- Missing phase tags in commits
- Ambiguous code changes

**Fix**: Use structured commit messages:
```bash
git commit -m "feat: Implement rate sheet processor

[Phase 4] Rate Sheet Agent
- Added GeminiAIProcessor
- Tests passing
"
```

### Slow Execution
**Symptom**: Each iteration takes >5 minutes

**Causes**:
- Too many files to analyze
- Git repo very large

**Fix**:
- Commit uncommitted changes to reduce diff size
- Reduce analysis window in prompt (last 10 commits → last 5)

---

## Integration with Other Agents

### Gemini CLI (L1 Orchestrator)
Before delegating tasks:
```bash
# Check latest sync report
cat SYNC_REPORTS/sync-latest.md

# Review current sprint status
cat conductor/current.md

# Check task assignments
cat conductor/tasks.md
```

### Claude Code (L2 Generator)
When completing work:
```bash
# Use structured commit messages for auto-detection
git commit -m "feat: Add loan matching endpoint

[Phase 2] Pricing Engine
- Implemented get_matched_loan_programs API
- Added input validation
- Tests passing (12 new tests)
"

# Then trigger sync to update docs
/ralph-loop "Execute sync..." --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

### Jules (L2 Builder)
After infrastructure changes:
```bash
git commit -m "chore: Update Docker configuration

[Phase 1] Foundation
- Added Redis service
- Updated port mappings
- Health checks configured
"

# Sync will detect and update Phase 1 checklist
```

---

## Best Practices

### 1. Commit Frequently
Small, focused commits = more accurate task detection

✅ Good:
```
feat: Add Lender model
feat: Add LoanProgram model
feat: Add pricing API endpoint
test: Add pricing engine tests
```

❌ Bad:
```
feat: Implement entire pricing engine
```

### 2. Use Conventional Commits
- `feat:` - New features
- `fix:` - Bug fixes
- `test:` - Test additions
- `docs:` - Documentation only
- `chore:` - Infrastructure/config
- `refactor:` - Code restructuring

### 3. Tag Phases
Include `[Phase N]` in commit messages:
```
feat: Add Wagtail page models

[Phase 3] Content Migration
- Created ProgramPage model
- Added StreamFields for content
```

### 4. Mention Test Status
Help auto-detection by mentioning test results:
```
feat: Implement rate sheet extraction

[Phase 4] Rate Sheet Agent
- Added PDF extraction pipeline
- Tests passing (15 new tests, coverage 87%)
```

### 5. Run Sync After Milestones
- Completed a feature → Run sync
- Finished a phase → Run sync
- Before standup/status meeting → Run sync
- After pulling others' changes → Run sync

---

## Customization

### Adjust Decision Thresholds

Edit `/home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync-v2.md`:

```markdown
**Decision Rules:**
- <3 task changes → Auto-update without asking
- 3-5 task changes → Auto-update but notify user in report
- >5 task changes → Ask user to confirm before updating
```

Change to your preference:
```markdown
**Decision Rules:**
- <5 task changes → Auto-update without asking  (more autonomous)
- 5-10 task changes → Auto-update but notify
- >10 task changes → Ask user to confirm
```

### Change Analysis Window

```markdown
- `git log --oneline -n 10` - Recent commits
```

Change to analyze more/fewer commits:
```markdown
- `git log --oneline -n 20` - More history
- `git log --oneline -n 5` - Less history (faster)
```

### Adjust Iteration Limit

```bash
# More iterations (for complex syncs)
--max-iterations 20

# Fewer iterations (for quick checks)
--max-iterations 5
```

---

## FAQ

**Q: How often should I run this?**
A: After significant commits, before status meetings, or hourly during active development.

**Q: Will it overwrite my manual edits?**
A: Only if they conflict with git evidence. It appends/updates, doesn't wholesale replace.

**Q: What if I disagree with an update?**
A: Edit the file manually after sync, or adjust the decision rules in the prompt.

**Q: Can I run multiple syncs simultaneously?**
A: No, ralph-loop runs in your current session. One sync at a time.

**Q: How do I stop a runaway loop?**
A: `/cancel-ralph`

**Q: Does it work with uncommitted changes?**
A: Yes, it analyzes both committed and uncommitted changes.

---

## Version
v2.0 - Ralph-Loop Optimized (2026-01-15)
