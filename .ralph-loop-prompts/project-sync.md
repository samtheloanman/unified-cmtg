# Ralph-Loop: Git-Integrated Project Sync v1.0

## Mission
Maintain real-time synchronization between code changes (via git) and project documentation/task tracking for unified-cmtg/unified-platform, running hourly with autonomous decision-making.

---

## Pre-Flight Checks

### 1. Lock File Check
```bash
LOCK_FILE="/home/samalabam/code/unified-cmtg/.ralph-loop-state/sync.lock"
if [ -f "$LOCK_FILE" ]; then
  echo "ERROR: Another sync is running (lock file exists)"
  exit 1
fi
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT
```

### 2. State File Initialization
```bash
STATE_FILE="/home/samalabam/code/unified-cmtg/.ralph-loop-state/last-sync.json"
mkdir -p /home/samalabam/code/unified-cmtg/.ralph-loop-state/

if [ ! -f "$STATE_FILE" ]; then
  echo '{"last_commit": "", "last_run": "", "files_processed": []}' > "$STATE_FILE"
fi
```

### 3. Working Directory
```bash
cd /home/samalabam/code/unified-cmtg/unified-platform || exit 1
```

---

## Phase 1: Git Change Detection (30 seconds)

### Identify Changed Files Since Last Sync
```bash
# Get last processed commit from state
LAST_COMMIT=$(jq -r '.last_commit' "$STATE_FILE")
CURRENT_COMMIT=$(git rev-parse HEAD)

if [ "$LAST_COMMIT" = "" ]; then
  # First run - check last 24 hours
  CHANGED_FILES=$(git diff --name-only HEAD~24..HEAD 2>/dev/null || git ls-files)
else
  # Incremental - only changes since last sync
  CHANGED_FILES=$(git diff --name-only "$LAST_COMMIT"..HEAD)
fi

# Also check unstaged/untracked
UNSTAGED=$(git diff --name-only)
UNTRACKED=$(git ls-files --others --exclude-standard)

ALL_CHANGES=$(echo -e "$CHANGED_FILES\n$UNSTAGED\n$UNTRACKED" | sort -u | grep -v '^$')
```

### Parse Git Log for Context
```bash
# Get commit messages since last sync
if [ "$LAST_COMMIT" != "" ]; then
  git log --oneline --no-merges "$LAST_COMMIT"..HEAD > /tmp/recent-commits.txt
else
  git log --oneline --no-merges -n 20 > /tmp/recent-commits.txt
fi
```

**Output**: List of changed files + commit messages for analysis

---

## Phase 2: Intelligent Change Categorization (60 seconds)

### Categorize Changes by Impact
For each file in `ALL_CHANGES`, classify as:

#### Code Changes (Backend)
- `backend/**/*.py` → Check for new models, APIs, tasks
- `backend/*/models.py` → Database schema changes
- `backend/*/views.py` → New API endpoints
- `backend/*/tasks.py` → New Celery tasks
- `backend/*/tests/**` → Test coverage changes

**Action**: Parse files to detect:
- New class definitions → New features
- Modified function signatures → API changes
- New test files → Feature completion signal

#### Code Changes (Frontend)
- `frontend/src/app/**/*.tsx` → New pages/routes
- `frontend/src/components/**` → UI components
- `frontend/src/lib/**` → Utilities/API clients
- `frontend/src/__tests__/**` → Test coverage

**Action**: Parse for:
- New route folders → New user-facing features
- API client changes → Backend integration status
- Component exports → Reusable UI library growth

#### Documentation Changes
- `conductor/**/*.md` → Workflow updates (HIGH PRIORITY)
- `*.md` (root level) → Strategic docs
- `README.md` updates → Setup/onboarding changes

**Action**:
- If conductor docs changed → Manual update, likely outdated
- If PRD/GEMINI changed → Re-align task priorities
- If README changed → Update onboarding checklist

#### Configuration Changes
- `docker-compose*.yml` → Infrastructure changes
- `requirements.txt` / `package.json` → Dependency updates
- `.env*` → Environment configuration
- `Dockerfile` → Container build changes

