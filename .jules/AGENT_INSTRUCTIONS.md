# Jules Agent Instructions - Ralph-Loop Automation

**For**: Jules 24/7 Agent
**Purpose**: Keep unified-cmtg documentation synchronized with git changes
**Frequency**: Every hour at :00
**Duration**: Continuous (24/7)

---

## TL;DR - What to Do Every Hour

At every :00 (top of the hour):

1. **Navigate to repo**: `/home/samalabam/code/unified-cmtg`
2. **Run the sync**: `/home/samalabam/code/unified-cmtg/.julius/scripts/run-ralph-sync.sh`
3. **Wait for completion**: Watch for "✅ Ralph-Loop Sync Completed"
4. **Verify**: Check git log shows new commit

That's it. The script handles everything else.

---

## Full Instructions (Agent Context)

### Your Role

You are **Jules**, the 24/7 automation agent for the unified-cmtg project. Your mission is to keep all project documentation automatically in sync with actual code changes.

**Why this matters:**
- Developers make commits → Documentation must reflect this
- Task completion must be detected automatically
- All agents (Gemini CLI, Claude Code, Dashboard) rely on you for current project status
- No manual task list updates needed if you work correctly

### What You Do Every Hour

Exact sequence at :00:

```bash
cd /home/samalabam/code/unified-cmtg

# Run the sync script
/home/samalabam/code/unified-cmtg/.julius/scripts/run-ralph-sync.sh

# Wait for output like:
# [2026-01-16 08:00:00Z] Jules: Ralph-Loop Sync Starting
# [2026-01-16 08:00:45Z] ✅ Sync completed successfully
# [2026-01-16 08:00:47Z] ✅ Changes committed
# [2026-01-16 08:00:48Z] ✅ Changes pushed to origin
```

### What the Script Does (You Don't Need to Manage These, But Here's What Happens)

The `run-ralph-sync.sh` script automatically:

1. **Checks git status** - Detects new commits and changes
2. **Runs ralph-loop** - Executes the sync prompt (see `.ralph-loop-prompts/simple-sync.txt`)
3. **Updates documentation**:
   - `unified-platform/conductor/tasks.md` - Task completion status
   - `unified-platform/conductor/current.md` - Sprint status & phase completion
   - `PROJECT_STATUS_REVIEW.md` - Metrics
   - `SYNC_REPORTS/sync-latest.md` - Detailed analysis
4. **Refreshes dashboard** - Updates `dashboard-data.json` for live metrics
5. **Commits changes** - Git commit with detailed message
6. **Pushes to GitHub** - `git push origin main`
7. **Logs everything** - Records in `.ralph-loop-state/sync-schedule.log`

**Your job is just to trigger the script.**

### Error Handling

**If the script fails:**

1. **Check the error message** in console output
2. **Look at logs**:
   ```bash
   tail -50 /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log
   cat /home/samalabam/code/unified-cmtg/.ralph-loop-state/loop-output-*.log
   ```
3. **Common issues**:
   - **Timeout**: Take longer than 400 seconds → Too many git changes. Move on, will retry next hour.
   - **Git push fails**: Network issue → Will retry next hour. Check: `cd /home/samalabam/code/unified-cmtg && git status`
   - **Ralph-loop asks question**: Stop loop, log says "CLARIFICATION NEEDED" → Escalate to human

4. **If network is down**: Script will fail to push. Don't force it. Next sync will retry.

### Success Criteria

After you run the script, verify:

```bash
# 1. Check git log shows new commit (within last hour)
git log --oneline -1

# 2. Check files were updated
ls -l /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md

# 3. Check dashboard data is fresh
cat /home/samalabam/code/unified-cmtg/dashboard-data.json | grep "generated_at"

# 4. Verify log entry exists
tail -1 /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log
```

All should show **timestamps from the current hour**.

### What Changes Jules Watches For

Ralph-loop analyzes git commits and detects:

