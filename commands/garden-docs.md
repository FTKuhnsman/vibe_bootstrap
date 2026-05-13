---
description: Scan spec documents for staleness against the codebase and optionally fix them. Dispatches the doc-gardener subagent.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - Agent
---

# Garden Docs

Scan specification documents for staleness against the actual codebase and optionally apply fixes.

## Usage

```
/garden-docs                          # Report mode: scan and print findings
/garden-docs --report                 # Write report to docs/plan/GARDEN_REPORT_<date>.md
/garden-docs --fix                    # Apply fixes on a branch (do not merge)
/garden-docs --scope ARCHITECTURE.md  # Scope to a single spec file
```

Default is report mode (read-only). `--fix` creates a branch and applies corrections.

## Process

### 1. Determine scope

Spec files to scan (all under `docs/spec/` unless `--scope` narrows it):

| File | What to check |
|------|---------------|
| `ARCHITECTURE.md` | Module names, directory paths, data-flow descriptions match actual code structure |
| `API.md` | Endpoint paths, method signatures, request/response shapes match implementation |
| `STACK.md` | Listed dependencies match `package.json` / `requirements.txt` / equivalent; versions are current |
| `CONVENTIONS.md` | Patterns described (naming, file structure, import style) match what `grep`/`glob` finds in the codebase |
| `LAYERS.md` | Layer names and module-to-layer mappings match actual directory layout |
| `GOLDEN_PRINCIPLES.md` | GP rules reference commands/files that still exist |
| `SMOKE_TEST.md` | Test scenarios reference routes/components that exist |
| `AGENT_DISPATCH.md` | Subagent roster matches `.claude/agents/` contents |

### 2. Dispatch the `doc-gardener` subagent

Dispatch with the five-field contract:

- **Files to read:** The spec files in scope + the codebase files they reference (discovered by grepping the spec for paths, function names, route patterns)
- **Files to modify:** None in report mode. In `--fix` mode: the spec files in scope.
- **Work:** For each spec file, compare every factual claim (file path exists, function signature matches, dependency version is current, module listed in layer mapping exists) against the codebase. Produce a findings list: `[file:section, claim, actual, severity]`.
- **Completion criteria:** A structured report with all findings categorized as `stale` (claim no longer true), `missing` (codebase has something the spec doesn't mention), or `ok` (claim verified).
- **Scope guard:** In report mode, do not modify any file. In `--fix` mode, only modify spec files listed in scope — never modify source code.

### 3. Report or fix

**Report mode (default):** Print the findings grouped by spec file. If `--report` is set, also write to `docs/plan/GARDEN_REPORT_<YYYY-MM-DD>.md`.

**`--fix` mode:**
1. Create a branch: `git checkout -b garden-docs/<date>`
2. Re-dispatch the `doc-gardener` subagent with Edit permission. The agent updates stale claims in the spec files to match the codebase.
3. If the spec contains executable examples (code blocks with paths), run them after editing to verify correctness.
4. Commit: `docs: garden-docs sweep — <count> stale claims updated`
5. Print the branch name. Do not merge — the branch is for human review.

### 4. Update the garden log

Append a line to `docs/plan/GARDEN_LOG.md` (create if missing):

```markdown
| Date | Mode | Specs scanned | Stale claims | Missing items | Notes |
|------|------|---------------|-------------|---------------|-------|
| 2026-05-12 | report | 6 | 4 | 2 | STACK.md has outdated React version |
```

## Anti-patterns to avoid

- **Updating specs to match broken code.** If the code is wrong and the spec is right, file a bug instead of "fixing" the spec.
- **Fixing source code from this command.** `/garden-docs` only modifies spec files. Source code fixes belong in `/fix-bug` or `/refactor`.
- **Running `--fix` without reviewing the branch.** Always review the diff before merging — the gardener may misinterpret a deliberate divergence as staleness.
