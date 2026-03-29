---
description: Task management. Add, start, complete, block, unblock tasks. Pick next priority item.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash(git status:*)
---

# Task

Manage project tasks (features/work items).

## Commands

### /task add [description]
Create new feature in backlog.
- Auto-generates ID: `F-<next-number>`
- Adds to FEATURES.md with status "backlog"
- Capture: title, description, affected areas

### /task start F-XXX
Move feature to in-progress.
- Move from backlog to ACTIVE.md
- Update status to "in-progress"
- Record start timestamp

### /task done F-XXX
Move feature to completed.
- Move from ACTIVE.md to FEATURES.md
- Update status to "completed"
- Record completion timestamp

### /task block F-XXX [reason]
Mark feature as blocked.
- Update status to "blocked"
- Store blocking reason

### /task unblock F-XXX
Remove blocked status.
- Update status back to previous state

### /task next
Recommend next highest-priority item.
- Find highest priority non-blocked backlog item
- Consider dependencies
- Suggest for /task start

## Process

1. Parse $ARGUMENTS for command and parameters
2. Read current planning documents
3. Update FEATURES.md and/or ACTIVE.md
4. Confirm change to user
5. Show updated status
