#!/bin/bash
# Jules Ralph-Loop Sync Runner
# Executed hourly by systemd timer to keep docs in sync
# Usage: /home/samalabam/code/unified-cmtg/.jules/scripts/run-ralph-sync.sh

set -euo pipefail

# Configuration
PROJECT_ROOT="/home/samalabam/code/unified-cmtg"
PLATFORM_DIR="$PROJECT_ROOT/unified-platform"
STATE_DIR="$PROJECT_ROOT/.ralph-loop-state"
REPORTS_DIR="$PROJECT_ROOT/SYNC_REPORTS"
LOG_FILE="$STATE_DIR/sync-schedule.log"
OUTPUT_LOG="$STATE_DIR/loop-output-$(date +%Y-%m-%d-%H%M%S).log"
SYNC_LOCK="$STATE_DIR/ralph-sync.lock"

# Ensure directories exist
mkdir -p "$STATE_DIR" "$REPORTS_DIR"

# Lock file management to prevent concurrent runs
if [ -f "$SYNC_LOCK" ]; then
  LOCK_AGE=$(($(date +%s) - $(stat -c %Y "$SYNC_LOCK" 2>/dev/null || echo 0)))
  if [ "$LOCK_AGE" -lt 600 ]; then  # Lock is fresh (< 10 min)
    echo "[$(date -u +'%Y-%m-%d %H:%M:%SZ')] Ralph-Loop already running, skipping" | tee -a "$LOG_FILE"
    exit 0
  fi
  # Stale lock, remove it
  rm -f "$SYNC_LOCK"
fi

touch "$SYNC_LOCK"
trap "rm -f $SYNC_LOCK" EXIT

log() {
  echo "[$(date -u +'%Y-%m-%d %H:%M:%SZ')] $*" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Jules: Ralph-Loop Sync Starting"
log "=========================================="

# Verify we're in the right place
if [ ! -d "$PLATFORM_DIR" ]; then
  log "ERROR: Platform directory not found: $PLATFORM_DIR"
  exit 1
fi

cd "$PLATFORM_DIR"
log "Working in: $PLATFORM_DIR"

# Check git status
GIT_STATUS=$(git status --porcelain | wc -l)
log "Uncommitted changes: $GIT_STATUS files"

# Run ralph-loop with timeout
log "Executing ralph-loop..."
START_TIME=$(date +%s)

PROMPT="Sync docs in /home/samalabam/code/unified-cmtg/unified-platform: Run git log -n 10 and git status. Read conductor/tasks.md and conductor/current.md. Update tasks.md by moving completed work to checkmark section and adding new TODOs to pending (auto if under 3 changes, otherwise ask me first). Update current.md with fresh timestamp and completion percentage (auto if under 10 percent change, otherwise ask me). If unsure about anything, STOP and ask: CLARIFICATION NEEDED: [your questions]. Wait for my response then continue. Write summary to SYNC_REPORTS/sync-latest.md. Output SYNC_COMPLETE when git is analyzed and docs match reality."

# Execute ralph-loop (timeout at 400 seconds = 6m40s for 6m inner timeout + overhead)
if timeout 400 /ralph-loop:ralph-loop "$PROMPT" --max-iterations 10 --completion-promise "SYNC_COMPLETE" 2>&1 | tee -a "$OUTPUT_LOG"; then
  EXIT_CODE=0
else
  EXIT_CODE=$?
fi

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

# Check for success marker
if grep -q "SYNC_COMPLETE" "$OUTPUT_LOG" 2>/dev/null; then
  log "✅ Sync completed successfully (${DURATION}s)"
  SYNC_SUCCESS=true
else
  if [ $EXIT_CODE -eq 124 ]; then
    log "⚠️  Sync timed out after ${DURATION}s"
  else
    log "❌ Sync failed with exit code $EXIT_CODE (${DURATION}s)"
  fi
  SYNC_SUCCESS=false
fi

# Update dashboard data
log "Refreshing dashboard data..."
if /home/samalabam/code/unified-cmtg/scripts/generate-dashboard.sh 2>&1 | tee -a "$OUTPUT_LOG"; then
  log "✅ Dashboard updated"
else
  log "⚠️  Dashboard update had issues"
fi

# Commit results if changes were made
if [ $GIT_STATUS -gt 0 ] && [ "$SYNC_SUCCESS" = true ]; then
  log "Committing documentation changes..."
  cd "$PROJECT_ROOT"

  if git add conductor/tasks.md conductor/current.md PROJECT_STATUS_REVIEW.md 2>/dev/null; then
    if git commit -m "chore(ralph): Hourly sync - updated task tracking and project status

[Automated by Jules]
- Analyzed git changes (10 commits)
- Updated task completion status
- Refreshed sprint status and phase completion
- Generated sync report

Run: $(date -u +'%Y-%m-%d %H:%M:%SZ')
Duration: ${DURATION}s" 2>&1 | tee -a "$OUTPUT_LOG"; then
      log "✅ Changes committed"

      if git push origin main 2>&1 | tee -a "$OUTPUT_LOG"; then
        log "✅ Changes pushed to origin"
      else
        log "⚠️  Could not push to origin (will retry next sync)"
      fi
    else
      log "⚠️  No changes to commit"
    fi
  else
    log "⚠️  Could not stage files for commit"
  fi
fi

# Final summary
log "=========================================="
if [ "$SYNC_SUCCESS" = true ]; then
  log "✅ Jules: Ralph-Loop Sync Completed"
  FINAL_STATUS="SUCCESS"
else
  log "⚠️  Jules: Ralph-Loop Sync Had Issues"
  FINAL_STATUS="PARTIAL"
fi
log "=========================================="
log "Output saved to: $OUTPUT_LOG"
log "Report available at: $PROJECT_ROOT/SYNC_REPORTS/sync-latest.md"
log ""

# Exit with appropriate code
[ "$SYNC_SUCCESS" = true ] && exit 0 || exit 1
