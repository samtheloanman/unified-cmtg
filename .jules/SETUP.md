# Jules Ralph-Loop Sync - Setup Guide

## Overview

Jules will automatically run the ralph-loop project sync every hour to keep documentation in sync with git changes. This requires minimal configuration.

---

## Quick Start (3 Steps)

### Step 1: Review the Task
```bash
cat /home/samalabam/code/unified-cmtg/.jules/tasks/ralph-loop-hourly-sync.md
```

### Step 2: Test the Runner
```bash
/home/samalabam/code/unified-cmtg/.jules/scripts/run-ralph-sync.sh
```

Expected output:
- ✅ Sync started and completed
- ✅ Documentation files updated
- ✅ Dashboard data refreshed
- ✅ Log entries created

### Step 3: Enable Hourly Execution (Choose One)

## Implementation Options

### Option A: Systemd Timer (Recommended - Auto-wake)

**Benefits**: Runs even if you're asleep, wakes machine from sleep, resilient

#### Setup

1. **Create service file** (`~/.config/systemd/user/jules-ralph-sync.service`):
```ini
[Unit]
Description=Jules Ralph-Loop Project Sync
After=network-online.target

[Service]
Type=oneshot
ExecStart=/home/samalabam/code/unified-cmtg/.jules/scripts/run-ralph-sync.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

2. **Create timer file** (`~/.config/systemd/user/jules-ralph-sync.timer`):
```ini
[Unit]
Description=Jules Ralph-Loop Sync Timer - Hourly
Requires=jules-ralph-sync.service

[Timer]
OnCalendar=hourly
Persistent=true
OnBootSec=5sec
AccuracySec=1s

[Install]
WantedBy=timers.target
```

3. **Enable and start**:
```bash
systemctl --user daemon-reload
systemctl --user enable jules-ralph-sync.timer
systemctl --user start jules-ralph-sync.timer
```

4. **Verify**:
```bash
systemctl --user status jules-ralph-sync.timer
systemctl --user list-timers jules-ralph-sync.timer
```

---

### Option B: Cron Job (Simple - No Wake)

**Benefits**: Simple, industry-standard

#### Setup

1. **Edit crontab**:
```bash
crontab -e
```

2. **Add this line** (runs at :00 every hour):
```bash
0 * * * * /home/samalabam/code/unified-cmtg/.jules/scripts/run-ralph-sync.sh >> /home/samalabam/code/unified-cmtg/.ralph-loop-state/cron.log 2>&1
```

3. **Verify**:
```bash
crontab -l
```

---

### Option C: Jules Agent Scheduler (If Available)

If your Jules instance has an agent scheduler:

```yaml
# Jules configuration
tasks:
  - name: ralph-sync
    schedule: "0 * * * *"  # Every hour at :00
    command: "/home/samalabam/code/unified-cmtg/.jules/scripts/run-ralph-sync.sh"
    notifications: true
```

---

## File Structure

```
.jules/
├── tasks/
│   └── ralph-loop-hourly-sync.md      # Task definition
├── scripts/
│   └── run-ralph-sync.sh              # Execution wrapper (270 lines)
└── SETUP.md                            # This file
```

---

## What Jules Does Hourly

### Every Hour at :00

1. **Check git for changes** - Count uncommitted files
2. **Run ralph-loop** - Execute sync with 10-iteration limit
3. **Capture output** - Save detailed logs
4. **Update docs** - tasks.md, current.md, PROJECT_STATUS_REVIEW.md
5. **Refresh dashboard** - Update dashboard-data.json for live dashboard
6. **Commit if needed** - Git commit with detailed message
7. **Push to origin** - Sync back to GitHub
8. **Log results** - Record success/failure in sync-schedule.log

### Output Files

After each run, you'll find:

```bash
# Latest sync report
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md

# Detailed loop output
ls -lh /home/samalabam/code/unified-cmtg/.ralph-loop-state/loop-output-*.log

# Sync schedule log
tail -f /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log
```

---

## Monitoring Jules

### Check Last Sync
```bash
tail -1 /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log
```

### View Full Today's Log
```bash
cat /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log | grep "$(date +%Y-%m-%d)"
```

### Check Dashboard Currency
```bash
cat /home/samalabam/code/unified-cmtg/dashboard-data.json | jq '.meta.generated_at'
```

### View Latest Report
```bash
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md | head -50
```

### Watch Real-Time Logs
```bash
# If using systemd
journalctl --user -u jules-ralph-sync.service -f

