#!/bin/bash
# Ralph-Loop Sync Runner - Wrapper script for systemd timer
# Purpose: Run project sync every hour with proper logging

set -euo pipefail

# Configuration
PROJECT_ROOT="/home/samalabam/code/unified-cmtg"
PLATFORM_DIR="$PROJECT_ROOT/unified-platform"
LOG_DIR="$PROJECT_ROOT/.ralph-loop-state"
LOG_FILE="$LOG_DIR/sync-runner.log"
PROMPT_FILE="$PROJECT_ROOT/.ralph-loop-prompts/simple-sync.txt"

# Create log directory if missing
mkdir -p "$LOG_DIR"

# Log function
log() {
  echo "[$(date -u +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=========================================="
log "Ralph-Loop Sync Started"
log "=========================================="

# Check if ralph-loop is installed
if ! command -v ralph-loop &> /dev/null; then
  log "ERROR: ralph-loop command not found. Please install the plugin."
  exit 1
fi

# Check if prompt file exists
if [ ! -f "$PROMPT_FILE" ]; then
  log "ERROR: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

# Change to platform directory
cd "$PLATFORM_DIR" || exit 1
log "Working directory: $PLATFORM_DIR"

# Read prompt content
PROMPT_CONTENT=$(cat "$PROMPT_FILE")

log "Running sync with simple-sync.txt prompt..."

# Run the ralph-loop sync
# Note: This will run in the background and timeout after 360 seconds (6 minutes)
timeout 360 ralph-loop:ralph-loop "$PROMPT_CONTENT" --max-iterations 10 --completion-promise "SYNC_COMPLETE" 2>&1 | tee -a "$LOG_FILE" || {
  EXIT_CODE=$?
  if [ $EXIT_CODE -eq 124 ]; then
    log "TIMEOUT: Sync exceeded 360 second limit"
  else
    log "ERROR: Sync failed with exit code $EXIT_CODE"
  fi
  exit $EXIT_CODE
}

log "=========================================="
log "Ralph-Loop Sync Completed"
log "=========================================="
log "Check latest report: $PROJECT_ROOT/SYNC_REPORTS/sync-latest.md"
log ""

exit 0
