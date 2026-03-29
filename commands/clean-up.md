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

2. **Check for common problems**
   - Dead code (unused variables, functions, imports)
   - Code complexity (long functions, deep nesting)
   - Missing error handling (try/catch, validation)
   - Naming issues (unclear variables, inconsistent conventions)
   - Hardcoded values (should be constants/config)
   - Missing docstrings/comments for complex logic
   - Type safety issues (untyped parameters, implicit any)
   - Check against patterns in `docs/spec/CONVENTIONS.md`

3. **Run automated linters**
   - Run the lint/format commands from CLAUDE.md's "Testing & Linting" section
   - Fix issues reported by linters

4. **Report findings**
   - List issues by severity
   - Categorize: formatting, complexity, safety, naming
   - Suggest refactoring if applicable
   - Do not change logic or functionality

## Output

```
Issues found in current diff:

FORMATTING (auto-fixed):
- 2 lines with trailing whitespace
- 1 import not alphabetized

CODE QUALITY:
- [src/utils.ts] Unused variable 'tempData' on line 42
- [models.py] Function 'process_data' is 150 lines (consider splitting)
- [hooks/useAuth.ts] Missing error handling in catch block

NAMING:
- [serializers.py] Parameter 'x' should be 'user_data'
```
