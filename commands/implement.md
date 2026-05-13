---
description: Implement a feature end-to-end using the multi-agent coordinated workflow. Plan, TDD, parallel agents, verify, smoke test.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - Agent
  - EnterPlanMode
  - ExitPlanMode
  - TodoWrite
  - mcp__chrome-devtools__new_page
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__close_page
  - mcp__chrome-devtools__list_pages
  - mcp__chrome-devtools__select_page
  - mcp__chrome-devtools__take_snapshot
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__list_console_messages
  - mcp__chrome-devtools__evaluate_script
  - mcp__chrome-devtools__click
  - mcp__chrome-devtools__fill
  - mcp__chrome-devtools__fill_form
  - mcp__chrome-devtools__list_network_requests
  - mcp__chrome-devtools__wait_for
---

# Implement

End-to-end feature implementation using the multi-agent coordinated workflow.

## Usage

```
/implement F-XXX                    # Implement a feature by ID
/implement [description]            # Implement from description
/implement --resume                 # Resume from progress file
```

## Process

### Phase 1: Plan (Coordinator)

1. **Check feature status (lifecycle gate):**
   - Read the feature's status from `docs/plan/FEATURES.md`
   - Apply the `can_implement()` gate (see `lib/validate.py`):
     - `stub` → **REFUSE.** Print: "Feature F-XXX is a stub. Run `/feature discovery F-XXX` to promote it to backlog first."
     - `done` → **REFUSE.** Print: "Feature F-XXX is already done."
     - `backlog`, `in-progress`, `blocked`, or no status field → **PROCEED.**
   - This gate is a tested invariant (see `tests/test_lifecycle_gate.py`). It cannot be weakened without a visible test change.

2. **Read context:**
   - `docs/spec/GOLDEN_PRINCIPLES.md` — the mechanical rules every agent must respect
   - `docs/spec/AGENT_DISPATCH.md` — the five-field dispatch contract
   - `docs/spec/LAYERS.md` — canonical dependency direction
   - `docs/plan/FEATURES.md` — feature spec and acceptance criteria
   - `docs/plan/discovery/F-XXX-*.md` — design discovery doc (if `/feature discovery` was run; provides background, alternatives, decisions)
   - `docs/plan/DECISIONS.md` — architecture decisions to respect
   - `docs/plan/DEPENDENCIES.md` — change impact matrix
   - `docs/spec/ARCHITECTURE.md` — system design and data flow
   - `docs/spec/CONVENTIONS.md` — code patterns and standards
   - `docs/spec/SMOKE_TEST.md` — browser-test playbook (read before Phase 4)
   - `CLAUDE.md` — stack, testing commands, navigation map
   - `docs/plan/ACTIVE.md` — what's in flight (avoid conflicts)
   - Relevant source code for affected areas

3. **Enter plan mode** and design the implementation:
   - Break work into numbered steps with sub-steps
   - Identify files each step creates/modifies (file ownership — no overlap between agents)
   - Define verification gates between steps
   - Identify which steps can run in parallel (backend + frontend independence)
   - Plan TDD: which tests to write before implementation
   - For each dispatched subagent (`test-writer`, `implementer`), specify the five-field dispatch contract and list relevant `GP-NNN` IDs (e.g., "GP-002 — schema-validate the request body", "GP-013 — tool grants enforce scope")

4. **Get user approval** on the plan before proceeding

5. **Create progress file:** `docs/plan/PROGRESS_F-XXX.md`
   ```markdown
   # F-XXX: [Feature Name] — Implementation Progress

   ## Step 1: [name]
   - [ ] 1a. [sub-step]
   - [ ] 1b. [sub-step]

   ## Step 2: [name]
   - [ ] 2a. [sub-step]
   ```

6. **Create feature branch:** `git checkout -b feature/F-XXX-short-name`

7. **Update ACTIVE.md:** Mark feature as in-progress

### Phase 2: TDD — Write Tests First (via `test-writer` subagent)

For each step that changes application logic:

1. **Dispatch the `test-writer` subagent** (backend + frontend can run in parallel):
   - Provide the five-field dispatch contract per `docs/spec/AGENT_DISPATCH.md`:
     - **Files to read:** spec files, discovery doc, existing source code for context
     - **Files to modify:** the test file(s) to create
     - **Work:** what behavior to test (happy path, error cases, edge cases)
     - **Completion criteria:** tests exist and fail with the expected error
     - **Scope guard:** do not create or modify any non-test file
   - The `test-writer` agent has NO Bash access (enforced by tool grants — see GP-013)
   - Tests WILL FAIL initially — that's expected
   - Follow testing patterns from `docs/spec/CONVENTIONS.md`

