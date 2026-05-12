# Golden Principles

Mechanical, opinionated rules that keep this codebase legible for agents and humans alike. Inspired by OpenAI's [harness engineering](https://openai.com/index/harness-engineering/) methodology.

## How to read this file

- Each rule has a stable ID (`GP-NNN`). Reference these IDs in commits, code comments, lint output, and PR descriptions.
- The **Auto-fix hint** is written for agents — it should be safe to act on without further context.
- Numbering is append-only. Never recycle an ID, even after a rule is retired (mark it `RETIRED` instead).
- These are the project's defaults. Curate them: delete rules you disagree with, add ones that catch recurring drift.

## Commands that consult this file

| Command | How it uses GP rules |
|---------|----------------------|
| `/garbage-collect` | Scans the codebase for violations, opens targeted refactor branches |
| `/review` | Includes GP compliance as a review category before PR |
| `/clean-up` | Applies auto-fix hints to the current diff |
| `/implement`, `/refactor` | Reads rules as constraints during the plan phase |
| `/check-layers` | Enforces GP-006 specifically (layered dependencies) |

---

## GP-001 — Centralize invariants in shared utilities

**Rule:** Prefer importing from an existing shared utility over writing a new helper inline.

**Why:** Hand-rolled helpers fragment behavior across the codebase. When invariants drift between near-duplicate helpers, agents (and humans) confidently make changes against the wrong copy.

**How to apply:** Before writing a helper, grep the project's `utils/` (or equivalent) module for existing functions that do — or nearly do — the job. If you must add a new helper, put it in the canonical utility module rather than next to the call site.

**Auto-fix hint:** Move the helper to the canonical utilities module and import it. If a near-duplicate already exists, delete the new one and use the existing implementation.

---

## GP-002 — Validate at boundaries, never probe shapes

**Rule:** At every external boundary (HTTP request, database row, env var, file, message queue payload), validate input with a typed schema. Inside the system, trust the validated shape.

**Why:** Code that probes data shape (`if 'key' in data`, `isinstance` chains, `data.get(...).get(...)`) hides invariants and lets bugs propagate silently. Agents reading such code cannot derive the contract.

**How to apply:** At each boundary, define a schema (Pydantic, Zod, dataclass, TypedDict, struct, protobuf — match the stack). Parse on entry. Propagate the typed object downstream — never raw dicts.

**Auto-fix hint:** Add a schema at the boundary. Replace probing chains with typed attribute access. If the shape is genuinely dynamic, declare it as `dict[str, Any]` and document the variation.

---

## GP-003 — One source of truth per concept

**Rule:** A given concept (a config value, a type definition, an enum, a route path, an error code, a constant) has exactly one definition. Every other usage imports it.

**Why:** Parallel definitions drift. The second copy almost always lags behind by one bug fix.

**How to apply:** Search for an existing definition before adding a new one. Re-export when needed; never re-declare.

**Auto-fix hint:** Delete the duplicate definition. Re-export from the canonical location and update imports.

---

## GP-004 — Errors carry actionable remediation

**Rule:** Every error message includes (a) what failed, (b) the offending value(s) when safe to log, and (c) what the caller should do next.

**Why:** An agent reading an error in a log should be able to act on it without re-deriving context. Bare `raise Exception('failed')` is hostile to every downstream reader.

**How to apply:** Use typed error classes with templated messages. The message format is: `"<what failed> for <value>: <how to fix or what to check>"`.

**Auto-fix hint:** Replace bare `raise Exception(...)` with a typed error class. Add the value and remediation hint to the message.

---

## GP-005 — Tests are deterministic and isolated

**Rule:** A test must produce the same result on any machine, any time of day, in any execution order, with no other tests running.

**Why:** Flake destroys the agent feedback loop. Agents cannot distinguish a flaky test from a real regression, so they either ignore failures (bad) or retry blindly (also bad).

**How to apply:** No `datetime.now()` / `Date.now()` without injection or freezing. No real network calls — mock them. No shared global state between tests. No "first run vs. subsequent run" branches. Use factories, not fixtures with mutable defaults.

**Auto-fix hint:** Inject the clock or freeze time. Mock the network call at the lowest layer. Move shared state into a fixture with explicit setup/teardown.

---

## GP-006 — Dependencies flow in one direction

**Rule:** Code in a lower layer never imports from a higher layer. See `docs/spec/LAYERS.md` for the canonical layer order in this project.

**Why:** Backward imports collapse the architecture. Once one is allowed, the boundary is gone — every refactor afterward has to wrestle the leak.

**How to apply:** Run `/check-layers` before merging significant changes. When tempted to import upward, invert the dependency: pass the higher-layer object as a parameter, or extract the shared piece into a lower layer.

**Auto-fix hint:** Replace the backward import with a parameter or dependency injection. If that's not feasible, extract the shared piece into a lower layer.