**Action**: Flag infrastructure tasks as complete or new

---

## Phase 3: Task Detection & Extraction (90 seconds)

### Heuristic-Based Task Completion Detection

#### Signal: Feature Complete
```
IF:
  - New model added in backend/*/models.py
  AND - Serializer exists in backend/*/serializers.py
  AND - View exists in backend/*/views.py
  AND - Tests exist in backend/*/tests/test_*.py
THEN:
  → Task "Implement [Model Name] API" is COMPLETE ✅
```

#### Signal: Frontend Integration Complete
```
IF:
  - API client function added in frontend/src/lib/api.ts
  AND - Component using client exists in frontend/src/components/
  AND - Test file exists in frontend/src/__tests__/
THEN:
  → Task "Integrate [Feature] in Frontend" is COMPLETE ✅
```

#### Signal: Phase Milestone Reached
```
IF:
  - All checklist items in conductor/tracks/phaseN/checklist.md marked done
  AND - Tests passing (check CI or recent commits mention "pass")
THEN:
  → Phase N is COMPLETE ✅ (flag for archival consideration)
```

#### Signal: New Task Discovered
```
IF:
  - Commit message contains "TODO:", "FIXME:", "WIP:"
  OR - Code comment contains "# TODO:"
  OR - File in untracked status for >1 hour
THEN:
  → New task discovered (extract and add to pending)
```

### Commit Message Parsing
Analyze commit messages for task lifecycle events:

| Pattern | Action |
|---------|--------|
| `"feat:"` / `"feature:"` | Add to "Completed" if tests exist, else "In Progress" |
| `"fix:"` / `"bug:"` | Mark related bug task as complete |
| `"refactor:"` | Update architecture notes, don't mark tasks complete |
| `"test:"` | Increment test coverage metric |
| `"docs:"` | Skip task updates (documentation-only) |
| `"wip:"` / `"WIP:"` | Add to "In Progress" |
| `"[Phase N]"` | Associate with specific phase tracking |

---

## Phase 4: Documentation Sync (60 seconds)

### Update Core Tracking Files

#### A. conductor/current.md
**Read current content → Apply updates → Write back**

Updates to make:
- Current sprint status → Use latest commit date
- Blockers → Extract from commit messages with "blocked", "issue", "problem"
- Active tasks → Cross-reference with "In Progress" from git activity
- Completion % → Calculate from checklist completion

**Decision Framework**:
- If completion % differs by <10% → Auto-update
- If completion % differs by >10% → Ask user for confirmation
- If new blocker detected → Auto-add, notify user
- If sprint date is >7 days old → Ask if we should start new sprint

#### B. conductor/tasks.md
**Read current content → Merge with detected changes → Write back**

Updates to make:
- Move completed tasks (detected via heuristics) to "Completed ✅" section
- Add new tasks (detected via TODOs/WIPs) to "Pending ⏳" section
- Update "In Progress 🟡" based on recent commits
- Add timestamps to completed tasks

**Decision Framework**:
- If >5 new tasks detected → Ask user to review list before adding
- If task completed but no tests → Ask if we should mark complete
- If task in progress >14 days → Flag as potentially stuck

#### C. Phase-Specific Checklists
For each `conductor/tracks/phase*/checklist.md`:

**Read → Detect completion signals → Update**

- If all items checked → Mark phase as "COMPLETE ✅"
- If new related code added → Add checklist item
- If >80% complete → Notify user of near-completion

**Decision Framework**:
- If auto-marking phase complete → Ask user to verify
- If adding new checklist items → Auto-add if <3 items, else ask

#### D. PROJECT_STATUS_REVIEW.md
**Update metrics based on git analysis**

Metrics to update:
- Total commits since last review
- Files changed count
- Lines added/removed
- Test coverage trend (if detectable)
- Phase completion percentages

**Decision Framework**:
- Auto-update all metrics
- If major change (>20% completion jump) → Notify user

---

## Phase 5: Cross-Reference Validation (45 seconds)

