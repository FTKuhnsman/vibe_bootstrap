---
description: Fix a bug using the coordinated workflow. Reproduce, write failing test, fix, verify in browser.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - Agent
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

# Fix Bug

Fix a bug using the structured reproduce → test → fix → verify workflow.

## Usage

```
/fix-bug B-XXX                      # Fix a tracked bug by ID
/fix-bug [description]              # Fix from description (auto-logs as new bug)
```

## Process

### Step 1: Understand the Bug

1. **Read bug details:**
   - If B-XXX given, read from `docs/plan/BUGS.md`
   - If description given, auto-log as new bug using `/bug log`
2. **Read affected source code** — understand the component and its dependencies
3. **Read context:**
   - `docs/plan/DEPENDENCIES.md` — identify what else could break
   - `docs/spec/ARCHITECTURE.md` — understand data flow through the affected area

### Step 2: Reproduce

1. **Try to reproduce in browser first:**
   - Confirm dev servers from `.claude/launch.json` are running (start them via `Bash` if not — chrome-devtools MCP does NOT start servers)
   - Open a Chrome page with `new_page` (or reuse one via `list_pages` + `select_page`); navigate to the affected URL via `navigate_page`
   - Follow reproduction steps from bug report
   - Use `list_console_messages` and `take_snapshot` to capture the error
   - If reproducible, note the exact error and state
2. **If not browser-reproducible**, reproduce via test:
   - Write a minimal test case that triggers the bug

### Step 3: Write Failing Test

1. **Write a test that captures the bug:**
   - The test should FAIL with the current code
   - The test should PASS once the bug is fixed
   - Follow testing patterns from `docs/spec/CONVENTIONS.md`
   - Place in the appropriate test file for the affected module
2. **Run the test to confirm it fails** using the test commands from CLAUDE.md

### Step 4: Fix

1. **For simple bugs** (1-3 files): Fix directly
2. **For complex bugs** (4+ files or cross-module): Dispatch agent(s) with:
   - Files to read (reference)
   - Files to modify (ownership)
   - The failing test as the completion criterion
   - Scope guard (fix only the bug, don't refactor)

### Step 5: Verify

1. **Run the failing test** — confirm it now PASSES
2. **Run full test suite** — confirm no regressions (use commands from CLAUDE.md)
3. **Browser smoke test** the fix:
   - Navigate to affected area
   - Follow original reproduction steps
   - Verify the bug no longer occurs
   - Check `list_console_messages` for zero errors (filter to `level === 'error'`)
4. **Check for related issues:**
   - Does the same pattern exist elsewhere? (Use `grep` to search)
   - If yes, fix all instances

### Step 6: Close

1. **Update `docs/plan/BUGS.md`:**
   - Change status to `closed`
   - Add fix date and brief description of fix
2. **Commit:**
   ```
   fix(B-XXX): [brief description]
   ```
3. **Report results to user**

## Quick Path for Trivial Bugs

If the bug is clearly trivial (typo, off-by-one, missing null check):
1. Skip plan mode
2. Write the test, fix, verify, commit
3. Still run browser smoke test if it's a UI bug
