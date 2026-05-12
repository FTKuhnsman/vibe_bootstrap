---
description: Code quality review of current diff. Check for issues without changing functionality.
allowed-tools:
  - Bash(git diff:*)
  - Bash
  - Read
---

# Clean Up

Code quality review of uncommitted changes. Identifies issues in current diff without modifying functionality.

## Process

1. **Review current diff**
   - Run `git diff HEAD` to view all staged and unstaged changes
   - Analyze changes for quality issues

2. **Apply Golden Principle auto-fix hints**
   - Read `docs/spec/GOLDEN_PRINCIPLES.md`
   - For each `GP-NNN` rule, scan the diff for violations
   - For each violation found, apply the rule's **Auto-fix hint** — these are agent-safe by design
   - Skip violations the auto-fix hint cannot resolve without judgement; surface them in the report instead

3. **Check for common problems** (catch what GP didn't)
   - Dead code (unused variables, functions, imports) — GP-008
   - Code complexity (long functions, deep nesting)
   - Missing error handling — GP-004 covers the message format
   - Naming issues (unclear variables, inconsistent conventions)
   - Hardcoded values (should be constants/config) — GP-011 for env-derived values
   - Missing docstrings/comments for complex logic — GP-007 for public APIs
   - Type safety issues (untyped parameters, implicit any) — GP-007
   - Check against patterns in `docs/spec/CONVENTIONS.md`

4. **Run automated linters**
   - Run the lint/format commands from CLAUDE.md's "Testing & Linting" section
   - Fix issues reported by linters

5. **Report findings**
   - List issues by severity, grouped by GP-ID where applicable
   - Categorize: GP violations, formatting, complexity, safety, naming
   - Suggest refactoring if applicable
   - Do not change logic or functionality — `/clean-up` only applies fixes that the GP auto-fix hint guarantees are behavior-preserving

## Output

```
Issues found in current diff:

GP VIOLATIONS (auto-fixed where safe):
- [GP-008] src/utils.ts:42 — Unused variable 'tempData' (auto-fix applied: deleted)
- [GP-011] backend/views.py:18 — Direct os.environ read (NEEDS REVIEW: moved to config.py)
- [GP-004] backend/api.py:55 — Bare `raise Exception('failed')` — left for manual review

FORMATTING (auto-fixed):
- 2 lines with trailing whitespace
- 1 import not alphabetized

CODE QUALITY (no auto-fix applied):
- [models.py] Function 'process_data' is 150 lines (consider splitting)
- [hooks/useAuth.ts] Missing error handling in catch block

NAMING:
- [serializers.py] Parameter 'x' should be 'user_data'
```
