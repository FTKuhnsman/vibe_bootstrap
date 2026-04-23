---
description: Refactor code using TDD and multi-agent coordination. Simplify, extract patterns, improve architecture.
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
  - mcp__chrome-devtools__list_console_messages
  - mcp__chrome-devtools__evaluate_script
  - mcp__chrome-devtools__list_network_requests
---

# Refactor

Refactor code safely using TDD, parallel agents, and verification gates.

## Usage

```
/refactor [description]              # Describe what to refactor
/refactor --resume                   # Resume from progress file
```

## Process

### Step 1: Analyze (Coordinator)

1. **Understand the refactoring scope:**
   - Read the affected files
   - Identify the pattern to extract, simplify, or reorganize
   - Check `docs/plan/DEPENDENCIES.md` for impact analysis
   - Check `docs/spec/CONVENTIONS.md` for target patterns
   - Check `CLAUDE.md` for relevant standards

2. **Enter plan mode** and design the refactoring:
   - Break into small, verifiable steps
   - Each step should leave the codebase in a working state
   - Identify file ownership per agent
   - Prioritize backward compatibility

3. **Get user approval** on the approach

4. **Create progress file:** `docs/plan/PROGRESS_refactor_[name].md`

5. **Create branch:** `git checkout -b refactor/[short-name]`

### Step 2: Write Tests First (Agents)

For each refactoring step:

1. **Write tests that define the expected behavior of the NEW code:**
   - If extracting a mixin/factory: test the new abstraction directly
   - If moving code: test that the new location works
   - Tests SHOULD FAIL initially

2. **Verify existing tests still pass** — the refactoring must not break them

### Step 3: Implement (Agents)

1. **Dispatch agents in parallel batches** (backend + frontend independent)
2. **After each batch:**
   - Run full test suite using commands from CLAUDE.md — ALL existing + new tests must pass
   - Fix any regressions immediately
   - Commit the step
   - Update progress file

### Step 4: Verify (Coordinator)

1. **Full test suite** — run all test commands from CLAUDE.md
2. **Browser smoke test:** Start servers, verify affected UI still works, zero console errors
3. **Lint check** — run all lint commands from CLAUDE.md

### Step 5: Finalize

1. **Update docs** if the refactoring changes architecture:
   - `CLAUDE.md` — update standards/conventions
   - `docs/plan/DECISIONS.md` — record the decision
   - `docs/plan/DEPENDENCIES.md` — update dependency graph
   - `docs/spec/ARCHITECTURE.md` — update if structure changed
   - `docs/spec/CONVENTIONS.md` — update if new patterns established
2. **Final commit and report**

## Principles

- **Never break existing tests** — every intermediate step must pass
- **Smaller batches > fewer batches** — more frequent verification
- **Extract, don't rewrite** — prefer incremental extraction over big-bang rewrites
- **Test the abstraction** — new patterns (mixins, factories, utils) get their own tests
- **Backward compatibility** — re-export from old locations when moving code
