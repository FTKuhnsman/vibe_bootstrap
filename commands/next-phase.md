---
description: Automatically extract and execute the next unfinished phase from FEATURES.md
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - Agent
---

# Next Phase

Automatically determine and execute the next development phase.

## Process

### Step 1: Determine the current phase

1. Read `docs/plan/FEATURES.md` and identify all phases
2. For each phase, check if ALL features have status `done`
3. The next phase is the first one with incomplete features
4. Read `docs/plan/ACTIVE.md` to confirm nothing is currently in progress

### Step 2: Extract scope

1. List all features in the next phase with their IDs and descriptions
2. Read acceptance criteria for each feature
3. Check dependencies — ensure prerequisite features are complete

### Step 3: Confirm before executing

Announce:
```
NEXT PHASE: Phase [N]
Features:
  - F-XXX: [name] (effort: M)
  - F-XXX: [name] (effort: L)
Estimated scope: [brief description]

Ready to execute?
```

Wait for user approval before proceeding.

### Step 4: Execute

For each feature in the phase:
1. Run `/implement F-XXX` using the full coordinated workflow
2. Verify each feature is complete before moving to the next
3. If a feature blocks, mark it and move to the next non-blocked one

### Step 5: Verify and report

After completing all features in the phase:

1. Run full test suite using commands from CLAUDE.md
2. If tests fail, debug and fix until they pass
3. Run `/status` to display the updated project state
4. Announce completion:
```
PHASE [N] COMPLETE
Tests: [X] passed
Features completed: [F-XXX, F-XXX]
Next up: Phase [N+1]

Run /next-phase again to continue, or review the changes first.
```

### Important Rules

- NEVER skip a phase — they must be executed in order
- If a phase is partially complete, resume where it left off
- If tests fail after 5 fix attempts, STOP and report the issue
- Commit working code at the end of each feature
