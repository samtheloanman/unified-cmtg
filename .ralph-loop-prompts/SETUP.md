# Ralph-Loop Project Sync - Setup Guide

## Prerequisites

1. **Ralph-Loop Plugin**: Verify installed
   ```bash
   claude --version  # Should show ralph-loop plugin available
   ```

2. **Git Repository**: Already initialized ✅
   ```bash
   cd /home/samalabam/code/unified-cmtg/unified-platform
   git status  # Should work
   ```

3. **Required Tools**: jq for JSON processing
   ```bash
   sudo apt-get install jq -y  # If not already installed
   ```

---

## Initial Setup

### Step 1: Create State Directory
```bash
mkdir -p /home/samalabam/code/unified-cmtg/.ralph-loop-state
mkdir -p /home/samalabam/code/unified-cmtg/SYNC_REPORTS
```

### Step 2: Initialize State File
```bash
cat > /home/samalabam/code/unified-cmtg/.ralph-loop-state/last-sync.json << 'EOF'
{
  "last_commit": "",
  "last_run": "",
  "files_processed": [],
  "version": "1.0"
}
EOF
```

### Step 3: Add to .gitignore
```bash
cat >> /home/samalabam/code/unified-cmtg/.gitignore << 'EOF'

# Ralph-Loop State (local only)
.ralph-loop-state/sync.lock
SYNC_REPORTS/sync-latest.md

# Keep archived reports but ignore latest (changes every hour)
!SYNC_REPORTS/sync-*.md
EOF
```

### Step 4: First Dry Run
```bash
ralph-loop run /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync.md --dry-run
```

Expected output: Preview of changes without executing

### Step 5: First Real Run
```bash
ralph-loop run /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync.md
```

Review the output in `/home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md`

---

## Enable Hourly Auto-Sync

### Option A: Cron (Traditional)
```bash
# Open crontab
crontab -e

# Add this line (runs every hour at :00)
0 * * * * cd /home/samalabam/code/unified-cmtg && ralph-loop run .ralph-loop-prompts/project-sync.md --timeout 360 >> .ralph-loop-state/cron.log 2>&1
```

### Option B: Ralph-Loop Daemon (Recommended)
```bash
# Start daemon that runs every hour
nohup ralph-loop daemon \
  --prompt /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync.md \
  --interval 3600 \
  --timeout 360 \
  --log /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync.log \
  > /dev/null 2>&1 &

# Save PID for later
echo $! > /home/samalabam/code/unified-cmtg/.ralph-loop-state/daemon.pid
```

### Option C: Systemd Service (Production)
```bash
# Create service file
sudo cat > /etc/systemd/system/unified-cmtg-sync.service << 'EOF'
[Unit]
Description=Unified CMTG Project Sync (Ralph-Loop)
After=network.target

[Service]
Type=simple
User=samalabam
WorkingDirectory=/home/samalabam/code/unified-cmtg
ExecStart=/usr/local/bin/ralph-loop daemon \
  --prompt /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync.md \
  --interval 3600 \
  --timeout 360 \
  --log /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync.log
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl enable unified-cmtg-sync.service
sudo systemctl start unified-cmtg-sync.service
sudo systemctl status unified-cmtg-sync.service
```

---

## Verification

### Check Sync Status
```bash
# View latest report
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md

# Check state file
cat /home/samalabam/code/unified-cmtg/.ralph-loop-state/last-sync.json | jq .

# View log (if using daemon)
tail -f /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync.log
```

### Check Lock File
```bash
# Should NOT exist (unless sync is currently running)
ls -la /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync.lock

# If stuck, manually remove (only if you're sure sync isn't running)
rm -f /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync.lock
```

---

## Troubleshooting

### Issue: "Lock file exists" error
**Cause**: Previous sync didn't complete cleanly
**Fix**:
```bash
# Check if sync is actually running
ps aux | grep ralph-loop

# If not running, remove lock
rm -f /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync.lock
```

### Issue: Sync takes >6 minutes
**Cause**: Too many files to process
**Fix**: Commit your changes to reduce uncommitted file count
```bash
cd /home/samalabam/code/unified-cmtg/unified-platform
git add .
git commit -m "Sync: Commit pending changes"
```

