# Agent Handoffs

This directory enables structured task handoffs between AI agents without copy-pasting prompts.

## Structure

```
handoffs/
├── CURRENT.md     # Currently active task
├── QUEUE.md       # Priority-ordered task queue
├── jules/
│   ├── inbox.md   # Tasks for Jules to pick up
│   └── outbox.md  # Completed tasks (for review)
├── claude/
│   ├── inbox.md   # Tasks for Claude Code
│   └── outbox.md  # Completed tasks
└── gemini/
    ├── inbox.md   # Tasks for Gemini CLI
    └── outbox.md  # Completed tasks
```

## Protocol

### When Starting Work
1. Check your `inbox.md`
2. Move task to `CURRENT.md`
3. Execute the task

### When Completing Work
1. Move task from inbox to your `outbox.md` with completion notes
2. Write next task to appropriate agent's `inbox.md`
3. Commit: `git commit -m "handoff: [from] → [to]: [task summary]"`
4. Push to trigger notifications

## Quick Commands

```bash
# Check your inbox
cat conductor/handoffs/$(whoami)/inbox.md

# Delegate to Jules via GitHub
gh issue create --title "Task X" --label "jules"

# Or comment on any issue
gh issue comment 123 --body "/jules fix the auth bug"
```

## Integration with GitHub

- Issues labeled `jules` auto-trigger Jules workflow
- Issues labeled `conductor` auto-add to tasks.md
- Self-hosted runner on dell-brain executes workflows
