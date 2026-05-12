---
description: Pre-PR code review. Check correctness, security, performance, accessibility, error handling, test coverage.
allowed-tools:
  - Bash(git diff:*)
  - Bash
  - Read
---

# Review

Comprehensive code review of current changes before submitting PR.

## Process

1. **Get current changes**
   - Run `git diff HEAD` to see all changes
   - Review scope and intent

2. **Golden Principles check** (do this first — mechanical rules catch the biggest legibility issues)
   - Read `docs/spec/GOLDEN_PRINCIPLES.md`
   - For each `GP-NNN`, scan the diff for violations
   - Flag each violation with its GP-ID and the rule's auto-fix hint
   - GP-006 specifically: run `/check-layers --diff` and include the output

3. **Check correctness**
   - Logic flow matches requirements
   - No off-by-one errors or state issues
   - Function signatures and types correct (GP-007)
   - API contracts honored (check `docs/spec/API.md`)

4. **Security review**
   - XSS vulnerabilities: User input properly escaped/sanitized
   - SQL injection: ORM usage correct, no raw queries with user input
   - Auth bypass: Permission checks in place, proper token handling
   - CSRF protection: Forms include tokens, API requires headers
   - Secrets management: No credentials in code, uses env vars (GP-011)
   - Check against patterns in `docs/spec/CONVENTIONS.md` security section

5. **Performance check**
   - N+1 queries: Database queries optimized
   - Re-renders: Memoization where needed
   - Unnecessary network calls: Debounce, request deduplication
   - Large data handling: Pagination, virtualization if needed

6. **Accessibility**
   - ARIA labels on interactive elements
   - Keyboard navigation support
   - Color contrast sufficient
   - Form labels associated with inputs

7. **Error handling**
   - Try/catch blocks for async operations
   - Proper error messages for users (GP-004: actionable remediation in every error)
   - Graceful fallbacks
   - No silent failures

8. **Test coverage**
   - Tests exist for critical paths
   - Error cases tested
   - Coverage adequate for complexity
   - Tests are deterministic (GP-005 — no `datetime.now()`, no real network)

9. **Prioritize findings**
   - Critical: Security, data loss, crashes, GP violations marked critical
   - High: Logic errors, major bugs, high-severity GP violations
   - Medium: Performance, error handling, medium-severity GP violations
   - Low: Style, minor improvements, low-severity GP violations
