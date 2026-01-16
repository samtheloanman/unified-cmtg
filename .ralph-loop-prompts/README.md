# Ralph-Loop Project Sync System

Git-driven documentation synchronization for unified-cmtg using Claude Code's ralph-wiggum plugin.

## Overview

This system keeps your project documentation (tasks, checklists, status reports) automatically synchronized with your git commit history using a self-referential AI feedback loop.

**How it works:**
1. You make commits with code changes
2. Run `/ralph-loop` with the sync prompt
3. Claude analyzes git history and code changes
4. Documentation files automatically update to reflect reality
5. Loop continues until everything is synchronized

## Files in This Directory

- **`project-sync-v2.md`** - Full detailed sync workflow (comprehensive)
- **`quick-sync.txt`** - Condensed reference prompt (fast)
- **`USAGE.md`** - Complete usage guide with examples
- **`README.md`** - This file

## Quick Start

### Option 1: Full Sync (Recommended)
```bash
/ralph-loop "Execute the project sync workflow from /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync-v2.md" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

**Use when**: Major changes, multiple commits, end of work session

### Option 2: Quick Sync (Fast)
```bash
/ralph-loop "$(cat /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/quick-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

**Use when**: Quick check, minor changes, hourly updates

## What Gets Updated

### 1. Task Tracking
**File**: `unified-platform/conductor/tasks.md`

**Updates**:
- Completed tasks (✅) - Auto-detected from commits with tests
- New tasks (⏳) - Extracted from TODOs and WIP commits
- In-progress (🟡) - Based on recent commit activity

### 2. Sprint Status
**File**: `unified-platform/conductor/current.md`

**Updates**:
- Current date/timestamp
- Active tasks list
- Completion percentage
- Blockers (from commit messages mentioning issues)

### 3. Phase Checklists
**Files**: `unified-platform/conductor/tracks/phase*/checklist.md`

**Updates**:
- Checks off completed items with code evidence
- Adds newly discovered tasks
- Updates phase completion percentages

### 4. Project Status
**File**: `PROJECT_STATUS_REVIEW.md`

**Updates**:
- Phase completion metrics
- Recent activity summary
- Commit counts and change statistics

### 5. Sync Reports
**File**: `SYNC_REPORTS/sync-latest.md`

**Contains**:
- Summary of all updates made
- Git changes analyzed
- Questions for user (if any)
- Next steps

## When to Run

### Recommended Schedule

**After Major Milestones**
```bash
# Completed a feature
git commit -m "feat: Implement rate sheet extraction [Phase 4]"
/ralph-loop "$(cat quick-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

**Hourly During Active Dev**
```bash
# Set a reminder to run every hour if many changes
/ralph-loop "$(cat quick-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

**Before Status Meetings**
```bash
# Get up-to-date task lists and metrics
/ralph-loop "Execute sync from project-sync-v2.md" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

**After Pulling Changes**
```bash
# Other agents (jules, gemini) pushed updates
git pull
/ralph-loop "$(cat quick-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

## How It Works

### Self-Referential Feedback Loop

1. **Iteration 1**: Read git changes → Update task files
2. **Iteration 2**: Read updated task files → Validate accuracy → Fix issues
3. **Iteration 3**: Read fixes → Validate again → Update checklists
4. **Iteration 4**: Read everything → Cross-validate → Generate report
5. **Iteration 5**: Final check → All criteria met → `<promise>SYNC_COMPLETE</promise>`

Each iteration sees the results of previous iterations and self-corrects.

### Git as Source of Truth

The system uses git history to automatically detect:

**Feature Completion**
```bash
git commit -m "feat: Add loan matching API

[Phase 2] Pricing Engine
- Implemented get_matched_loan_programs
- Added input validation
- Tests passing (15 new tests)
"
```
→ Task "Implement loan matching API" moved to Completed ✅

**New Tasks**
```python
# TODO: Add rate adjustment calculations
def calculate_adjusted_rate():
    pass
```
→ New task "Add rate adjustment calculations" added to Pending ⏳

**Work in Progress**
```bash
git commit -m "wip: Working on Floify integration [Phase 5]"
```
→ Task "Floify integration" added to In Progress 🟡

## Decision Framework

### Autonomous Updates (No User Input)
- <3 task status changes
- Completion % changes <10%
- <5 broken links found
- Clear evidence of completion (tests exist + pass)
- Routine metric updates

### Asks User
- >5 new tasks discovered
- Completion % jumps >10%
- Phase marked 100% complete
- Task in progress >14 days
- Uncertain about completion status

### Never Autonomous
- Archiving files
- Deleting content
- Changing phase priorities
- Marking complete without test evidence

## Reading the Results

### Check Sync Report
```bash
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md
```

**Key sections:**
- **Git Changes Analyzed** - What was reviewed
- **Documentation Updates** - What was changed
- **Task Status Changes** - Completions, additions, updates
- **Questions for User** - Items needing your decision

### Check Updated Tasks
```bash
cat /home/samalabam/code/unified-cmtg/unified-platform/conductor/tasks.md
```

See your completed tasks (✅), new tasks (⏳), and in-progress work (🟡).

### Check Phase Status
```bash
cat /home/samalabam/code/unified-cmtg/unified-platform/conductor/tracks/phase2_pricing/checklist.md
```