### Internal Link Checking (Fast Mode)
```bash
# Only check links in modified markdown files
for file in $(echo "$ALL_CHANGES" | grep '\.md$'); do
  grep -oP '\[.*?\]\(\K[^)]+' "$file" | while read -r link; do
    if [[ "$link" =~ ^/ ]]; then
      # Absolute path
      [ ! -f "$link" ] && echo "BROKEN: $file → $link"
    elif [[ ! "$link" =~ ^http ]]; then
      # Relative path
      dir=$(dirname "$file")
      [ ! -f "$dir/$link" ] && echo "BROKEN: $file → $link"
    fi
  done
done
```

**Decision Framework**:
- If <5 broken links → Auto-fix by updating paths
- If >5 broken links → Report to user, ask for guidance
- If link points to archived file → Update to archive path

---

## Phase 6: Archive Management (30 seconds)

### Archive Candidates Detection
```
IF:
  - Phase checklist is 100% complete
  AND - Phase hasn't been modified in >30 days
  AND - No open links pointing to phase docs
THEN:
  → Flag for archival (ASK USER before archiving)
```

### Redundancy Detection
```bash
# Find duplicate content (>80% similar markdown files)
for file in conductor/**/*.md; do
  # Use file similarity heuristics
  # If duplicate found → Flag for review
done
```

**Decision Framework**:
- Never auto-archive (always ask user)
- If duplicate detected → Ask which to keep
- If file unused for >90 days → Suggest archival

---

## Phase 7: Report Generation (15 seconds)

### Create Sync Report
**File**: `/home/samalabam/code/unified-cmtg/SYNC_REPORTS/sync-latest.md`
**Archive**: Previous report to `sync-YYYY-MM-DD-HHMM.md`

```markdown
# Project Sync Report
**Run**: [ISO 8601 timestamp with timezone]
**Version**: 1.0
**Commit Range**: [LAST_COMMIT]..[CURRENT_COMMIT]
**Files Analyzed**: [count]
**Duration**: [seconds]

---

## Changes Detected

### Code Changes
- Backend: [count] files
- Frontend: [count] files
- Tests: [count] files

### Documentation Updates
- Conductor: [count] files
- Strategic docs: [count] files

### Configuration Changes
- [list of config files modified]

---

## Task Updates

### Completed ✅ ([count])
- [Task name] - [Phase] - [Detected via: commit abc123]

### Added to Pending ⏳ ([count])
- [Task name] - [Phase] - [Source: TODO in file.py:123]

### In Progress 🟡 ([count])
- [Task name] - [Agent] - [Last commit: 2 hours ago]

### Flagged as Stuck 🔴 ([count])
- [Task name] - [In progress for 14 days]

---

## Phase Status Changes

| Phase | Old % | New % | Status |
|-------|-------|-------|--------|
| Phase 1 | 90% | 90% | No change |
| Phase 2 | 85% | 92% | ↑ (3 tasks completed) |
| Phase 3 | 60% | 60% | No change |

---

## Documentation Actions

### Files Updated ([count])
- conductor/current.md - Updated sprint status
- conductor/tasks.md - Added 3 completed tasks

### Broken Links Fixed ([count])
- [file] → [old link] → [new link]

### Archive Candidates ([count])
- [file] - [reason] - **PENDING USER APPROVAL**

---

## Questions for User

[Only if Decision Framework triggered "ask user"]

1. **Phase 2 Completion**: Auto-detected 92% complete. Mark as done?
2. **New Tasks**: Found 7 new TODOs. Add all to tasks.md?
3. **Archive**: phase1_foundation hasn't been touched in 45 days. Archive?

---

## Next Sync Priorities

1. [Priority 1 based on current phase]
2. [Priority 2 based on detected blockers]
3. [Priority 3 based on stale tasks]

---

## Errors/Warnings

[Any issues encountered during sync]

---

## State Update
- Last commit processed: [CURRENT_COMMIT]
- Last run: [ISO 8601 timestamp]
- Files processed: [count]
```

---

## Phase 8: State Persistence (5 seconds)

