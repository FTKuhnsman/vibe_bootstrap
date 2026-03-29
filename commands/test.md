---
description: Generate tests for specified component/feature. Create happy path, error states, edge cases.
allowed-tools:
  - Bash
  - Write
  - Read
  - Glob
---

# Test

Generate comprehensive tests for a specified component or feature.

## Process

1. **Parse arguments**
   - $ARGUMENTS specifies what to test (e.g., `LoginForm`, `auth-service`)
   - Required: component/feature name
   - Optional: specific test cases to focus on

2. **Analyze the code**
   - Locate source file(s) for the component
   - Understand inputs, outputs, side effects
   - Identify external dependencies (API calls, state)
   - Note edge cases and error scenarios

3. **Read testing conventions**
   - Check `docs/spec/CONVENTIONS.md` for testing patterns (fixtures, mocks, structure)
   - Check existing test files nearby for patterns to follow

4. **Create test file**
   - Place test file according to project conventions (co-located or in tests/ directory)
   - Follow the test runner and assertion patterns from CLAUDE.md's "Testing & Linting" section
   - Include docstrings explaining test purpose

5. **Write test cases**
   - **Happy path**: Normal use, expected behavior
   - **Error states**: Invalid input, API failures, network errors
   - **Edge cases**: Boundary values, empty states, race conditions
   - **Integration**: Component interactions, state updates
   - Minimum 3-5 tests per component

6. **Run tests**
   - Use the test command from CLAUDE.md's "Testing & Linting" section
   - Verify all tests pass
   - Check coverage if available

7. **Report**
   - List tests created
   - Coverage percentage
   - Any skipped tests with reason

## Example

```
/test LoginForm          # Test the LoginForm component
/test authenticate       # Test auth service function
/test payment-processing # Test payment module
```