See updated completion status for specific phases.

## Best Practices

### 1. Use Structured Commit Messages
```bash
# Good - Auto-detectable
git commit -m "feat: Implement feature X [Phase N]"
git commit -m "fix: Bug in module Y [Phase N]"
git commit -m "test: Add tests for Z [Phase N]"

# Bad - Hard to detect
git commit -m "updates"
git commit -m "more work"
```

### 2. Include Phase Tags
```bash
[Phase 1] Foundation
[Phase 2] Pricing Engine
[Phase 3] Content Migration
[Phase 4] Rate Sheet Agent
[Phase 5] Floify Integration
```

### 3. Mention Test Status
```bash
git commit -m "feat: Add API endpoint

[Phase 2] Pricing Engine
- Created quote endpoint
- Added validation
- Tests passing (10 new tests, 85% coverage)
"
```

### 4. Commit Frequently
Small, focused commits = more accurate detection
```bash
# Good (3 commits)
git commit -m "feat: Add model"
git commit -m "feat: Add API endpoint"
git commit -m "test: Add tests"

# Less ideal (1 commit)
git commit -m "feat: Add entire feature with model, API, tests"
```

### 5. Review Sync Reports
Always check `SYNC_REPORTS/sync-latest.md` after sync to:
- Verify updates are correct
- Answer any questions
- Understand what changed

## Troubleshooting

### Loop Doesn't Complete

**Check**: Final iteration output for ❌ items
```
=== Status ===
✅ Criteria met: 7/8
❌ Remaining: User confirmation needed for Phase 2 completion
```

**Fix**: Check sync report for questions, answer them, run again

### Too Many Questions

**Cause**: Many changes since last sync (>5 tasks, >10% completion jump)

**Fix**: Normal behavior! Answer questions in the report, or adjust thresholds in `project-sync-v2.md`

### Wrong Updates

**Cause**: Unclear commit messages, missing phase tags

**Fix**: Use structured commit messages (see Best Practices above)

### Slow Execution

**Cause**: Too many uncommitted files, large git history

**Fix**:
```bash
# Commit pending changes
git add .
git commit -m "chore: Sync pending work"

# Or reduce analysis window in prompt (10 commits → 5 commits)
```

### Cancel If Needed
```bash
/cancel-ralph
```

## Integration with Multi-Agent Workflow

### Gemini CLI (L1 Orchestrator)
Before delegating tasks:
```bash
cat SYNC_REPORTS/sync-latest.md  # Check latest status
cat conductor/current.md          # Check sprint status
cat conductor/tasks.md            # Check task assignments
```

### Claude Code (L2 Generator)
After completing work:
```bash
git commit -m "feat: Implemented X [Phase N] - tests passing"
/ralph-loop "$(cat quick-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

### Jules (L2 Builder)
After infrastructure changes:
```bash
git commit -m "chore: Updated Docker config [Phase 1]"
/ralph-loop "$(cat quick-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

## Examples

### Example 1: After Implementing a Feature
```bash
# You just finished implementing loan matching API
git add backend/api/views.py backend/api/tests/test_views.py
git commit -m "feat: Implement loan matching API

[Phase 2] Pricing Engine
- Added get_matched_loan_programs endpoint
- Input validation for qualification data
- Tests passing (12 new tests, coverage 89%)
"

# Run sync
/ralph-loop "$(cat /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/quick-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"

# Check results
cat SYNC_REPORTS/sync-latest.md
# Should show: Task "Implement loan matching API" moved to Completed ✅
```

### Example 2: Hourly Maintenance Sync
```bash
# Quick check for any changes
/ralph-loop "$(cat /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/quick-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"

# Typical output:
# - 3 commits analyzed
# - 1 task completed
# - Phase 2: 85% → 89%
# - <promise>SYNC_COMPLETE</promise>
```

### Example 3: Before Status Meeting
```bash
# Full comprehensive sync
/ralph-loop "Execute the project sync workflow from /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync-v2.md" --max-iterations 10 --completion-promise "SYNC_COMPLETE"

# Review comprehensive report
cat SYNC_REPORTS/sync-latest.md

# Share updated status
cat conductor/current.md
cat PROJECT_STATUS_REVIEW.md
```

## Customization

Edit `project-sync-v2.md` to adjust:

- **Decision thresholds**: Change auto-update limits
- **Analysis window**: More/fewer commits to analyze
- **Max iterations**: Safety limits
- **File locations**: Custom paths
- **Completion criteria**: What constitutes "done"

See `USAGE.md` for detailed customization instructions.

## Support

For issues or questions:
1. Check `USAGE.md` for detailed troubleshooting
2. Review `project-sync-v2.md` for full workflow specification
3. Check sync logs in `SYNC_REPORTS/sync-latest.md`
4. Ask Claude Code for help with specific error messages

## Version History

- **v2.0** (2026-01-15): Ralph-loop optimized design
  - Self-referential feedback loop
  - Git-driven task detection
  - Autonomous decision framework
  - Hourly maintenance capability

---

**Quick Command Reference:**

```bash
# Full sync
/ralph-loop "Execute sync from /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync-v2.md" --max-iterations 10 --completion-promise "SYNC_COMPLETE"

# Quick sync
/ralph-loop "$(cat /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/quick-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"

# Cancel
/cancel-ralph
```
