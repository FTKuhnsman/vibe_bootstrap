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
  - mcp__Claude_Preview__preview_start
  - mcp__Claude_Preview__preview_stop
  - mcp__Claude_Preview__preview_snapshot
  - mcp__Claude_Preview__preview_screenshot
  - mcp__Claude_Preview__preview_console_logs
  - mcp__Claude_Preview__preview_eval
  - mcp__Claude_Preview__preview_click
  - mcp__Claude_Preview__preview_fill
  - mcp__Claude_Preview__preview_logs
  - mcp__Claude_Preview__preview_network
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

1. **Read context:**
   - `docs/plan/FEATURES.md` — feature spec and acceptance criteria
   - `docs/plan/DECISIONS.md` — architecture decisions to respect
   - `docs/plan/DEPENDENCIES.md` — change impact matrix
   - `docs/spec/ARCHITECTURE.md` — system design and data flow
   - `docs/spec/CONVENTIONS.md` — code patterns and standards
   - `CLAUDE.md` — stack, testing commands, conventions
   - `docs/plan/ACTIVE.md` — what's in flight (avoid conflicts)
   - Relevant source code for affected areas

2. **Enter plan mode** and design the implementation:
   - Break work into numbered steps with sub-steps
   - Identify files each step creates/modifies (file ownership — no overlap between agents)
   - Define verification gates between steps
   - Identify which steps can run in parallel (backend + frontend independence)
   - Plan TDD: which tests to write before implementation

3. **Get user approval** on the plan before proceeding

4. **Create progress file:** `docs/plan/PROGRESS_F-XXX.md`
   ```markdown
   # F-XXX: [Feature Name] — Implementation Progress

   ## Step 1: [name]
   - [ ] 1a. [sub-step]
   - [ ] 1b. [sub-step]

   ## Step 2: [name]
   - [ ] 2a. [sub-step]
   ```

5. **Create feature branch:** `git checkout -b feature/F-XXX-short-name`

6. **Update ACTIVE.md:** Mark feature as in-progress

### Phase 2: TDD — Write Tests First (Agents)

For each step that changes application logic:

1. **Dispatch test-writing agents** (backend + frontend can run in parallel):
   - Each agent gets: files to read (reference), files to create (test files), completion criteria
   - Tests should define the expected behavior of the new code
   - Tests WILL FAIL initially — that's expected
   - Follow testing patterns from `docs/spec/CONVENTIONS.md`

2. **Verify tests were written:** Run the test commands from CLAUDE.md's "Testing & Linting" section to confirm tests exist and fail as expected

3. **Update progress file** — mark test sub-steps complete

### Phase 3: Implement (Agents)

1. **Dispatch implementation agents** in parallel batches:
   - Each agent owns specific files (no overlap)
   - Agent prompt includes: files to read, files to modify, patterns to follow (reference CLAUDE.md and docs/spec/CONVENTIONS.md), what NOT to do
   - Backend and frontend agents run in parallel when independent

2. **After each batch:**
   - Run full test suite using commands from CLAUDE.md's "Testing & Linting" section
   - Fix any failures (coordinator fixes or dispatches focused fix agent)
   - Update progress file — mark implementation sub-steps complete
   - Commit the step: `git commit` with conventional message

### Phase 4: Browser Smoke Test (Coordinator)

1. **Start dev servers** using `preview_start` for servers in `.claude/launch.json`
2. **Test the feature end-to-end:**
   - Navigate to the relevant page using `preview_eval`
   - Use `preview_snapshot` to verify page structure
   - Use `preview_fill` and `preview_click` to interact with forms/buttons
   - Use `preview_console_logs` with `level: error` to check for runtime errors
   - Use `preview_network` to verify API calls
   - Follow any app-specific flows defined in CLAUDE.md's "Smoke Test Flows" section
3. **If bugs found:**
   - Log with `/bug log`
   - Fix immediately
   - Re-run smoke test
4. **Update progress file** — mark smoke test complete

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

## Agent Dispatch Template

When dispatching agents, each prompt must include:
```
Files to READ (reference only): [list]
Files to CREATE or MODIFY: [list]
Patterns to follow: [reference CLAUDE.md and docs/spec/CONVENTIONS.md]
Completion criteria: [what "done" looks like]
What NOT to do: [scope guard]
```

## Commit Convention

One commit per logical step:
- `feat(F-XXX): [step description]`
- `test(F-XXX): [test description]`
- `fix(B-XXX): [bug fix found during implementation]`
- `docs: [documentation updates]`