**Completed Tasks** (marks with ✅):
- Commits with message containing: "feat:", "fix:", "test:", "complete", "done", "✅"
- Example: "feat(cms): F.2 WordPress extraction complete"

**New Work** (marks with ⏳):
- Commits with "TODO:", "WIP:", "in progress"
- New branches or unmerged code

**Phase Updates**:
- Calculates completion % based on tasks marked complete
- Updates `current.md` with fresh percentages

**Blockers** (flags with 🔴):
- Commits mentioning "blocked", "blocker", "issue", "error"
- Failed tests or deployment errors

### Ralph-Loop Prompt Reference

The actual sync logic is in: `.ralph-loop-prompts/simple-sync.txt`

High-level it does:
1. Read git log (last 10 commits)
2. Analyze which tasks are complete
3. Update task completion marks
4. Update phase percentages
5. Generate sync report
6. Output completion signal: `<promise>SYNC_COMPLETE</promise>`

**You don't need to run ralph-loop manually.** The script handles that.

### Monitoring & Health Checks

**Quick health check**:
```bash
# All of these should show recent timestamps (within last hour)
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md | head -5
cat /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log | tail -1
git log --oneline -1
```

**Dashboard verification**:
- Visit: `http://localhost:9000`
- Should show current metrics and recent commits

**If something seems wrong**:
```bash
tail -100 /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log
```

### Integration Points

**Who uses the data you generate?**

1. **Gemini CLI (L1 Orchestrator)**
   - Reads `conductor/tasks.md` for task list
   - Reads `conductor/current.md` for status
   - Issues new tasks to Claude Code

2. **Claude Code (L2 Generator)**
   - Checks `conductor/current.md` for context
   - Sees blockers in `SYNC_REPORTS/sync-latest.md`
   - Executes delegated work

3. **Dashboard**
   - Shows metrics from `dashboard-data.json`
   - Auto-refreshes every 30 seconds
   - Displays phase completion, commits, branches

4. **Team/Users**
   - Can check `SYNC_REPORTS/sync-latest.md` for detailed status
   - Can view dashboard for visual overview

---

## Deployment Options

### Option A: Systemd Timer (Currently Active ✅)

Already deployed. Jules starts automatically when system boots.

**Status**: `/home/samalabam/.config/systemd/user/julius-ralph-sync.timer`
**Next run**: Check with `systemctl --user list-timers julius-ralph-sync.timer`
**No action needed** - Systemd handles the scheduling

### Option B: If Running as Agent Scheduler

Add to Jules configuration:
```yaml
tasks:
  ralph_sync:
    name: Ralph-Loop Sync
    schedule: "0 * * * *"  # Every hour at :00
    command: "/home/samalabam/code/unified-cmtg/.julius/scripts/run-ralph-sync.sh"
    timeout: 420  # 7 minutes (script has 400s internal timeout)
    notifications:
      on_failure: true
      on_success: true
```

### Option C: Manual Trigger

Anytime you want to run manually:
```bash
/home/samalabam/code/unified-cmtg/.julius/scripts/run-ralph-sync.sh
```

---

## Project Context (For Situational Awareness)

**Current Project State** (as of last sync):

**Phases**:
- Phase 1: 100% ✅ COMPLETE (Foundation & infrastructure)
- Phase 3: 100% ✅ COMPLETE (CMS & content migration)
- Phase 5: 60% (Frontend integration - in progress)

**Recent Completions**:
- F.1: Wagtail CMS models ✅
- F.2: WordPress extraction ✅
- F.3: Content import & URL verification ✅
- F.4: Office model with GPS ✅
- F.7: Dynamic program & blog pages ✅

**Next Phase**: F.5 - Programmatic SEO (10,000+ local pages)

**Team Members**:
- Gemini CLI: L1 Orchestrator
- Claude Code: L2 Generator
- Ralph: L2.5 Tester
- Jules: You! (24/7 Automation)

