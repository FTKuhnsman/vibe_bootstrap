---
description: Bug management. Log, fix, close bugs. Track by severity.
allowed-tools:
  - Read
  - Write
  - Edit
---

# Bug

Manage project bugs and issues.

## Commands

### /bug log [description]
Create new bug report.
- Auto-generates ID: `B-<next-number>`
- Adds to BUGS.md with status "open"
- Capture: title, description, severity, reproduction steps, affected component
- Severity levels: critical, high, medium, low
- Auto-called during /verify-ui if issues found

### /bug fix B-XXX
Mark bug as being worked on.
- Update status to "in-progress"
- Record fix start timestamp

### /bug close B-XXX
Close bug as resolved.
- Update status to "closed"
- Record close timestamp
- Optionally link to commit or PR that fixed it

### /bug list
Show all open bugs.
- Display grouped by severity
- Show description, component, date opened
- Highlight critical/high priority

## Process

1. Parse $ARGUMENTS for command and parameters
2. Read BUGS.md
3. Update bug entry or create new one
4. Confirm change to user
5. Show updated bug list/status

## Auto-Logging

During `/verify-ui`, if console errors or broken flows are detected:
- Automatically create bug entries
- Do not ask for permission
- Set appropriate severity based on impact
- Include reproduction steps from UI testing
