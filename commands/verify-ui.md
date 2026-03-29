---
description: Visual verification of UI using browser automation. Start servers, test flows, check console errors, log bugs.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Agent
  - mcp__Claude_Preview__preview_start
  - mcp__Claude_Preview__preview_stop
  - mcp__Claude_Preview__preview_snapshot
  - mcp__Claude_Preview__preview_screenshot
  - mcp__Claude_Preview__preview_console_logs
  - mcp__Claude_Preview__preview_eval
  - mcp__Claude_Preview__preview_click
  - mcp__Claude_Preview__preview_fill
  - mcp__Claude_Preview__preview_inspect
  - mcp__Claude_Preview__preview_logs
  - mcp__Claude_Preview__preview_network
  - mcp__Claude_Preview__preview_resize
---

# Verify UI

Browser-based visual verification of frontend functionality using the Claude Preview tools.

## Usage

```
/verify-ui                          # Full smoke test (all flows)
/verify-ui [flow]                   # Test specific flow
```

## Process

### 1. Start Dev Servers

Use `preview_start` for servers defined in `.claude/launch.json`:
- Start each configured server
- Wait for all to be ready
- Check `preview_logs` for startup errors

### 2. Read Flows

Read the "Smoke Test Flows" section of CLAUDE.md for app-specific test flows.

If no flows are defined, run the **default verification**:
1. Navigate to the app's root URL
2. `preview_snapshot` — verify something renders
3. `preview_console_logs(level: "error")` — zero errors
4. `preview_network` — no failed API calls
5. `preview_resize` — responsive layout check

### 3. Run Flows

For each flow (or the one specified in $ARGUMENTS):

1. Follow the steps described in CLAUDE.md
2. Use `preview_snapshot` (accessibility tree) for text/structure verification
3. Use `preview_fill` and `preview_click` for form interaction
4. Use `preview_eval` for complex interactions that click/fill can't handle
5. After form submission, wait 2-3 seconds before checking results
6. Check `preview_console_logs(level: "error")` after each major step

### 4. Cross-Flow Checks

After all flows complete:
1. `preview_console_logs(level: "error")` — zero errors total
2. `preview_network` — no failed API calls
3. `preview_resize` — responsive layout check

### 5. Log Issues

For each issue found:
- Use `/bug log` to create bug entry automatically
- Include: component, error message, reproduction steps
- Set severity based on impact:
  - Crash/error boundary triggered → S1
  - Broken functionality → S2
  - Visual/cosmetic → S3

### 6. Report Results

Output a summary table:

```
Flow          | Status | Issues
------------- | ------ | ------
[Flow 1]      | PASS   |
[Flow 2]      | FAIL   | B-XXX: [description]
Console Errors| PASS   | 0 errors
```

## Tips

- Use `preview_snapshot` (accessibility tree) over `preview_screenshot` for text verification
- Use `preview_eval` for complex interactions that `preview_click`/`preview_fill` can't handle
- Input selectors: check `input[type]`, `input[placeholder]`, or use `preview_eval` to inspect DOM
- If a page appears empty, check `preview_console_logs` for errors and `window.location.href` via `preview_eval`
