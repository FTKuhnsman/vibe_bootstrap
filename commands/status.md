---
description: Quick one-glance dashboard. Summary of project progress and priorities.
allowed-tools:
  - Read
  - Glob
---

# Status

Display quick project status dashboard from all planning files.

## Process

1. **Locate and read planning files**
   - Read `CLAUDE.md` header for project name
   - Read `ACTIVE.md` (in-progress items)
   - Read `FEATURES.md` (backlog and completed)
   - Read `BUGS.md` (open bugs by severity)
   - Read `DECISIONS.md` (recent decisions)
   - Search from project root

2. **Extract data**
   - Count items in each category
   - Identify blocked items
   - Count bugs by severity
   - Filter completed items from last 7 days
   - Find next priority in backlog

3. **Format dashboard output**

## Output Format

```
═══════════════════════════════════════════════════════════════
  [PROJECT NAME] STATUS
═══════════════════════════════════════════════════════════════

IN PROGRESS (N items):
  ► F-XX: [description]

  Run: /plan in-progress    Details: /task <id>

BLOCKED (N items):
  ⚠ F-XX: [description]
    Reason: [blocking reason]

  Run: /plan blocked    Unblock: /task unblock F-XX

OPEN BUGS (N total):
  🔴 CRITICAL (N):  B-XX [description]
  🟠 HIGH (N):      B-XX [description]
  🟡 MEDIUM (N):    B-XX [description]
  🔵 LOW (N):       B-XX [description]

  Run: /bug list    Log: /bug log [description]

BACKLOG (N items):
  📋 Next up: F-XX ([description])

  Top priorities:
    • F-XX: [description]
    • F-XX: [description]

  Run: /plan backlog    Pick next: /task next

COMPLETED (Last 7 days: N items):
  ✓ F-XX, F-XX

RECENT DECISIONS:
  📝 YYYY-MM-DD: [decision summary]

═══════════════════════════════════════════════════════════════
  Next action: /task start F-XX  or  /plan [section]
═══════════════════════════════════════════════════════════════
```

## Related Commands

- `/plan` - View detailed project plan
- `/task` - Manage tasks (add, start, done, block)
- `/bug` - Manage bugs (log, fix, close, list)
- `/review` - Code review before PR
- `/commit-push-pr` - Submit changes
