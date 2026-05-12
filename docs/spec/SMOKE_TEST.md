# Browser Smoke Test Playbook

Reference for `/verify-ui` and the smoke-test phase of `/implement`, `/fix-bug`, and `/refactor`. Populate the placeholders below with your stack-specific gotchas as you discover them — these are starting points, not exhaustive rules.

This playbook assumes the [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) is installed (tools named `mcp__chrome-devtools__*`).

## Smoke test flows

<!-- Define app-specific browser test flows for /verify-ui to execute. Example:

### Auth flow
1. Navigate to /login
2. Verify login form renders
3. Fill email and password, submit
4. Verify redirect to dashboard

### Main feature flow
1. Navigate to /dashboard
2. Click "Create New"
3. Fill form and submit
4. Verify item appears in list
-->

_Run `/spec` to help populate this section based on your app's routes and features._

## Prerequisites

<!-- Document anything required before flows can run:
- Test user(s) and how to create them (e.g., a Django shell snippet, a seed script)
- Auth token storage location (e.g., localStorage key name)
- Required env vars or feature flags
- Seed data or fixtures
-->

## Creating test data

<!-- When form submission fails (e.g., React-controlled inputs that ignore native DOM events,
custom date pickers, RN TextInputs), create data via API using evaluate_script:

```js
const token = localStorage.getItem('<your-token-key>');
const res = await fetch('/api/<resource>/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
  body: JSON.stringify({...})
});
return res.status;
```

Then navigate_page directly to the page under test.
-->

## Clicking elements

<!-- Selector strategy:
- Prefer [data-testid="..."] and [aria-label="..."] selectors.
- Pseudo-selectors like :has-text() are NOT supported.
- If `click` doesn't trigger a React state update, fall back to evaluate_script with
  document.querySelector('selector').click().
-->

## Portal / modal components

<!-- Components rendered via portal to document.body (modals, toasts, bottom sheets) may
not appear in take_snapshot. Query them directly via evaluate_script:
document.querySelector('[data-testid="..."]') or [role="dialog"].

take_screenshot may time out when modals/overlays are open — use evaluate_script to
inspect DOM instead.
-->

## Verification order

Run these in sequence per page or per interaction:

1. **`list_console_messages`** — zero errors required (filter `level === 'error'`).
2. **`take_snapshot`** — verify page structure and text content.
3. **`evaluate_script`** — DOM inspection, portal components, debug state.
4. **`list_network_requests`** — confirm API calls succeeded (no non-2xx responses).
5. **`take_screenshot`** — visual proof (skip if it times out with modals open).

## When to skip the smoke test

The smoke test phase can be skipped entirely when the change has zero UI surface area:

- Pure model / migration / schema changes with no template or component touched.
- Background tasks, cron jobs, CLI tools.
- Pure backend refactors that don't change the API response shape.

If any of those *do* affect the API, run `/verify-ui` for at least one consumer flow.

## Stack-specific gotchas

<!-- Populate as you encounter them. Example entries:

### Django + React (Vite)
- The Vite dev server proxies /api to the Django backend — both must be running.
- Django's CSRF middleware requires the X-CSRFToken header from /api/auth/csrf/ first.

### Next.js
- Hydration mismatches log as console errors — fix them before smoke tests are reliable.
- next/image triggers /_next/image requests that may show as non-2xx during the first load.
-->
