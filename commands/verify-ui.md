---
description: Visual verification of UI using browser automation. Drive real Chrome via chrome-devtools MCP, test flows, check console errors, log bugs.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Agent
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__new_page
  - mcp__chrome-devtools__close_page
  - mcp__chrome-devtools__select_page
  - mcp__chrome-devtools__list_pages
  - mcp__chrome-devtools__take_snapshot
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__click
  - mcp__chrome-devtools__fill
  - mcp__chrome-devtools__fill_form
  - mcp__chrome-devtools__type_text
  - mcp__chrome-devtools__hover
  - mcp__chrome-devtools__drag
  - mcp__chrome-devtools__press_key
  - mcp__chrome-devtools__handle_dialog
  - mcp__chrome-devtools__wait_for
  - mcp__chrome-devtools__evaluate_script
  - mcp__chrome-devtools__list_console_messages
  - mcp__chrome-devtools__get_console_message
  - mcp__chrome-devtools__list_network_requests
  - mcp__chrome-devtools__get_network_request
  - mcp__chrome-devtools__resize_page
  - mcp__chrome-devtools__emulate
---

# Verify UI

Browser-based visual verification of frontend functionality using the **chrome-devtools MCP**. Drives a real Chrome instance — no headless/sandboxed surprises.

## Usage

```
/verify-ui                          # Full smoke test (all flows)
/verify-ui [flow]                   # Test specific flow
```

## Process

### 1. Confirm Dev Servers Are Running

**The chrome-devtools MCP does NOT start servers.** Before any flow:

- Read `.claude/launch.json` for the configured server commands and ports
- Check each port is responding (e.g., `curl -s http://localhost:<port>/`)
- If a server is down, start it via `Bash` as a background process using the `runtimeExecutable` + `runtimeArgs` from `launch.json`. Track the PID so you can stop it later.
- If you cannot start a server (missing dependencies, port conflict), ask the user to start it in a separate terminal and continue once they confirm.

Open a Chrome page pointed at the frontend:
- `mcp__chrome-devtools__new_page(url: "<frontend-url>")` — or reuse an existing page via `list_pages` + `select_page`

### 2. Read Flows

Read the "Smoke Test Flows" section of CLAUDE.md for app-specific test flows.

If no flows are defined, run the **default verification**:
1. `navigate_page` to the app's root URL
2. `take_snapshot` — verify something renders
3. `list_console_messages` — zero errors (filter client-side for `level === 'error'`)
4. `list_network_requests` — no failed API calls (non-2xx)
5. `resize_page` — responsive layout check (e.g., 375×667 mobile + 1280×800 desktop)

### 3. Run Flows

For each flow (or the one specified in $ARGUMENTS):

1. Follow the steps described in CLAUDE.md
2. Use `take_snapshot` (accessibility tree) for text/structure verification
3. Use `fill` / `fill_form` and `click` for form interaction
4. Use `evaluate_script` for complex interactions that `click`/`fill` can't handle (controlled inputs, portal-rendered elements)
5. After form submission, `wait_for` an expected element or use a short delay before checking results
6. Check `list_console_messages` (errors only) after each major step

### 4. Cross-Flow Checks

After all flows complete:
1. `list_console_messages` — zero errors total
2. `list_network_requests` — no failed API calls
3. `resize_page` — responsive layout check

### 5. Stop Servers

If you started servers in step 1, stop them now (kill tracked PIDs via `Bash`). Leave servers alone if the user started them.

### 6. Log Issues

For each issue found:
- Use `/bug log` to create bug entry automatically
- Include: component, error message, reproduction steps
- Set severity based on impact:
  - Crash/error boundary triggered → S1
  - Broken functionality → S2
  - Visual/cosmetic → S3

### 7. Report Results

Output a summary table:

```
Flow          | Status | Issues
------------- | ------ | ------
[Flow 1]      | PASS   |
[Flow 2]      | FAIL   | B-XXX: [description]
Console Errors| PASS   | 0 errors
```

## Tips

- Prefer `take_snapshot` (accessibility tree) over `take_screenshot` for text verification — faster and survives overlays
- Use `evaluate_script` for complex interactions that `click`/`fill` can't handle (e.g., React-controlled date pickers, RN TextInputs that ignore native DOM events)
- Selector strategy: prefer `[data-testid="..."]` and `[aria-label="..."]`. Pseudo-selectors like `:has-text()` are NOT supported.
- If `click` doesn't trigger React state updates, fall back to `evaluate_script` with `document.querySelector('selector').click()`
- For portal-rendered modals/toasts: `take_snapshot` may miss them — query directly with `evaluate_script`
- See CLAUDE.md "Browser Smoke Test Playbook" for stack-specific gotchas