### Update State File
```bash
jq --arg commit "$CURRENT_COMMIT" \
   --arg time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
   --argjson files "$(echo "$ALL_CHANGES" | jq -R . | jq -s .)" \
   '.last_commit = $commit | .last_run = $time | .files_processed = $files' \
   "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
```

### Cleanup
```bash
rm -f "$LOCK_FILE"
```

---

## Performance Budget (Total: ~5 minutes)

| Phase | Time Budget | Optimization |
|-------|-------------|--------------|
| Git Detection | 30s | Use git plumbing commands |
| Categorization | 60s | Parallel file reads |
| Task Detection | 90s | Regex-based parsing |
| Doc Sync | 60s | Only update changed files |
| Link Validation | 45s | Only check modified .md files |
| Archive Detection | 30s | Cache file stats |
| Report Generation | 15s | Template-based |
| State Update | 5s | Single file write |

**Hard Timeout**: 6 minutes (fail-safe)

---

## Decision Framework Summary

### Auto-Execute (No User Input)
- ✅ Completion % changes <10%
- ✅ <5 broken links detected
- ✅ <3 new tasks added
- ✅ Metric updates
- ✅ Status updates based on commits
- ✅ Adding completed tasks to checklist

### Ask User (Uncertain)
- ❓ Completion % changes >10%
- ❓ >5 new tasks detected
- ❓ Phase marked as 100% complete
- ❓ Task in progress >14 days
- ❓ Any archive operations
- ❓ >5 broken links
- ❓ Major structural changes detected

### Never Auto-Execute (Always Ask)
- 🚫 Archiving any files
- 🚫 Deleting content
- 🚫 Changing phase priorities
- 🚫 Marking phases complete without tests passing
- 🚫 Major PRD alignment changes

---

## Error Handling

### Recoverable Errors
- Git command fails → Skip that phase, continue
- File read fails → Log error, continue with next file
- JSON parse fails → Use backup state from previous run

### Fatal Errors
- Lock file stuck (>2 hours old) → Alert user, exit
- State file corrupted → Alert user, request manual recovery
- Git repo not found → Exit immediately

### Rollback Procedure
```bash
# If sync caused issues, rollback:
git checkout HEAD -- conductor/
git checkout HEAD -- PROJECT_STATUS_REVIEW.md
# Restore state file from backup
cp .ralph-loop-state/last-sync.json.backup .ralph-loop-state/last-sync.json
```

---

## Integration with Other Agents

### For Gemini CLI (L1 Orchestrator)
- Read: `SYNC_REPORTS/sync-latest.md` for current status
- Use: Phase % completion for delegation decisions
- Check: "Questions for User" section for escalations

### For Claude Code (L2 Generator)
- Read: `conductor/tasks.md` for current task assignments
- Read: `conductor/current.md` for sprint context
- Update: Create commits with structured messages for auto-detection

### For Jules (L2 Builder)
- Read: Infrastructure changes from sync report
- Update: Docker/config changes should trigger sync
- Check: Configuration change detection in reports

---

## Ralph-Loop CLI Integration

### Hourly Execution
```bash
# Cron job (every hour)
0 * * * * /usr/local/bin/ralph-loop run /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync.md --timeout 360

# Or using ralph-loop daemon mode
ralph-loop daemon \
  --prompt /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync.md \
  --interval 3600 \
  --timeout 360 \
  --log /home/samalabam/code/unified-cmtg/.ralph-loop-state/sync.log
```

### Manual Trigger
```bash
# Force immediate sync
ralph-loop run /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync.md

# Dry-run mode (preview only)
ralph-loop run /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/project-sync.md --dry-run
```

---

## Success Criteria

✅ Completes in <5 minutes
✅ Accurately detects completed tasks (>95% accuracy)
✅ Zero false positives on phase completion
✅ All agents can read latest status from sync reports
✅ User only interrupted for high-confidence questions
✅ Git is single source of truth
✅ Handles concurrent development (multiple agents committing)
✅ Recovers gracefully from errors

---

## Version History
- **v1.0** (2026-01-15): Initial git-integrated design for hourly sync
