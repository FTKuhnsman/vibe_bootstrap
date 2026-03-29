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

2. **Check correctness**
   - Logic flow matches requirements
   - No off-by-one errors or state issues
   - Function signatures and types correct
   - API contracts honored (check `docs/spec/API.md`)

3. **Security review**
   - XSS vulnerabilities: User input properly escaped/sanitized
   - SQL injection: ORM usage correct, no raw queries with user input
   - Auth bypass: Permission checks in place, proper token handling
   - CSRF protection: Forms include tokens, API requires headers
   - Secrets management: No credentials in code, uses env vars
   - Check against patterns in `docs/spec/CONVENTIONS.md` security section

4. **Performance check**
   - N+1 queries: Database queries optimized
   - Re-renders: Memoization where needed
   - Unnecessary network calls: Debounce, request deduplication
   - Large data handling: Pagination, virtualization if needed

5. **Accessibility**
   - ARIA labels on interactive elements
   - Keyboard navigation support
   - Color contrast sufficient
   - Form labels associated with inputs

6. **Error handling**
   - Try/catch blocks for async operations
   - Proper error messages for users
   - Graceful fallbacks
   - No silent failures

7. **Test coverage**
   - Tests exist for critical paths
   - Error cases tested
   - Coverage adequate for complexity

8. **Prioritize findings**
   - Critical: Security, data loss, crashes
   - High: Logic errors, major bugs
   - Medium: Performance, error handling
   - Low: Style, minor improvements
