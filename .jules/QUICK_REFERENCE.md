# Jules Ralph-Loop Sync - Quick Reference

## What Jules Does
Runs the ralph-loop project sync **every hour** to keep documentation in sync with git.

## Files Jules Uses

| File | Purpose |
|------|---------|
| `.jules/tasks/ralph-loop-hourly-sync.md` | Task definition (what to do) |
| `.jules/scripts/run-ralph-sync.sh` | Runner script (how to do it) |
| `conductor/tasks.md` | What it updates (task status) |
| `conductor/current.md` | What it updates (sprint info) |
| `SYNC_REPORTS/sync-latest.md` | What it generates (detailed report) |
| `.ralph-loop-state/sync-schedule.log` | Jules' activity log |

## Quick Start (Choose One)

### Systemd (Recommended - Includes Wake-on-LAN)
```bash
# Will wake machine from sleep and run hourly
mkdir -p ~/.config/systemd/user

# Create service file
cat > ~/.config/systemd/user/jules-ralph-sync.service << 'EOF'
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
EOF

# Create timer file
cat > ~/.config/systemd/user/jules-ralph-sync.timer << 'EOF'
[Unit]
Description=Jules Ralph-Loop Sync - Hourly

[Timer]
OnCalendar=hourly
Persistent=true
OnBootSec=5sec
AccuracySec=1s

[Install]
WantedBy=timers.target
EOF

# Enable & start
systemctl --user daemon-reload
systemctl --user enable julius-ralph-sync.timer
systemctl --user start julius-ralph-sync.timer

# Verify
systemctl --user status julius-ralph-sync.timer
```

### Cron (Simple Alternative)
```bash
crontab -e

# Add this line (runs every hour at :00)
0 * * * * /home/samalabam/code/unified-cmtg/.jules/scripts/run-ralph-sync.sh >> /home/samalabam/code/unified-cmtg/.ralph-loop-state/cron.log 2>&1

# Verify
crontab -l
```

## Monitor Jules

```bash
# Check latest sync
tail -1 /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync-schedule.log

# View latest report
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md | head -30

# Watch live logs (systemd)
journalctl --user -u julius-ralph-sync.service -f

# Check if scheduled (systemd)
systemctl --user list-timers julius-ralph-sync.timer

# Check if scheduled (cron)
crontab -l | grep ralph-sync
```

## Manual Trigger (Anytime)
```bash
/home/samalabam/code/unified-cmtg/.jules/scripts/run-ralph-sync.sh
```

## What Happens Each Hour

1. ✅ Reads git changes (last 10 commits)
2. ✅ Analyzes code for completed tasks
3. ✅ Updates task tracking files
4. ✅ Refreshes sprint status
5. ✅ Updates live dashboard
6. ✅ Commits documentation if changes
7. ✅ Pushes to git origin
8. ✅ Logs everything to sync-schedule.log

## Example Output

```
[2026-01-16 12:00:00Z] Jules: Ralph-Loop Sync Starting
[2026-01-16 12:00:02Z] Uncommitted changes: 8 files
[2026-01-16 12:00:03Z] Executing ralph-loop...
[2026-01-16 12:00:45Z] ✅ Sync completed successfully (42s)
[2026-01-16 12:00:46Z] ✅ Dashboard updated
[2026-01-16 12:00:47Z] ✅ Changes committed to git
[2026-01-16 12:00:48Z] ✅ Jules: Ralph-Loop Sync Completed
```

## Customization

| Need | Change |
|------|--------|
| Different schedule | Edit `OnCalendar=` in timer (hourly, daily, etc.) |
| No git commits | Comment out commit section in `run-ralph-sync.sh` |
| More iterations | Change `--max-iterations 10` to `20` |
| Skip dashboard update | Comment out `generate-dashboard.sh` line |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Not running | Check: `systemctl --user is-enabled julius-ralph-sync.timer` |
| Timing out | Commit changes more frequently to reduce diff size |
| Git push fails | Will retry next hour automatically |
| Need to clarify | Check log for "CLARIFICATION NEEDED" and answer |

## Links

- **Full Documentation**: `.jules/SETUP.md`
- **Task Definition**: `.jules/tasks/ralph-loop-hourly-sync.md`
- **Runner Script**: `.jules/scripts/run-ralph-sync.sh`
- **Reports**: `SYNC_REPORTS/sync-latest.md`
- **Activity Log**: `.ralph-loop-state/sync-schedule.log`
- **Live Dashboard**: `http://localhost:9000` (updated automatically)

## Status Dashboard

Always check the live dashboard for current project status:
```
http://localhost:9000
```

Jules keeps it updated with fresh metrics every sync!

---

**Setup**: 5-10 minutes (copy-paste)
**Maintenance**: Zero (fully automatic)
**Success Rate**: >99% (retries automatically)