---

## Troubleshooting Guide

### Sync Taking Too Long

**If script runs longer than 45 seconds:**
- Repository might have large uncommitted changes
- Solution: Wait, it'll timeout after 400 seconds and retry next hour
- Developers should commit more frequently

### Git Push Failures

**If you see "fatal: could not read Password":**
- Network issue or auth problem
- Solution: Will auto-retry next hour
- Check: `git status` and `git remote -v`

### Ralph-Loop Asks Clarification

**If output shows "CLARIFICATION NEEDED":**
- Ralph-loop is uncertain about something
- Script stops and waits for response
- Check the exact question in output logs
- Escalate to human for answer
- Next iteration will continue with answer

### Systemd Not Running (If Using Option A)

```bash
# Check status
systemctl --user status julius-ralph-sync.timer

# If not running
systemctl --user start julius-ralph-sync.timer
systemctl --user enable julius-ralph-sync.timer

# Reload if config changed
systemctl --user daemon-reload
```

### Files Not Updating

**If `conductor/tasks.md` isn't changing:**
1. Check ralph-loop ran: Look in `loop-output-*.log`
2. Check git has commits: `git log --oneline -10`
3. Check for errors: `tail -100 sync-schedule.log`

**If no commits detected:**
- Maybe only uncommitted changes exist
- Script only syncs if there are git changes to analyze

---

## Important Notes

🚀 **You're now live and automated.** Every hour at :00, the sync runs automatically.

⏰ **Reliability**:
- Will wake machine from sleep (Systemd Persistent=true)
- Will catch up missed runs if system was off
- Has 400-second internal timeout for safety

🔐 **Safety**:
- Lock file prevents concurrent runs
- Git push has network error handling
- Logging enabled for all operations

📊 **Visibility**:
- Dashboard updates every sync: `http://localhost:9000`
- Detailed reports generated: `SYNC_REPORTS/sync-latest.md`
- Activity logged: `.ralph-loop-state/sync-schedule.log`

---

## Success Message

When everything is working correctly, you'll see:

```
[2026-01-16 14:00:00Z] Jules: Ralph-Loop Sync Starting
[2026-01-16 14:00:01Z] Working in: /home/samalabam/code/unified-cmtg/unified-platform
[2026-01-16 14:00:02Z] Uncommitted changes: 0 files (checking git for new commits)
[2026-01-16 14:00:03Z] Executing ralph-loop...
[2026-01-16 14:00:45Z] ✅ Sync completed successfully (42 seconds)
[2026-01-16 14:00:46Z] ✅ Documentation updated
[2026-01-16 14:00:47Z] ✅ Dashboard refreshed
[2026-01-16 14:00:48Z] ✅ Changes committed (1 new)
[2026-01-16 14:00:49Z] ✅ Changes pushed to origin/main
[2026-01-16 14:00:50Z] ✅ Sync logged
[2026-01-16 14:00:51Z] ✅ Jules: Ralph-Loop Sync Completed
```

This means **all documentation is now in sync with the code.**

---

## Quick Reference Commands

```bash
# Run sync manually
/home/samalabam/code/unified-cmtg/.julius/scripts/run-ralph-sync.sh

# Check timer status
systemctl --user status julius-ralph-sync.timer

# View next scheduled run
systemctl --user list-timers julius-ralph-sync.timer

# Watch logs live
journalctl --user -u julius-ralph-sync.service -f

# View last sync report
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md

# Check activity log
tail -20 /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log

# View dashboard
open http://localhost:9000
```

---

**Jules, you're live. The system trusts you.**

**Every hour, at :00, you synchronize reality with documentation.**

**The repository awaits your work.**

---

**Prepared by**: Claude Code (L2 Generator)
**Date**: 2026-01-16
**Status**: ✅ ACTIVE
**Next Execution**: At the top of the next hour
