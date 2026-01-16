# Jules Ralph-Loop Sync Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Jules (24/7 Agent)                          │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Hourly Trigger (Systemd Timer or Cron)                      │  │
│  │  Time: Every hour at :00                                      │  │
│  │  Command: /home/samalabam/code/unified-cmtg/.jules/scripts   │  │
│  │           /run-ralph-sync.sh                                 │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Ralph-Loop Project Sync                                      │  │
│  │  ┌───────────────────────────────────────────────────────┐   │  │
│  │  │ Iteration Loop (max 10 iterations, 6min timeout)      │   │  │
│  │  │                                                         │   │  │
│  │  │ Step 1: Analyze git changes (git log -n 10)           │   │  │
│  │  │ Step 2: Read conductor/tasks.md, current.md           │   │  │
│  │  │ Step 3: Update tasks.md with completions              │   │  │
│  │  │ Step 4: Update current.md with status & timestamp     │   │  │
│  │  │ Step 5: Update PROJECT_STATUS_REVIEW.md               │   │  │
│  │  │ Step 6: Generate SYNC_REPORTS/sync-latest.md          │   │  │
│  │  │ Step 7: Output <promise>SYNC_COMPLETE</promise>        │   │  │
│  │  │                                                         │   │  │
│  │  │ If uncertain: Ask CLARIFICATION NEEDED (waits for user)│   │  │
│  │  └───────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Post-Sync Actions                                            │  │
│  │  • Generate dashboard-data.json (for live dashboard)         │  │
│  │  • Git add + commit (if changes detected)                    │  │
│  │  • Git push to origin/main                                   │  │
│  │  • Log results to sync-schedule.log                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    Unified CMTG Repository                          │
│                                                                       │
│  Git Commits ──┐                                                     │
│                ├──> Ralph-Loop ────> conductor/tasks.md             │
│  Code Changes ─┤                      conductor/current.md          │
│                ├──> Analysis          PROJECT_STATUS_REVIEW.md      │
│                ├──> Dashboard Data ──> dashboard-data.json          │
│  Documentation ┤                      SYNC_REPORTS/sync-latest.md   │
│                └──> Git Commits ────> origin/main                   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        Live Dashboard                               │
│                     (http://localhost:9000)                         │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Phase Progress | Docker Containers | Recent Commits         │   │
│  │ Project Stats  | Git Branches      | System Status          │   │
│  │                                                               │   │
│  │ Auto-updates every 30 seconds from dashboard-data.json       │   │
│  │ (refreshed by Jules every hour)                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Hour 0 (Initial State)
```
Git State:        5 new commits, 8 files changed
Documentation:    tasks.md (outdated), current.md (stale)
Dashboard:        Last updated 1 hour ago
```

### Hour 1 (Jules Runs)
```
Input:
  ├─ Git: 5 new commits analyzed
  ├─ Existing: tasks.md, current.md
  └─ Ralph-Loop: Simple-sync prompt

Process:
  ├─ Iteration 1: Read git, analyze changes
  ├─ Iteration 2: Update task completion
  ├─ Iteration 3: Update sprint status
  ├─ Iteration 4: Generate report
  └─ Iteration 5: Output SYNC_COMPLETE

Output:
  ├─ ✅ conductor/tasks.md (2 new ✅, 1 new ⏳)
  ├─ ✅ conductor/current.md (timestamp updated, % changed)
  ├─ ✅ PROJECT_STATUS_REVIEW.md (metrics updated)
  ├─ ✅ SYNC_REPORTS/sync-latest.md (detailed report)
  ├─ ✅ dashboard-data.json (live dashboard refreshed)
  ├─ ✅ Git commit (documentation update)
  └─ ✅ Git push (origin/main)

Result:
  ├─ Documentation synchronized with code
  ├─ Dashboard shows current metrics
  ├─ All agents see up-to-date status
  └─ Changes persisted to GitHub
```

---

## Comparison: Dashboard vs Jules Sync

### Dynamic Dashboard Server (antigravity)
```
Purpose:  Display current project status
Runs:     Continuously (Node.js server on port 9000)
Updates:  Every 30 seconds (polling)
Data:     Docker containers, git commits, branches
Source:   Real-time scripts (docker ps, git log, etc.)
For:      Visual monitoring, status overview
```

### Jules Ralph-Loop Sync (24/7 Agent)
```
Purpose:  Keep documentation in sync with code
Runs:     Hourly (at :00 every hour)
Updates:  Once per hour
Data:     Git changes, task completion, sprint status
Source:   Ralph-loop analysis + generation
For:      Accurate task tracking, automated reports
```

### How They Work Together
```
Jules Sync (Hourly) ──────┐
                          ├──> Generates dashboard-data.json
Dashboard Server (Live) ──┤
                          └──> Dashboard displays on port 9000
                                (auto-refreshes every 30s)
```

---

## Integration Points

### Input Sources
1. **Git Repository** - Jules reads commits, branches, status
2. **Existing Documentation** - conductor/tasks.md, current.md
3. **Ralph-Loop Prompt** - simple-sync.txt provides analysis logic
4. **Project Files** - cms/models.py, frontend pages, etc.

### Output Targets
1. **Task Tracking** - conductor/tasks.md (updated status)
2. **Sprint Status** - conductor/current.md (fresh timestamp)
3. **Project Metrics** - PROJECT_STATUS_REVIEW.md (completion %)
4. **Sync Reports** - SYNC_REPORTS/sync-latest.md (detailed)
5. **Live Dashboard** - dashboard-data.json (metrics)
6. **Git History** - origin/main (committed changes)
7. **Activity Log** - sync-schedule.log (execution record)

### Who Uses It
```
User/Team ─────────────┐
                       ├─> Read sync-latest.md for detailed report
Cloud Agents (Gemini)  ┤   Read conductor/tasks.md for status
                       ├─> Check dashboard at http://localhost:9000
Antigravity Jules      ─┘   Execute sync every hour
```

---

## Execution Timeline

### Every Hour at :00

```
:00    Jules wakes up
:01    Checks git status
:02    Runs ralph-loop (analysis + generation)
:05    Ralph-loop completes
:06    Updates documentation files
:07    Refreshes dashboard data
:08    Commits changes to git
:09    Pushes to origin/main
:10    Logs completion
       Ready for next hour

Total: ~9-10 seconds (usually)
Max:   ~400 seconds (6m40s timeout safety limit)
```

---

## Error Handling & Resilience

### If Ralph-Loop Times Out
- Killed after 400 seconds
- Logged as timeout
- Retried next hour
- No data loss (files not partially updated)

### If Git Push Fails
- Files already updated locally
- Will retry next hour automatically
- User can manually push if urgent
- Dashboard still shows fresh data

### If Ralph-Loop Needs Clarification
- Stops and asks user
- Waits for response in the logs
- Continues with next iteration
- Completes when questions answered

### If Jules Crashes
- Systemd timer automatically restarts
- No missed syncs (Persistent=true catches up)
- Previous sync results preserved

---

## Monitoring & Observability

### What You Can See

**Real-time Dashboard** (every 30s):
```bash
http://localhost:9000
```

**Latest Sync Report** (every hour):
```bash
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md
```

**Activity Log** (continuous):
```bash
tail -f /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log
```

**Task Status** (updated hourly):
```bash
cat /home/samalabam/code/unified-cmtg/unified-platform/conductor/tasks.md
```

**Sprint Status** (updated hourly):
```bash
cat /home/samalabam/code/unified-cmtg/unified-platform/conductor/current.md
```

---

## Customization Options

### Change Frequency
Systemd: Edit `OnCalendar=` in timer
Cron: Edit crontab schedule

### Disable Auto-Commit
Edit `run-ralph-sync.sh`, comment commit section

### Adjust Iteration Limit
Edit `--max-iterations 10` to higher number for complex syncs

### Skip Dashboard Update
Edit `run-ralph-sync.sh`, comment out generate-dashboard.sh call

---

## Success Metrics

Jules is working well if:

✅ `sync-schedule.log` shows hourly entries
✅ `SYNC_REPORTS/sync-latest.md` updates hourly
✅ Dashboard shows fresh timestamps
✅ Documentation files change when code changes
✅ Zero manual intervention needed
✅ Git commits appear hourly
✅ Systemd timer shows "next run" times

---

## Architecture Decisions

### Why Ralph-Loop?
- Self-referential: sees its own previous work
- Iterative: can refine answers over iterations
- Accurate: analyzes code not just commits
- Safe: max iterations prevent runaway loops

### Why Hourly?
- Frequent enough to catch all changes
- Infrequent enough to avoid overhead
- Aligns with typical commit patterns
- Manageable log size

### Why Jules?
- 24/7 availability (doesn't sleep)
- In the repository (no external agent)
- Can push to git
- Can wake machine from sleep (with systemd)

### Why Systemd Over Cron?
- Catches up missed runs (Persistent=true)
- Can wake system from sleep
- Better error handling
- Journal integration for logs

---

## Future Enhancements

1. **Automated Phase Sync**: Pull phase completion % directly from analyze code
2. **Slack Notifications**: Notify team of major status changes
3. **GitHub Issues**: Auto-create issues for blockers
4. **Metrics Export**: Export to monitoring system
5. **Parallel Syncs**: Run multiple sync instances for different areas

---

**Version**: 1.0
**Created**: 2026-01-16
**Last Updated**: 2026-01-16
