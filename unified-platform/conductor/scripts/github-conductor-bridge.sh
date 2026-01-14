#!/bin/bash
# GitHub-Conductor Bridge Script
# Syncs Conductor task completion status back to GitHub issues

set -e

CONDUCTOR_DIR="$(dirname "$0")/.."
REPO="samtheloanman/unified-cmtg"

echo "🔄 Syncing Conductor tasks to GitHub..."
echo "=========================================="

# Check if tasks.md exists
if [ ! -f "$CONDUCTOR_DIR/tasks.md" ]; then
    echo "❌ tasks.md not found in $CONDUCTOR_DIR"
    exit 1
fi

# Parse tasks.md for completed items that reference GitHub issues
COMPLETED_TASKS=$(grep -E "^\- \[x\].*#[0-9]+" "$CONDUCTOR_DIR/tasks.md" || true)

if [ -z "$COMPLETED_TASKS" ]; then
    echo "ℹ️  No completed tasks with GitHub issue references found"
    exit 0
fi

echo "$COMPLETED_TASKS" | while IFS= read -r line; do
    # Extract issue number from the line (format: #123)
    ISSUE_NUM=$(echo "$line" | grep -oP '#\K[0-9]+' || true)
    
    if [ -z "$ISSUE_NUM" ]; then
        continue
    fi
    
    echo ""
    echo "Processing issue #$ISSUE_NUM..."
    
    # Check if issue is still open
    ISSUE_STATE=$(gh issue view "$ISSUE_NUM" --json state --jq .state 2>/dev/null || echo "NOT_FOUND")
    
    if [ "$ISSUE_STATE" == "NOT_FOUND" ]; then
        echo "  ⚠️  Issue #$ISSUE_NUM not found, skipping"
        continue
    fi
    
    if [ "$ISSUE_STATE" == "OPEN" ]; then
        echo "  📌 Issue #$ISSUE_NUM is still open, closing..."
        
        gh issue close "$ISSUE_NUM" \
          --comment "✅ Task completed by Conductor orchestration

This issue was automatically closed because the corresponding task in \`conductor/tasks.md\` has been marked as complete.

Task line: \`$line\`" || echo "  ❌ Failed to close issue"
        
        echo "  ✅ Closed issue #$ISSUE_NUM"
    else
        echo "  ℹ️  Issue #$ISSUE_NUM already closed"
    fi
done

echo ""
echo "=========================================="
echo "✅ Sync complete"
