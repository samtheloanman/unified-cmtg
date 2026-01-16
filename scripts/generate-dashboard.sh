#!/bin/bash
# Dashboard Generator Script
# Collects live data and outputs a JSON file for dashboard.html
# Usage: ./scripts/generate-dashboard.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_FILE="$PROJECT_ROOT/dashboard-data.json"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M %Z')
TIMESTAMP_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "🔄 Collecting Dashboard Data..."

# --- Collect Docker Data ---
# Format: Name,Status,Ports
echo "📦 Docker containers..."
CONTAINERS_JSON="[]"
if command -v docker &> /dev/null; then
    # We use a custom format to easily parse into JSON
    # Note: Using a robust way to generate JSON array from bash is tricky, ensuring escaping is key.
    # Here we build a simple CSV-like string then convert to JSON structure manually or via python/jq if avail.
    # We'll use a simple loop approach for bash compatibility.
    
    CONTAINER_LIST=$(docker ps --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>/dev/null || true)
    
    if [ ! -z "$CONTAINER_LIST" ]; then
        CONTAINERS_JSON="["
        FIRST=1
        while IFS='|' read -r name status ports; do
            if [ $FIRST -eq 0 ]; then
                CONTAINERS_JSON="$CONTAINERS_JSON,"
            fi
            # Clean up ports (sometimes they are long lists)
            SHORT_PORT=$(echo "$ports" | grep -o "[0-9]*->[0-9]*" | head -1 | cut -d'-' -f1)
            if [ -z "$SHORT_PORT" ]; then
                 SHORT_PORT=$(echo "$ports" | grep -o ":[0-9]*" | head -1) 
            fi
            
            # Simple status check
            IS_HEALTHY="true"
            if [[ "$status" == *"unhealthy"* ]] || [[ "$status" == *"Exited"* ]]; then
                IS_HEALTHY="false"
            fi

            CONTAINERS_JSON="$CONTAINERS_JSON {\"name\": \"$name\", \"status\": \"$status\", \"port\": \"$SHORT_PORT\", \"healthy\": $IS_HEALTHY}"
            FIRST=0
        done <<< "$CONTAINER_LIST"
        CONTAINERS_JSON="$CONTAINERS_JSON]"
    fi
fi

# --- Collect Git Data ---
echo "📝 Git history..."
COMMITS_JSON="[]"
BRANCHES_JSON="[]"
COMMIT_COUNT=0
BRANCH_COUNT=0

if [ -d "$PROJECT_ROOT/.git" ]; then
    cd "$PROJECT_ROOT"
    
    # Commits: hash|subject|author_name|relative_date
    LOGS=$(git log --oneline -n 20 --format="%h|%s|%an|%ar" 2>/dev/null || true)
    if [ ! -z "$LOGS" ]; then
        COMMITS_JSON="["
        FIRST=1
        while IFS='|' read -r hash subject author date; do
            if [ $FIRST -eq 0 ]; then
                COMMITS_JSON="$COMMITS_JSON,"
            fi
            # Escape quotes in subject
            CLEAN_SUBJECT=$(echo "$subject" | sed 's/"/\\"/g')
            
            IS_JULES="false"
            if [[ "$author" == *"Jules"* ]]; then
                IS_JULES="true"
            fi
            
            COMMITS_JSON="$COMMITS_JSON {\"hash\": \"$hash\", \"message\": \"$CLEAN_SUBJECT\", \"author\": \"$author\", \"date\": \"$date\", \"is_ai\": $IS_JULES}"
            FIRST=0
            COMMIT_COUNT=$((COMMIT_COUNT + 1))
        done <<< "$LOGS"
        COMMITS_JSON="$COMMITS_JSON]"
    fi

    # Branches
    BRANCHES=$(git branch -a --format="%(refname:short)|%(committerdate:relative)" --sort=-committerdate 2>/dev/null | head -15 || true)
    if [ ! -z "$BRANCHES" ]; then
        BRANCHES_JSON="["
        FIRST=1
        while IFS='|' read -r name date; do
            if [ $FIRST -eq 0 ]; then
                BRANCHES_JSON="$BRANCHES_JSON,"
            fi
            IS_MAIN="false"
            if [[ "$name" == "main" ]] || [[ "$name" == "master" ]]; then
                IS_MAIN="true"
            fi
            
            BRANCHES_JSON="$BRANCHES_JSON {\"name\": \"$name\", \"date\": \"$date\", \"is_main\": $IS_MAIN}"
            FIRST=0
            BRANCH_COUNT=$((BRANCH_COUNT + 1))
        done <<< "$BRANCHES"
        BRANCHES_JSON="$BRANCHES_JSON]"
    fi
fi

# --- Phase Status (Manually maintained for now, can be hooked to a file later) ---
# Copied from current dashboard state
PHASES_JSON='[
    {"id": "F.1", "name": "Wagtail CMS Models & Structure", "progress": 100, "status": "Done"},
    {"id": "F.2", "name": "WordPress Content Extraction", "progress": 0, "status": "Pending"},
    {"id": "F.3", "name": "Content Import & URL Migration", "progress": 0, "status": "Pending"},
    {"id": "F.4", "name": "Location & Office Data Import", "progress": 100, "status": "Done"},
    {"id": "F.5", "name": "Programmatic SEO Infrastructure", "progress": 0, "status": "Pending"},
    {"id": "F.6", "name": "AI Content Generation Pipeline", "progress": 0, "status": "Pending"},
    {"id": "F.7", "name": "Next.js CMS Integration", "progress": 50, "status": "In Progress"},
    {"id": "F.8", "name": "Floify Integration Completion", "progress": 80, "status": "In Progress"},
    {"id": "F.9", "name": "Production Hardening & Testing", "progress": 0, "status": "Pending"},
    {"id": "F.10", "name": "Deployment & Cutover", "progress": 0, "status": "Pending"}
]'

# Calculate overall progress
TOTAL_PROGRESS_SUM=0
PHASE_COUNT=0
# Parse the JSON string carefully or just hardcode the calc for bash simplicity
# For bash, we will sum the known values: 100+100+50+80 = 330 / 10 = 33
OVERALL_PROGRESS=33
COMPLETED_PHASES=2 # F.1 and F.4

# --- Construct Final JSON ---
cat > "$DATA_FILE" << EOF
{
  "meta": {
    "generated_at": "$TIMESTAMP",
    "generated_at_iso": "$TIMESTAMP_ISO",
    "host": "$(hostname)"
  },
  "stats": {
    "phases_complete": $COMPLETED_PHASES,
    "overall_progress": $OVERALL_PROGRESS,
    "recent_commits": $COMMIT_COUNT,
    "containers_running": $(echo "$CONTAINERS_JSON" | grep -o "name" | wc -l),
    "active_branches": $BRANCH_COUNT
  },
  "phases": $PHASES_JSON,
  "containers": $CONTAINERS_JSON,
  "commits": $COMMITS_JSON,
  "branches": $BRANCHES_JSON
}
EOF

echo "✅ Generated $DATA_FILE"
echo "   Size: $(du -h $DATA_FILE | cut -f1)"