### Issue: State file corrupted
**Cause**: Interrupted write operation
**Fix**: Restore from backup or recreate
```bash
# If backup exists
cp /home/samalabam/code/unified-cmtg/.ralph-loop-state/last-sync.json.backup \
   /home/samalabam/code/unified-cmtg/.ralph-loop-state/last-sync.json

# Or recreate
echo '{"last_commit": "", "last_run": "", "files_processed": []}' > \
  /home/samalabam/code/unified-cmtg/.ralph-loop-state/last-sync.json
```

### Issue: No changes detected
**Cause**: State file has current commit already
**Fix**: This is normal if no new commits since last sync

### Issue: Questions keep appearing
**Cause**: Sync is uncertain and following decision framework
**Fix**: Review questions in sync-latest.md and provide guidance, or adjust decision thresholds in project-sync.md

---

## Manual Operations

### Force Re-Scan Everything
```bash
# Reset state to trigger full scan
echo '{"last_commit": "", "last_run": "", "files_processed": []}' > \
  /home/samalabam/code/unified-cmtg/.ralph-loop-state/last-sync.json

# Run sync
ralph-loop run /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync.md
```

### Stop Auto-Sync
```bash
# If using cron
crontab -e  # Remove the line

# If using daemon
kill $(cat /home/samalabam/code/unified-cmtg/.ralph-loop-state/daemon.pid)

# If using systemd
sudo systemctl stop unified-cmtg-sync.service
sudo systemctl disable unified-cmtg-sync.service
```

### Archive Old Reports
```bash
# Keep only last 7 days of reports
cd /home/samalabam/code/unified-cmtg/SYNC_REPORTS
find . -name "sync-*.md" -mtime +7 -exec mv {} archived/ \;
```

---

## Integration with Workflow

### For Gemini CLI (L1 Orchestrator)
Before delegating tasks, check sync status:
```bash
cat /home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md
```

Use the "Next Sync Priorities" section to inform task delegation.

### For Claude Code (L2 Generator)
When completing tasks, use structured commit messages:
```bash
git commit -m "feat: Implement rate sheet processor

[Phase 4] Rate Sheet Agent
- Added GeminiAIProcessor class
- Implemented fallback to PdfPlumber
- Tests passing"
```

This allows auto-detection of:
- Feature completion (`feat:`)
- Phase association (`[Phase 4]`)
- Test status (`Tests passing`)

### For Jules (L2 Builder)
Infrastructure changes trigger sync:
```bash
# After modifying docker-compose.yml
git commit -m "chore: Update Docker configuration

[Phase 1] Foundation
- Added Redis service
- Updated port mappings"
```

---

## Best Practices

1. **Commit Often**: Smaller commits = more accurate task detection
2. **Structured Messages**: Use conventional commits (feat:, fix:, docs:, etc.)
3. **Phase Tags**: Include `[Phase N]` in commit messages
4. **Test Status**: Mention "tests passing" or "WIP" in commits
5. **Review Reports**: Check sync-latest.md daily for questions
6. **Clean Git**: Keep working directory clean for faster syncs

---

## Performance Tuning

### If Syncs Are Slow
1. Reduce commit message history window (change HEAD~24 to HEAD~6)
2. Increase interval (3600s → 7200s for every 2 hours)
3. Commit frequently to reduce uncommitted file scans
4. Add file type exclusions (e.g., skip .pyc, node_modules)

### If Syncs Miss Changes
1. Reduce interval (3600s → 1800s for every 30 min)
2. Increase commit history window (HEAD~24 → HEAD~48)
3. Check state file is updating correctly
4. Verify git commands work in your environment

---

## Success Indicators

✅ Sync completes in <5 minutes
✅ sync-latest.md updates every hour
✅ Task completions auto-detected from commits
✅ User questions only for important decisions
✅ All agents reference sync reports for status
✅ No manual task list updates needed

---

## Support

If issues persist:
1. Check logs: `.ralph-loop-state/sync.log`
2. Verify git status: `cd unified-platform && git status`
3. Test manually: `ralph-loop run .ralph-loop-prompts/project-sync.md --dry-run`
4. Review decision framework in project-sync.md
5. Ask Claude Code for assistance with specific error messages
