# Simple Ralph-Loop Sync - Usage

## Three Ways to Run

### Option 1: Direct Command (Recommended)
Copy and paste this exact command:

```bash
/ralph-loop:ralph-loop "Sync docs in /home/samalabam/code/unified-cmtg/unified-platform: Run git log -n 10 and git status. Read conductor/tasks.md and conductor/current.md. Update tasks.md by moving completed work to checkmark section and adding new TODOs to pending. Update current.md with fresh timestamp and completion percentage. Write summary to SYNC_REPORTS/sync-latest.md. Output SYNC_COMPLETE when done." --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

**When prompted for permission: APPROVE IT**

### Option 2: Using the File
If the above works, you can also use:

```bash
/ralph-loop:ralph-loop "$(cat /home/samalabam/code/unified-cmtg/.ralph-loop-prompts/simple-sync.txt)" --max-iterations 10 --completion-promise "SYNC_COMPLETE"
```

### Option 3: Ask Claude to Run It
Just say to me: "Run the simple sync now"

And I'll execute the workflow manually in this session.

## What Happens

1. **Iteration 1**: Git analysis + first doc updates
2. **Iteration 2**: Validation + corrections
3. **[If needed]**: Claude asks clarification questions, you answer
4. **Iteration 3**: Continue with your answers
5. **Final iteration**: Final check + SYNC_COMPLETE

Typical completion: **2-4 iterations** (~3-5 minutes)

## Clarification Workflow

If Claude is unsure about something, it will STOP and ask you:

```
CLARIFICATION NEEDED:
Question 1: I found a commit "feat: add processor" but no tests - mark as complete?
Question 2: Found 7 new TODOs in code - should I add all to tasks.md?
```

**You respond** with your answers:

```
1. No, don't mark complete without tests
2. Yes, add all 7 TODOs
```

**Claude continues** the next iteration using your guidance.

### When Claude Asks

- Ambiguous commit messages
- Task might be done but no test evidence
- More than 5 new tasks found
- Completion % would jump more than 10%
- Conflicting info in git vs docs
- Unsure if TODO is real or just a comment

## What Gets Updated

- `conductor/tasks.md` - Task status (completed ✅, pending ⏳, in-progress 🟡)
- `conductor/current.md` - Sprint status, timestamp, completion %
- `SYNC_REPORTS/sync-latest.md` - Summary of what changed

## After Completion

Check the results:
```bash
cat SYNC_REPORTS/sync-latest.md
```

## Example Session with Clarifications

```
=== Iteration 1 ===
Checking git log...
Found 8 commits since last sync.
Reading tasks.md and current.md...

CLARIFICATION NEEDED:
Question 1: Found commit "feat: add rate sheet processor" but I don't see test files - should I mark "Implement rate sheet processor" as complete?
Question 2: Found 6 new TODO comments in backend code - should I add all 6 to tasks.md or are some just developer notes?
Question 3: Completion would jump from 75% to 88% - is this accurate or should I recount?

[YOU RESPOND:]
1. No, don't mark complete without tests. Move to "In Progress" instead.
2. Add only the ones that say "TODO:" not the ones that say "MAYBE:"
3. Recount carefully, 88% seems high.

=== Iteration 2 ===
Continuing with your guidance...
- Moved rate sheet processor to In Progress (not complete)
- Added 4 TODO tasks (skipped 2 MAYBE comments)
- Recounted: actual completion is 82%
- Updated tasks.md and current.md

All criteria met. SYNC_COMPLETE
```

## Troubleshooting

**Permission denied**: Approve the command when prompted

**Still blocked**: Use Option 3 (ask me to run it manually)

**Claude asks too many questions**: Adjust the thresholds (change "3 tasks" to "5 tasks" in the prompt)

**Claude doesn't ask enough**: Lower thresholds or add "When in doubt, ask me" to the prompt

**Loop doesn't complete**: Check SYNC_REPORTS/sync-latest.md for questions

**Cancel anytime**: `/cancel-ralph`
