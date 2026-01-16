#!/bin/bash
# Jules Sync Agent Wrapper
# Designed for cron execution on dell-brain Docker container
# Runs the Python sync agent with proper environment setup

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to repo directory
cd "$REPO_ROOT"

# Run the Python sync agent
python3 "$SCRIPT_DIR/sync-agent.py"

# Capture exit code
EXIT_CODE=$?

# Log summary
if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Jules sync completed successfully" >> "$SCRIPT_DIR/../.ralph-loop-state/sync-schedule.log"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Jules sync failed with exit code $EXIT_CODE" >> "$SCRIPT_DIR/../.ralph-loop-state/sync-schedule.log"
fi

exit $EXIT_CODE
