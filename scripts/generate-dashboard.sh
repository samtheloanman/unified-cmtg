#!/bin/bash
# Dashboard Generator Script - Dynamic version
# Parses checklist.md for phase status
# Usage: ./scripts/generate-dashboard.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DATA_FILE="$PROJECT_ROOT/dashboard/dashboard-data.json"
CHECKLIST_FILE="$PROJECT_ROOT/unified-platform/conductor/tracks/finalization_20260114/checklist.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M %Z')
TIMESTAMP_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "🔄 Collecting Dashboard Data..."

# --- Collect Docker Data ---
echo "📦 Docker containers..."
CONTAINERS_JSON="[]"
if command -v docker &> /dev/null; then
    CONTAINER_LIST=$(docker ps --format "{{.Names}}|{{.Status}}|{{.Ports}}" 2>/dev/null || true)
    
    if [ -n "$CONTAINER_LIST" ]; then
        CONTAINERS_JSON="["
        FIRST=1
        while IFS='|' read -r name status ports; do
            [ -z "$name" ] && continue
            if [ $FIRST -eq 0 ]; then
                CONTAINERS_JSON="$CONTAINERS_JSON,"
            fi
            SHORT_PORT=$(echo "$ports" | grep -oE ':[0-9]+' | head -1 || echo "")
            
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
    
    LOGS=$(git log --oneline -n 20 --format="%h|%s|%an|%ar" 2>/dev/null || true)
    if [ -n "$LOGS" ]; then
        COMMITS_JSON="["
        FIRST=1
        while IFS='|' read -r hash subject author date; do
            [ -z "$hash" ] && continue
            if [ $FIRST -eq 0 ]; then
                COMMITS_JSON="$COMMITS_JSON,"
            fi
            CLEAN_SUBJECT=$(echo "$subject" | sed 's/"/\\"/g')
            
            IS_JULES="false"
            if [[ "$author" == *"jules"* ]] || [[ "$author" == *"Jules"* ]]; then
                IS_JULES="true"
            fi
            
            COMMITS_JSON="$COMMITS_JSON {\"hash\": \"$hash\", \"message\": \"$CLEAN_SUBJECT\", \"author\": \"$author\", \"date\": \"$date\", \"is_ai\": $IS_JULES}"
            FIRST=0
            COMMIT_COUNT=$((COMMIT_COUNT + 1))
        done <<< "$LOGS"
        COMMITS_JSON="$COMMITS_JSON]"
    fi

    BRANCHES=$(git branch -a --format="%(refname:short)|%(committerdate:relative)" --sort=-committerdate 2>/dev/null | head -15 || true)
    if [ -n "$BRANCHES" ]; then
        BRANCHES_JSON="["
        FIRST=1
        while IFS='|' read -r name date; do
            [ -z "$name" ] && continue
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

# --- Parse Phase Status from checklist.md ---
echo "📊 Parsing phases..."

# Simpler approach: count [x] vs [ ] per phase section
get_phase_progress() {
    local phase_id="$1"
    local checklist="$2"
    
    # Get line range for this phase
    local start_line=$(grep -n "^## Phase $phase_id" "$checklist" 2>/dev/null | head -1 | cut -d: -f1)
    if [ -z "$start_line" ]; then
        echo "0|Pending"
        return
    fi
    
    # Find next phase or end of file
    local end_line=$(tail -n +$((start_line + 1)) "$checklist" | grep -n "^## Phase" | head -1 | cut -d: -f1)
    if [ -z "$end_line" ]; then
        end_line=9999
    else
        end_line=$((start_line + end_line - 1))
    fi
    
    # Extract section
    local section=$(sed -n "${start_line},${end_line}p" "$checklist")
    
    # Count items
    local total=$(echo "$section" | grep -c '^\- \[' 2>/dev/null || echo 0)
    local done=$(echo "$section" | grep -c '^\- \[x\]' 2>/dev/null || echo 0)
    
    # Clean values (remove any whitespace)
    total=$(echo "$total" | tr -d '[:space:]')
    done=$(echo "$done" | tr -d '[:space:]')
    
    # Ensure numeric
    [[ ! "$total" =~ ^[0-9]+$ ]] && total=0
    [[ ! "$done" =~ ^[0-9]+$ ]] && done=0
    
    local progress=0
    local status="Pending"
    
    if [ "$total" -gt 0 ]; then
        progress=$((done * 100 / total))
    fi
    
    # Check for COMPLETE marker in header
    if echo "$section" | head -5 | grep -q "✅.*COMPLETE"; then
        progress=100
        status="Done"
    elif [ "$progress" -eq 100 ]; then
        status="Done"
    elif [ "$progress" -gt 0 ]; then
        status="In Progress"
    fi
    
    echo "$progress|$status"
}

# Build phases JSON
PHASES_JSON="["
COMPLETED_PHASES=0
TOTAL_PROGRESS=0

declare -A PHASE_NAMES
PHASE_NAMES["F.1"]="Wagtail CMS Models & Structure"
PHASE_NAMES["F.2"]="WordPress Content Extraction"
PHASE_NAMES["F.3"]="Content Import & URL Migration"
PHASE_NAMES["F.4"]="Location & Office Data Import"
PHASE_NAMES["F.5"]="Programmatic SEO Infrastructure"
PHASE_NAMES["F.6"]="AI Content Generation Pipeline"
PHASE_NAMES["F.7"]="Next.js CMS Integration"
PHASE_NAMES["F.8"]="Floify Integration Completion"
PHASE_NAMES["F.9"]="Production Hardening & Testing"
PHASE_NAMES["F.10"]="Deployment & Cutover"

FIRST=1
for phase_id in F.1 F.2 F.3 F.4 F.5 F.6 F.7 F.8 F.9 F.10; do
    if [ -f "$CHECKLIST_FILE" ]; then
        result=$(get_phase_progress "$phase_id" "$CHECKLIST_FILE")
        progress=$(echo "$result" | cut -d'|' -f1)
        status=$(echo "$result" | cut -d'|' -f2)
    else
        progress=0
        status="Pending"
    fi
    
    name="${PHASE_NAMES[$phase_id]}"
    
    if [ $FIRST -eq 0 ]; then
        PHASES_JSON="$PHASES_JSON,"
    fi
    PHASES_JSON="$PHASES_JSON {\"id\": \"$phase_id\", \"name\": \"$name\", \"progress\": $progress, \"status\": \"$status\"}"
    FIRST=0
    
    TOTAL_PROGRESS=$((TOTAL_PROGRESS + progress))
    if [ "$progress" -eq 100 ]; then
        COMPLETED_PHASES=$((COMPLETED_PHASES + 1))
    fi
done

PHASES_JSON="$PHASES_JSON]"
OVERALL_PROGRESS=$((TOTAL_PROGRESS / 10))

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
echo "   Phases complete: $COMPLETED_PHASES/10"
echo "   Overall progress: $OVERALL_PROGRESS%"
