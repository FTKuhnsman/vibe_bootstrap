---
description: View project status. Read planning files and summarize in-progress, blocked, backlog, bugs, decisions. Use --phases for a phase-grouped feature overview.
allowed-tools:
  - Read
  - Glob
  - Grep
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
   - Optional filter: `in-progress`, `blocked`, `bugs`, `backlog`, `decisions`, `--phases`
   - If provided, show only matching section

## Usage

```
/plan                    # Show all
/plan blocked            # Show only blocked items
/plan bugs               # Show only bugs
/plan backlog            # Show only feature backlog
/plan --phases           # Show features grouped by phase with completion stats
```

## --phases subcommand

When `$ARGUMENTS` contains `--phases`:

1. Read `docs/plan/FEATURES.md`
2. Parse every feature entry using `lib/validate.py:parse_features()` — extract F-ID, name, status, priority, effort, and phase
3. Group features by phase number. Features without a phase go under "Unphased".
4. For each phase, compute:
   - Total features
   - Count by status: stub, backlog, in-progress, blocked, done
   - Completion percentage: `done / total * 100`
5. Render a table per phase:

```
## Phase 1 — 60% complete (3/5 done)

| F-ID   | Name              | Status      | Priority | Effort |
|--------|-------------------|-------------|----------|--------|
| F-001  | User auth         | done        | P0       | L      |
| F-002  | Dashboard         | in-progress | P0       | XL     |
| F-003  | Notifications     | backlog     | P1       | M      |
| F-004  | Admin panel       | done        | P1       | L      |
| F-005  | User settings     | done        | P2       | S      |

## Phase 2 — 0% complete (0/3 done)

| F-ID   | Name              | Status      | Priority | Effort |
|--------|-------------------|-------------|----------|--------|
| F-006  | Reports           | stub        | P1       | L      |
| F-007  | Export            | stub        | P2       | M      |
| F-008  | Integrations      | backlog     | P1       | XL     |
```

6. End with a summary line: "N features across M phases. X done, Y in-progress, Z stub."
