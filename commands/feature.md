---
description: Feature management. Add, list, view, update features in FEATURES.md. Run design discovery for new features. Filter by status, priority, phase.
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
3. Ask the user for any missing details (use sensible defaults where possible):
   - **Name** — from arguments, or ask
   - **Priority** — P0/P1/P2/P3 (default: P1)
   - **Estimated Effort** — S/M/L/XL (default: M)
   - **Phase** — phase number (default: next unfinished phase)
   - **Description** — what and why
   - **Acceptance Criteria** — bulleted checklist items
   - **Dependencies** — other F-XXX IDs, or "None"
   - **Notes** — optional context
4. Append the feature to the appropriate phase section in FEATURES.md
5. Confirm creation with ID and summary

### /feature list [filters]
List features with optional filters.

1. Read `docs/plan/FEATURES.md`
2. Parse all features into a structured list
3. Apply filters: `--status=backlog|in-progress|done`, `--priority=P0|P1|P2|P3`, `--phase=N`
4. Display as a compact table
5. Show count: "Showing X of Y features"

### /feature view F-XXX
Show full details of a specific feature.

### /feature update F-XXX [changes]
Update one or more fields on an existing feature.
- `--status=in-progress|done|backlog`, `--priority=P0`, `--effort=L`, `--phase=5`
- When marking as `done`, auto-append today's date

### /feature discovery [F-XXX or name]
Enter planning mode and walk through a structured design discovery for a feature.

**Process:**

1. **Enter planning mode**
2. **Identify the feature** from F-XXX ID, name, or ask
3. **Gather project context:**
   - `docs/plan/FEATURES.md` — existing features, dependencies
   - `docs/plan/DECISIONS.md` — accepted architecture decisions
   - `docs/spec/ARCHITECTURE.md` — system design
   - `docs/spec/CONVENTIONS.md` — code patterns
   - `docs/plan/ACTIVE.md` — what's in flight
   - `docs/plan/BUGS.md` — related known issues
   - Existing `docs/plan/discovery/` docs
   - Relevant source code as needed
4. **Walk through discovery interactively:**
   - Problem & Users
   - User Stories
   - Requirements (functional + non-functional)
   - Architecture Fit
   - UI/UX
   - Real-Time considerations
   - Dependencies
   - Impact Analysis
   - Technical Approach (options with pros/cons)
   - Acceptance Criteria
   - Effort Estimate
   - Open Questions
5. **Save** to `docs/plan/discovery/F-XXX-feature-name.md`
6. **Record decisions** in `docs/plan/DECISIONS.md`
7. **Update FEATURES.md** if needed
8. **Exit planning mode**

## Priority Reference

- **P0:** Critical path — blocks other features
- **P1:** High value — should ship in v1
- **P2:** Nice-to-have — post-MVP
- **P3:** Low priority — deferred

## Effort Reference

- **S:** 1–2 days | **M:** 3–5 days | **L:** 1–2 weeks | **XL:** 2+ weeks
