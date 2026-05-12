---
description: Enforce GP-006 (one-way dependencies). Reads docs/spec/LAYERS.md and reports backward imports — code in a lower layer importing from a higher layer.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Check Layers

Verify that the codebase's dependency direction matches the canonical layer model defined in `docs/spec/LAYERS.md`. Enforces `GP-006`.

## Usage

```
/check-layers                          # Full scan, print violations
/check-layers --since HEAD~50          # Only check files changed in the last 50 commits
/check-layers --diff                   # Only check files in the current uncommitted diff
/check-layers --layer service          # Only check imports out of one named layer
/check-layers --explain GP-006         # Print the rule and exit
```

## Process

### 1. Load the layer model

Read `docs/spec/LAYERS.md`. Parse:
- The ordered list of layers (lowest → highest).
- The module → layer mapping table (pattern → layer name).
- The "Allowed exceptions" section — keep a set of `(file, target_layer)` pairs to skip.

**Opt-out check:** If LAYERS.md contains the literal `does not enforce a layered architecture`, print `LAYERS.md opt-out detected — /check-layers is a no-op.` and exit 0.

### 2. Build the file → layer index

For each tracked source file (`git ls-files`), match it against the module-mapping patterns. The first matching pattern wins. Files that match nothing are recorded as `unmapped` — these are warnings, not violations.

If `--since <ref>` or `--diff` is set, restrict the index to changed files.

### 3. Scan imports

For each file in the index:

- **Python:** grep for `^(from|import)\s+(\S+)` lines.
- **TypeScript/JavaScript:** grep for `^(import|export)\s+.*from\s+['"](.+)['"]` lines, plus `require('...')`.
- **Go:** grep within `import (...)` blocks.
- **Other:** add stack-specific patterns from `docs/spec/STACK.md` if defined.

For each import target:
1. Resolve it to a project file (skip stdlib and third-party imports).
2. Look up the target's layer using the same mapping.
3. Compare: if `source_layer_index > target_layer_index` → OK. If equal → OK. If `source_layer_index < target_layer_index` → **violation**.
4. Skip the violation if it appears in LAYERS.md's "Allowed exceptions" section.

### 4. Report

Print findings grouped by source layer:

```
/check-layers — GP-006 enforcement

VIOLATIONS (must fix):
[types → service]   backend/types/user.py:3
                    imports backend/services/auth.py
                    fix: move shared piece into types/ or invert the dependency

[repo → service]    backend/repo/queries.py:18
                    imports backend/services/normalizer.py
                    fix: pass the normalized value as a parameter from the service layer

WARNINGS (unmapped files):
- scripts/migrate_legacy.py (no layer mapping in LAYERS.md)
- backend/wsgi.py (no layer mapping)

OK:
- 247 files checked
- 0 same-layer imports flagged
- 12 allowed exceptions skipped
```

### 5. Exit code

- **0** — no violations (warnings allowed).
- **1** — one or more violations.
- **2** — couldn't parse LAYERS.md or the layer model is incomplete (no mappings).

This makes `/check-layers` safe to wire into CI: failing exit code blocks merge until the model is consistent.

## How to fix violations

Each violation has two paths forward (per GP-006's auto-fix hint):

1. **Invert the dependency.** Pass the higher-layer object as a parameter from the call site, or extract the shared piece into a lower layer.
2. **Document the exception.** If the violation is genuinely unavoidable, add an entry to LAYERS.md's "Allowed exceptions" section with a one-sentence reason and a date. `/check-layers` will skip the violation on the next run.

Prefer (1). (2) is for cases where the layer model has a real gap that you'll address later.

## Anti-patterns to avoid

- **Blanket exceptions.** Don't add entries like "all of `backend/legacy/`" to the exceptions section. Exceptions are file-level and time-bounded.
- **Layer thrashing.** Don't reshuffle the layer order to avoid a fix. The order in LAYERS.md is the contract; if you change it, every consumer has to be reviewed.
- **Skipping `--since` runs.** The full scan is the source of truth; `--since` is for fast feedback during work, not for hiding pre-existing violations.

## Related rules and files

- `GP-006` in `docs/spec/GOLDEN_PRINCIPLES.md`
- `docs/spec/LAYERS.md` — the canonical layer model
- `/garbage-collect` — broader Golden Principle sweep; defers layering specifically to this command
