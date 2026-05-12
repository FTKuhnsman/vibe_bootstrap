# Agent Dispatch Specification

How the coordinator dispatches subagents during `/implement`, `/refactor`, `/fix-bug`, and `/garbage-collect`. Edit this file when your team's dispatch patterns drift from what's described here — every command that dispatches agents reads from this spec.

## The five required fields

Every agent dispatch MUST include all five fields. A dispatch that omits any of them is invalid and the coordinator should reject it before running.

| Field | Purpose | Example |
|-------|---------|---------|
| **Files to read** | Reference context (read-only) | `core/models.py`, `core/tests/test_permissions.py` |
| **Files to modify** | Ownership — only this agent touches these | `core/permissions.py`, `core/signals.py` |
| **Work** | Bullet list of specific tasks | "Create `can_view_module()` with organizer bypass; emit signal on grant/revoke" |
| **Completion criteria** | How to verify the agent succeeded | "Permission and signal tests pass" |
| **Scope guard** | What the agent must NOT touch | "Only `core/permissions.py` and `core/signals.py` — no view or model changes" |

## Dispatch rules

- **No file ownership overlap** between concurrent agents. If two agents need to modify the same file, run them sequentially.
- **One verification gate per batch.** After each batch of concurrent agents completes, run the full test suite before starting the next batch.
- **Maximize parallelism within constraints.** Group agents so backend + frontend (or independent backend modules) run together.
- **Cap concurrency at 3 agents per batch.** More than that and the coordinator's context gets noisy.
- **Reference Golden Principles by ID** in dispatch prompts where they apply. "Follow GP-002 — schema-validate the request body" is clearer than restating the rule.
- **Cite the spec files** the agent should read: `docs/spec/CONVENTIONS.md`, `docs/spec/ARCHITECTURE.md`, `docs/spec/LAYERS.md`, and any feature-specific discovery doc.

## TDD step structure

Each implementation step follows red → green → verify:

1. **RED step** — A dedicated test-writing agent creates failing tests that define the expected contract.
   - Tests MUST be written before implementation.
   - The test agent's scope guard explicitly forbids implementing models/views/components.
   - Commit failing tests with: `test(F-XXX): add failing tests for [component]`.

2. **GREEN step** — Implementation agents (parallel where independent) make the tests pass.
   - Each implementation agent reads the failing tests as part of its reference context.
   - Commit when all tests pass: `feat(F-XXX): implement [component]`.

3. **VERIFY** — Full test suite run between every step.
   - Fix regressions immediately before proceeding to the next step.

## Discovery-to-implementation bridge

When `/feature discovery` produces a discovery doc, the implementation plan MUST include:

1. **Step 0 — Setup**
   - Create feature branch off the integration branch.
   - Create `docs/plan/PROGRESS_F-XXX.md` with checkboxes for every step.
   - Save the discovery doc to `docs/plan/discovery/F-XXX-feature-name.md`.
   - Record any new architecture decisions in `docs/plan/DECISIONS.md` (auto-assign D-XXX IDs).
   - Add or update feature entries in `docs/plan/FEATURES.md`.
   - Commit: `docs: add F-XXX discovery and decisions`.

2. **Steps 1–N — TDD cycles** — Each cycle is RED → GREEN → VERIFY → COMMIT with explicit agent dispatches per the five-field spec above.

3. **Integration verify** — Full backend + frontend test suites, linting, build check.

4. **Browser smoke test** — `/verify-ui` with the scenarios listed in the discovery doc (skip if no UI impact). See `docs/spec/SMOKE_TEST.md` for the playbook.

5. **Documentation cleanup** — Update FEATURES.md (mark acceptance criteria checked), ACTIVE.md (move to completed), the PROGRESS file (final checkboxes), DECISIONS.md (any new D-XXX), and BUGS.md (close any bugs fixed in passing).

## Session resilience

If a session dies mid-implementation:

- Check `docs/plan/PROGRESS_*.md` for the last completed sub-step.
- Resume from the next incomplete sub-step.
- All committed work is safe.
- Use `/implement --resume` (or `/refactor --resume`) to auto-detect and continue.

## Anti-patterns to reject

- **Implicit ownership.** "Update the user model" without listing the file — reject; coordinator must name `users/models.py` explicitly.
- **Open scope.** "Refactor as you see fit" — reject; scope guard must enumerate forbidden files or layers.
- **Mixed responsibilities.** One agent writing both tests and implementation — split into RED and GREEN agents.
- **Cross-batch dependencies.** Agent in batch 2 requires a file written by agent in batch 1, but batch 1's verification didn't gate on that file existing — restructure so the dependency is explicit.
- **No completion criteria.** "Just implement it" — reject; the criteria must be a sentence the coordinator can mechanically check (test passes, file exists, function returns expected value).
