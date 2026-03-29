---
description: View project status. Read planning files and summarize in-progress, blocked, backlog, bugs, decisions.
allowed-tools:
  - Read
  - Glob
---

# Plan

Display project status from planning documents.

## Process

1. **Locate planning files**
   - Read `ACTIVE.md` (in-progress work)
   - Read `FEATURES.md` (feature backlog)
   - Read `BUGS.md` (open bugs)
   - Read `DECISIONS.md` (recent architectural decisions)
   - Search from project root

2. **Parse and summarize**
   - In-progress: Extract items currently being worked on
   - Blocked: List blocked items with reasons
   - Top 5 backlog: Show highest priority upcoming features
   - Open bugs: Count by severity
   - Recent decisions: Show last 3-5 decisions with dates

3. **Filter with $ARGUMENTS**
   - Optional filter: `in-progress`, `blocked`, `bugs`, `backlog`, `decisions`
   - If provided, show only matching section

## Usage

```
/plan                    # Show all
/plan blocked            # Show only blocked items
/plan bugs               # Show only bugs
/plan backlog            # Show only feature backlog
```
