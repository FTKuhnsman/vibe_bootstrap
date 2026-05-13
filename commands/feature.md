---
description: Feature management. Add, stub, list, view, update features in FEATURES.md. Run design discovery for new features. Filter by status, priority, phase.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - EnterPlanMode
  - ExitPlanMode
---

# Feature

Manage the project feature backlog in `docs/plan/FEATURES.md`.

## Commands

Parse `$ARGUMENTS` to determine which subcommand to run. If no arguments given, default to `list`.

### /feature add [name]
Add a new feature to the backlog.

1. Read `docs/plan/FEATURES.md` and scan for the highest existing `F-XXX` ID
2. Auto-assign the next sequential ID
3. Only **name** and **description** are required. Ask the user for those if not provided. All other fields use sensible defaults:
   - **Name** — from arguments, or ask
   - **Description** — what and why (from arguments, or ask)
   - **Priority** — P0/P1/P2/P3 (default: P1)
   - **Status** — `backlog` (default) — see lifecycle below
   - **Estimated Effort** — S/M/L/XL (default: M)
   - **Phase** — phase number (default: next unfinished phase)
   - **Acceptance Criteria** — optional; leave empty until `/feature discovery` fills them in
   - **Dependencies** — other F-XXX IDs, or "None"
   - **Notes** — optional context
4. Append the feature to the appropriate phase section in FEATURES.md
5. Confirm creation with ID and summary

### /feature stub [name1] [name2] ...
Bulk-create placeholder features with status `stub`.

1. Read `docs/plan/FEATURES.md` and find the highest `F-XXX` ID
2. For each name provided, create a minimal entry:
   - Auto-assign sequential IDs
   - Set **Status** to `stub`
   - Set **Priority** to P2, **Effort** to M (defaults)
   - Leave **Acceptance Criteria** empty — stubs are not implementable until discovery runs
3. Append all entries to the Backlog (Unphased) section
4. Confirm: "Created N stub features: F-XXX, F-YYY, ..."

**Stub lifecycle:** A `stub` feature cannot be implemented. Run `/feature discovery F-XXX` to flesh it out — discovery promotes the status to `backlog`, making it eligible for `/implement`. This prevents half-baked features from entering the implementation pipeline.

### /feature list [filters]
List features with optional filters.

1. Read `docs/plan/FEATURES.md`
2. Parse all features into a structured list
3. Apply filters: `--status=stub|backlog|in-progress|done|blocked`, `--priority=P0|P1|P2|P3`, `--phase=N`
4. Display as a compact table
5. Show count: "Showing X of Y features"

### /feature view F-XXX
Show full details of a specific feature.

### /feature update F-XXX [changes]
Update one or more fields on an existing feature.
- `--status=in-progress|done|backlog|stub|blocked`, `--priority=P0`, `--effort=L`, `--phase=5`
- When marking as `done`, auto-append today's date

### /feature discovery [F-XXX or name]
Run a structured design discovery for a feature. This is the canonical path from idea to implementable spec.

**Process:**

1. **Enter planning mode**
2. **Identify the feature** from F-XXX ID, name, or ask
3. **Dispatch the `discovery-interviewer` subagent** with:
   - **Files to read:** `docs/plan/FEATURES.md`, `docs/plan/DECISIONS.md`, `docs/spec/ARCHITECTURE.md`, `docs/spec/CONVENTIONS.md`, `docs/plan/ACTIVE.md`, `docs/plan/BUGS.md`, existing `docs/plan/discovery/` docs, relevant source code
   - **Files to modify:** `docs/plan/discovery/F-XXX-feature-name.md` (new discovery doc)
   - **Work:** Walk the user through the 15-section discovery interview: Problem & Users, User Stories, Requirements (functional + non-functional), Architecture Fit, UI/UX, Real-Time considerations, Dependencies, Impact Analysis, Technical Approach (options with pros/cons), Data Model, API Contract, Error Handling, Acceptance Criteria, Effort Estimate, Open Questions
   - **Completion criteria:** Discovery doc saved with all sections filled
   - **Scope guard:** Do not write implementation code. Do not modify non-discovery files.
4. **After the subagent completes:**
   - Record decisions in `docs/plan/DECISIONS.md` (auto-assign D-XXX IDs)
   - Update FEATURES.md: promote status from `stub` → `backlog` (if it was a stub), fill in acceptance criteria, effort, priority, and phase from discovery output
   - If the feature was a `stub`, the promotion to `backlog` makes it eligible for `/implement`
5. **Exit planning mode**

## Feature Lifecycle

```
stub → backlog → in-progress → done
                 ↕
               blocked
```

| Status | Meaning | `/implement` allowed? |
|--------|---------|----------------------|
| `stub` | Placeholder — needs discovery first | No (see `lib/validate.py:can_implement()`) |
| `backlog` | Fully specified, ready to build | Yes |
| `in-progress` | Currently being built | Yes (resume) |
| `blocked` | Waiting on external dependency | Yes (unblock + resume) |
| `done` | Shipped and verified | No |

Features without a `status:` field are treated as `backlog` for backward compatibility.

The lifecycle gate is enforced mechanically by `can_implement()` in `lib/validate.py`. The `/implement` command calls this function before proceeding — a `stub` feature is refused with a message pointing to `/feature discovery`.

## Priority Reference

- **P0:** Critical path — blocks other features
- **P1:** High value — should ship in v1
- **P2:** Nice-to-have — post-MVP
- **P3:** Low priority — deferred

## Effort Reference

- **S:** 1–2 days | **M:** 3–5 days | **L:** 1–2 weeks | **XL:** 2+ weeks