---

## GP-007 — Public APIs are typed and documented

**Rule:** Every function or method that crosses a module boundary has explicit types on all parameters and return value, plus a one-line docstring stating what it does.

**Why:** Agents reason from signatures. Untyped boundaries force every caller — human or agent — to read the implementation to know what to pass.

**How to apply:** Run the project's type checker as part of the verification gate. Avoid `Any` / `unknown` — narrow before merging. Prefer `from __future__ import annotations` in Python, `as const` in TypeScript where applicable.

**Auto-fix hint:** Add type annotations. If a parameter is `Any`, narrow it to the actual shape used or declare the variation explicitly.

---

## GP-008 — Dead code is deleted, not commented out

**Rule:** If code is unused, remove it. Do not leave commented-out blocks, `// removed in F-XXX` markers, or "we'll need this later" stubs.

**Why:** Dead code is noise in every grep, blame, and review. It misleads agents into thinking the codebase uses patterns it has abandoned. Git keeps the history — that is the paper trail.

**How to apply:** Delete unused functions, variables, imports, branches, fixtures, exports, and routes. If you genuinely need a paper trail, link the commit hash in the PR description.

**Auto-fix hint:** Delete the block outright. The previous version is recoverable via `git log -p -- <file>`.

---

## GP-009 — Cross-module side effects flow through documented events

**Rule:** When module A's action triggers behavior in module B, route it through a named signal/event with a documented payload — not through a direct import from A to B.

**Why:** Direct cross-module imports hard-wire the dependency graph and prevent the modules from being reasoned about independently. Side-effect chains hidden behind imports are the #1 source of "why did this change break that?".

**How to apply:** Define the signal in a dedicated `signals.py` / `events.ts` module. List the signal and its payload in `docs/spec/ARCHITECTURE.md`. Module B subscribes; module A emits.

**Auto-fix hint:** Replace the direct call with an `events.emit('<name>', payload)`. Add the signal name and payload schema to `docs/spec/ARCHITECTURE.md`.

---

## GP-010 — Prefer composition over inheritance

**Rule:** When extending behavior, default to composition (small functions or classes wired together) over inheritance hierarchies. Inheritance is reserved for clear `is-a` relationships in a narrow domain.

**Why:** Deep hierarchies are hostile to incremental change. Each subclass quietly couples to the implementation details of every ancestor; agents (and humans) cannot reason about a method without reading the full chain.

**How to apply:** Reach for a mixin or base class only after composition has been considered and rejected with a documented reason. Strategy objects, hooks, and utility functions are usually the right tool.

**Auto-fix hint:** Replace inheritance with a strategy object, hook, or utility function. If the hierarchy stays, add a one-line comment above the class explaining why.

---

## GP-011 — Configuration loads from one typed source

**Rule:** All runtime configuration is read from a single typed config module that validates env vars and config files at startup. Application code reads from this module — never directly from `os.environ` / `process.env` / `ENV[...]`.

**Why:** Scattered env reads make it impossible to enumerate the configuration surface area, fail fast on misconfiguration, or document what the app needs to run.

**How to apply:** Add a new variable to the central `config` module first (with type, default, and validation). Import from there everywhere else. The config module must raise at import time if a required value is missing.

**Auto-fix hint:** Move the env access into the config module. Replace direct reads with `from <project>.config import settings` (or equivalent).

---

## GP-012 — Generated code is regenerated, not edited

**Rule:** Files marked as generated (migrations, OpenAPI clients, GraphQL types, lockfiles, protobuf output, etc.) are produced by a script. Re-run the generator instead of editing by hand.

**Why:** Hand-edits to generated files drift from the source and break the next regeneration. The regeneration step then produces a confusing diff, and someone "fixes" it by editing the output again — and the cycle locks in.

**How to apply:** Find the generator command (usually in `package.json` scripts, a `Makefile`, or a `scripts/` directory). Re-run it. If the output is wrong, fix the input schema or generator config — not the output.

**Auto-fix hint:** Run the generator command. If the output is still wrong, modify the source schema/spec/template and re-run.

---

## Adding a new rule

When you find yourself making the same correction more than twice across PRs, encode it here. Format:

```markdown
## GP-NNN — <one-line statement>

**Rule:** <the rule, written as an imperative>

**Why:** <the cost the rule prevents — usually a past incident or a structural pain point>

**How to apply:** <when this rule applies and what to do>

**Auto-fix hint:** <agent-actionable remediation, safe to run without further context>
```

Bump the highest existing GP number by one. Add a one-line entry to the "Commands that consult this file" table if a new command checks the rule.

## Retiring a rule

Mark the rule heading as `## GP-NNN — RETIRED — <one-line statement>` and add a `**Retired:** <date and reason>` block. Do not delete the entry — preserving the ID prevents future rules from accidentally reusing the number, and old commits referencing the ID still resolve.
