# Jules Task: Hourly Ralph-Loop Project Sync

**Task ID**: RALPH_SYNC_HOURLY
**Frequency**: Every hour (at :00)
**Purpose**: Automatically synchronize project documentation with git changes
**Owner**: Jules (The Builder)
**Status**: Active

---

## Task Definition

You are responsible for running the ralph-loop project sync every hour to keep project documentation synchronized with actual code state.

### When to Run
- Every hour at :00 (1:00, 2:00, 3:00, etc.)
- Immediately after major commits are pushed
- On-demand if user requests

### What to Do

#### Step 1: Trigger the Ralph-Loop
```bash
cd /home/samalabam/code/unified-cmtg/unified-platform
/ralph-loop:ralph-loop "Sync docs in /home/samalabam/code/unified-cmtg/unified-platform: Run git log -n 10 and git status. Read conductor/tasks.md and conductor/current.md. Update tasks.md by moving completed work to checkmark section and adding new TODOs to pending (auto if under 3 changes, otherwise ask me first). Update current.md with fresh timestamp and completion percentage (auto if under 10 percent change, otherwise ask me). If unsure about anything, STOP and ask: CLARIFICATION NEEDED: [your questions]. Wait for my response then continue. Write summary to SYNC_REPORTS/sync-latest.md. Output SYNC_COMPLETE when git is analyzed and docs match reality." --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

#### Step 2: Capture Output
Save the ralph-loop output to: `/home/samalabam/code/unified-cmtg/.ralph-loop-state/loop-output-YYYY-MM-DD-HH.log`

#### Step 3: Check for Success
Look for: `<promise>SYNC_COMPLETE</promise>` in output
- ✅ If found: Sync succeeded
- ❌ If not found: Check for error messages, log issue

#### Step 4: Commit Results (Optional)
If documentation files were updated:
```bash
cd /home/samalabam/code/unified-cmtg
git add conductor/tasks.md conductor/current.md PROJECT_STATUS_REVIEW.md
git commit -m "chore(ralph): Hourly sync - updated task tracking and project status

[Automated by Jules]
- Analyzed git changes
- Updated task completion status
- Refreshed sprint status
- Generated sync report
"
git push origin main
```

#### Step 5: Update Dashboard Data
Call the dashboard data generator to refresh live metrics:
```bash
/home/samalabam/code/unified-cmtg/scripts/generate-dashboard.sh
```

This updates `/home/samalabam/code/unified-cmtg/dashboard-data.json` so the dashboard shows current info.

#### Step 6: Report Status
Log the sync result:
```bash
echo "[$(date -u +'%Y-%m-%d %H:%M:%SZ')] Ralph-Loop Sync: SUCCESS" >> /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log
```

### Error Handling

**If ralph-loop times out (>6 minutes)**:
- Kill the process: `pkill -f "ralph-loop:ralph-loop"`
- Log the timeout
- Try again next hour

**If sync asks for clarifications**:
- Inform the user immediately via Slack/notification
- Wait for response before continuing
- Store clarification in `.ralph-loop-state/clarifications.json`

**If git commit fails**:
- Don't panic - files are already updated locally
- Log the error
- User can manually push later

### Success Criteria
- ✅ `SYNC_COMPLETE` appears in output
- ✅ Documentation files updated (if changes detected)
- ✅ Dashboard data refreshed
- ✅ Log entry created

### Monitoring

Check sync health with:
```bash
# View latest sync report
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md

# View recent sync logs
tail -20 /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log

# Check dashboard is current
cat /home/samalabam/code/unified-cmtg/dashboard-data.json | jq '.meta.generated_at'
```

### Permissions Needed
- ✅ Read: git history, markdown files
- ✅ Write: conductor/tasks.md, conductor/current.md, PROJECT_STATUS_REVIEW.md, dashboard-data.json
- ✅ Execute: git commands, ralph-loop command, generate-dashboard.sh
- ✅ Network: Push to origin/main (if committing)

### Integration Points

**Receives from**:
- **Git**: Current state of repo (commits, branches)
- **Existing docs**: Current task tracking state

**Outputs to**:
- **conductor/tasks.md**: Updated task status
- **conductor/current.md**: Updated sprint info
- **SYNC_REPORTS/sync-latest.md**: Detailed sync report
- **dashboard-data.json**: Live metrics for dashboard
- **Git commits**: Optional documentation commits

**Notifies**:
- **User**: If clarifications needed
- **Dashboard**: Automatically updated via script
- **Logs**: Status logged to sync-schedule.log

---

## Technical Details

### Ralph-Loop Configuration
- **Mode**: Self-referential feedback loop
- **Max iterations**: 10 (safety limit)
- **Completion signal**: `<promise>SYNC_COMPLETE</promise>`
- **Timeout**: 360 seconds (6 minutes) hard limit
- **Prompt**: Stored in `.ralph-loop-prompts/simple-sync.txt`

### File Paths
- **Prompt file**: `/home/samalabam/code/unified-cmtg/.ralph-loop-prompts/simple-sync.txt`
- **State dir**: `/home/samalabam/code/unified-cmtg/.ralph-loop-state/`
- **Reports dir**: `/home/samalabam/code/unified-cmtg/SYNC_REPORTS/`
- **Docs to update**:
  - `/unified-platform/conductor/tasks.md`
  - `/unified-platform/conductor/current.md`
  - `/PROJECT_STATUS_REVIEW.md`

### Schedule
Triggered by systemd timer on user's machine, or can be triggered by Jules via agent scheduler.

---

## Manual Trigger

User can manually trigger a sync anytime with:
```bash
# Quick request to Jules
@jules run ralph-sync

# Or directly
/ralph-loop:ralph-loop "..." --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

---

## Success Examples

### Example 1: Typical Hourly Sync
```
[00:45] Ralph-Loop Sync: STARTED
[00:46] Git analyzed: 5 commits found
[00:47] Tasks updated: 2 completed, 1 new pending
[00:48] Docs updated: tasks.md, current.md
[00:49] Dashboard refreshed: dashboard-data.json
[00:50] Ralph-Loop Sync: SUCCESS
```

### Example 2: Sync with Clarification
```
[01:45] Ralph-Loop Sync: STARTED
[01:47] CLARIFICATION NEEDED: Found 6 new TODOs - add all or filter?
[USER] Please answer: add all of them
[01:48] Continuing with user guidance...
[01:50] Ralph-Loop Sync: SUCCESS
```

### Example 3: Nothing to Sync
```
[02:45] Ralph-Loop Sync: STARTED
[02:46] Git status: no new commits
[02:47] Docs match reality: no updates needed
[02:48] Ralph-Loop Sync: SUCCESS (no changes)
```

---

## Handoff Format

When passing to another agent or user, include:
- Latest sync report: `SYNC_REPORTS/sync-latest.md`
- Current status: `conductor/current.md`
- Task list: `conductor/tasks.md`
- Any clarifications needed

---

**Created**: 2026-01-16
**Last Updated**: 2026-01-16
**Version**: 1.0