# If using cron
tail -f /home/samalabam/code/unified-cmtg/.ralph-loop-state/cron.log
```

---

## Troubleshooting

### Sync Not Running

**Check if timer/cron is enabled:**
```bash
# Systemd
systemctl --user is-enabled jules-ralph-sync.timer

# Cron
crontab -l | grep ralph-sync
```

**If systemd, restart it:**
```bash
systemctl --user restart jules-ralph-sync.timer
```

### Sync Timing Out

- Ralph-loop has 400 second timeout (6m40s)
- If consistently timing out, there may be too many changes
- Solution: Commit changes more frequently so diffs are smaller

### Git Push Failing

- Happens if network is down or auth issues
- Jules will retry next hour
- Check git status: `cd /home/samalabam/code/unified-cmtg && git status`

### Ralph-Loop Asks for Clarification

Jules will:
1. STOP the sync loop
2. Log "CLARIFICATION NEEDED"
3. Wait for your response
4. Continue in next iteration when you answer

You'll see this in the output log and should respond ASAP.

---

## Customization

### Change Schedule

**Systemd** - Edit timer file:
```ini
[Timer]
OnCalendar=*-*-* 00,06,12,18:00:00  # Run at 12am, 6am, noon, 6pm
```

**Cron** - Edit crontab:
```bash
0 */6 * * *   # Every 6 hours
*/30 * * * *  # Every 30 minutes
```

### Adjust Loop Iterations

In `run-ralph-sync.sh`, change:
```bash
--max-iterations 10  # Increase to 20 for complex syncs
```

### Skip Git Commits

If you don't want Jules to auto-commit, edit `run-ralph-sync.sh` and comment out the commit section (around line 90).

---

## Integration with Dashboard

Jules automatically runs:
```bash
/home/samalabam/code/unified-cmtg/scripts/generate-dashboard.sh
```

This updates the live dashboard with current metrics. The dashboard at `http://localhost:9000` will always show fresh data from the last sync.

---

## Example: First 24 Hours

```
[00:00] ✅ Sync #1 - 3 tasks completed, dashboard updated
[01:00] ✅ Sync #2 - No changes detected
[02:00] ✅ Sync #3 - 1 new task added, committed to git
[03:00] ✅ Sync #4 - No changes
...
[23:00] ✅ Sync #23 - 5 tasks completed, 2 new tasks, committed
```

Each sync is logged and tracked. You can always see the latest status in:
- Dashboard: `http://localhost:9000`
- Reports: `SYNC_REPORTS/sync-latest.md`
- Logs: `sync-schedule.log`

---

## Support & Escalation

If Jules encounters an error:

1. **Check the output log**: `loop-output-*.log` files contain full details
2. **Review the sync report**: `SYNC_REPORTS/sync-latest.md` has context
3. **Check sync-schedule.log** for patterns
4. **Common issues**:
   - Timeout: Too many changes, ask team to commit more
   - Git push failed: Retry manually or wait for next sync
   - Clarification needed: Answer questions in logs

---

## Testing

### Manual Test Run
```bash
/home/samalabam/code/unified-cmtg/.jules/scripts/run-ralph-sync.sh
```

Expected output:
```
[2026-01-16 08:00:00Z] Jules: Ralph-Loop Sync Starting
[2026-01-16 08:00:01Z] Working in: /home/samalabam/code/unified-cmtg/unified-platform
[2026-01-16 08:00:02Z] Uncommitted changes: 4 files
[2026-01-16 08:00:03Z] Executing ralph-loop...
[2026-01-16 08:00:45Z] ✅ Sync completed successfully (42s)
[2026-01-16 08:00:46Z] ✅ Dashboard updated
[2026-01-16 08:00:47Z] ✅ Changes committed
[2026-01-16 08:00:48Z] ✅ Changes pushed to origin
[2026-01-16 08:00:49Z] ✅ Jules: Ralph-Loop Sync Completed
```

### Dry-Run (Check Without Executing)
```bash
# Preview what would happen
cd /home/samalabam/code/unified-cmtg/unified-platform
git status
```

---

## Next Steps

1. **Choose implementation** (Option A/B/C above)
2. **Follow setup steps** for your choice
3. **Test manually**: `/home/samalabam/code/unified-cmtg/.jules/scripts/run-ralph-sync.sh`
4. **Verify it's scheduled**: `systemctl --user list-timers` or `crontab -l`
5. **Monitor first run** by watching logs

---

**Configuration**: Systemd user timer (recommended) or cron job
**Frequency**: Every hour at :00
**Automation Level**: Fully automatic after setup
**Human Intervention**: Only if ralph-loop asks for clarification

---

**Setup created**: 2026-01-16
**Version**: 1.0