2. **Verify tests were written:** Run the test commands from CLAUDE.md's "Testing & Linting" section to confirm tests exist and fail as expected

3. **Update progress file** — mark test sub-steps complete

### Phase 3: Implement (via `implementer` subagent)

1. **Dispatch the `implementer` subagent** in parallel batches:
   - Provide the five-field dispatch contract:
     - **Files to read:** the failing tests (primary context), spec files, discovery doc
     - **Files to modify:** the production files to create/update (no overlap between agents)
     - **Work:** make the failing tests pass
     - **Completion criteria:** all tests pass, lint clean
     - **Scope guard:** which files and layers NOT to touch
   - The `implementer` reads failing tests first — they are the specification
   - Backend and frontend `implementer` dispatches run in parallel when independent

2. **After each batch:**
   - Run full test suite using commands from CLAUDE.md's "Testing & Linting" section
   - Fix any failures (coordinator fixes or dispatches focused fix agent)
   - Update progress file — mark implementation sub-steps complete
   - Commit the step: `git commit` with conventional message

### Phase 4: Browser Smoke Test (Coordinator)

Skip this phase entirely if the change has no UI impact (pure models/migrations/CLI/background tasks with no template or component touched).

1. **Confirm dev servers are running** (chrome-devtools MCP does NOT start servers):
   - Read `.claude/launch.json` for the configured server commands and ports
   - Check each port responds; if not, start via `Bash` as a background process and track the PID
2. **Open Chrome and navigate:**
   - `new_page(url: <frontend-url>)` — or reuse a page via `list_pages` + `select_page`
   - `navigate_page` to the relevant route
3. **Test the feature end-to-end:**
   - Use `take_snapshot` to verify page structure
   - Use `fill` / `fill_form` / `click` for form interaction
   - Use `evaluate_script` for controlled inputs, portal-rendered components, or DOM queries that `click`/`fill` can't handle
   - Use `list_console_messages` (filter `level === 'error'`) — must be zero
   - Use `list_network_requests` to verify API calls succeeded
   - Follow any app-specific flows + gotchas in CLAUDE.md's "Smoke Test Flows" and "Browser Smoke Test Playbook" sections
4. **If bugs found:**
   - Log with `/bug log`
   - Fix immediately
   - Re-run smoke test
5. **Stop servers** if you started them; leave alone if the user did
6. **Update progress file** — mark smoke test complete

### Phase 5: Finalize (Coordinator)

1. **Run full verification** using commands from CLAUDE.md's "Testing & Linting" and "Verification Checklist" sections:
   - Backend tests — all pass
   - Frontend tests — all pass (if applicable)
   - Build — no errors (if build command defined)
   - Backend lint — clean
   - Frontend lint — clean (if applicable)

2. **Update docs:**
   - `docs/plan/FEATURES.md` — mark acceptance criteria checked, status done
   - `docs/plan/ACTIVE.md` — move to completed
   - `docs/plan/DECISIONS.md` — add new architecture decisions if any
   - `docs/plan/BUGS.md` — close any bugs fixed during implementation

3. **Final commit and report**

## Resume Support

If `$ARGUMENTS` is `--resume`:
1. Search for `docs/plan/PROGRESS_*.md` files
2. Find the most recent one with incomplete steps
3. Read it and resume from the first incomplete sub-step
4. All committed work is safe — pick up exactly where it left off

## Agent Dispatch Specification

See **`docs/spec/AGENT_DISPATCH.md`** for the canonical five-field spec, TDD step structure, discovery-to-implementation bridge, and anti-patterns. Every dispatch in this command's plan MUST honor that spec.

Quick reference (five required fields): **Files to read**, **Files to modify**, **Work**, **Completion criteria**, **Scope guard**.

## Verification gate per batch

After each agent batch:
1. Run full test suite (commands from CLAUDE.md's "Testing & linting" section).
2. Run `/check-layers --diff` — any GP-006 violations block the next batch.
3. Update the PROGRESS file checkboxes.

## Commit Convention

One commit per logical step:
- `feat(F-XXX): [step description]`
- `test(F-XXX): [test description]`
- `fix(B-XXX): [bug fix found during implementation]`
- `refactor(GP-NNN): [GP-driven cleanup that happened during the work]`
- `docs: [documentation updates]`
