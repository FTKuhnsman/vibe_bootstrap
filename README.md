# vibe_bootstrap

A reusable harness for building software with [Claude Code](https://claude.ai/claude-code). Clone, run `setup.py`, and you get the full multi-agent workflow described in OpenAI's [harness engineering](https://openai.com/index/harness-engineering/) post — adapted for any stack.

---

## Table of contents

1. [Why](#why)
2. [Mental model](#mental-model)
3. [Quick start](#quick-start)
4. [End-to-end walkthroughs](#end-to-end-walkthroughs)
   - [4.1 Initialize a new project](#41-initialize-a-new-project)
   - [4.2 Implement a complex feature](#42-implement-a-complex-feature)
   - [4.3 Debug a bug](#43-debug-a-bug)
   - [4.4 Refactor](#44-refactor)
   - [4.5 Continuous cleanup](#45-continuous-cleanup)
5. [Daily operating practices](#daily-operating-practices)
6. [Commands reference](#commands-reference)
7. [Spec system](#spec-system)
8. [Harness engineering alignment](#harness-engineering-alignment)
9. [Presets](#presets)
10. [Customization](#customization)
11. [Project structure](#project-structure)
12. [FAQ](#faq)

---

## Why

Building software with Claude Code is powerful, but the workflow — slash commands, planning docs, spec files, auto-format hooks, browser smoke testing, session resilience — takes time to set up from scratch. This repo packages all of that into a reusable bootstrap, aligned with the harness-engineering methodology.

**Core idea (from the article):** anything the agent can't access in-context doesn't exist for it. So you build the *harness* — a small, opinionated set of files and commands — that lets the agent reason about the full domain directly from the repository.

**What you get:**
- 18 slash commands for the full development lifecycle, including `/garbage-collect` and `/check-layers`
- **Golden Principles**: 12 mechanical, agent-actionable rules (`GP-001`..`GP-012`) every command consults
- **Layered architecture enforcement**: `docs/spec/LAYERS.md` + `/check-layers` block backward imports
- **Continuous garbage collection**: `/garbage-collect` scans for principle drift, opens targeted refactor PRs
- Planning system (features, bugs, decisions, dependencies, discovery)
- Eight spec files covering stack, architecture, conventions, API, golden principles, agent dispatch, layers, and smoke testing
- Cross-tool compatibility: emits both `CLAUDE.md` and `AGENTS.md` (Codex/Cursor/Copilot read the latter)
- Auto-format hooks (lint on save) + protected-file blocks
- Browser smoke testing via the [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- Multi-agent coordination with TDD step structure, dispatch specification, and session resilience (progress files survive context loss)
- Two-tier permissions: shared `settings.json` + machine-specific `settings.local.json`
- Optional deploy automation: `--with-deploy` adds `deploy.sh` / `deploy.ps1` + `Dockerfile` + entrypoint

---

## Mental model

Working with this bootstrap means thinking of yourself as the **harness operator**, not the implementer. Your job is to make sure the agent has the context, constraints, and feedback loops it needs to do useful work. The agent's job is to do the work.

Three things follow from this:

1. **The spec files are the contract, not decoration.** When you edit `docs/spec/GOLDEN_PRINCIPLES.md`, you're changing what every future agent will be measured against. When you edit `docs/spec/LAYERS.md`, you're changing what `/check-layers` blocks at merge time. Treat these files as source code — they get reviewed, versioned, and curated.

2. **You intervene at checkpoints, not in the middle.** The right places to steer are: approving the plan (after `/implement F-XXX` enters plan mode), reviewing the diff before commit, and editing spec files to encode rules you've found yourself enforcing manually. Don't hand-edit files mid-implementation — that breaks the agent's mental model and creates merge conflicts with its in-progress work.

3. **Drift is the enemy, not bugs.** Bugs get fixed in one PR. Drift — Golden Principle violations, inconsistent patterns, dead code, stale docs — compounds. The article calls it "compound interest." Run `/garbage-collect` weekly. Read the `GC_LOG.md`. When a violation count climbs, that rule deserves a sweep.

The rest of this README assumes that mental model. The walkthroughs in §4 show you how to apply it.

---

## Quick start

```bash
# 1. Clone into your project directory
git clone https://github.com/FTKuhnsman/vibe_bootstrap.git my-project
cd my-project
rm -rf .git  # Discard bootstrap git history

# 2. Run setup with a preset (or omit --preset for interactive mode)
python setup.py --preset django-react
# Add --with-deploy if you want Docker/Portainer-style deploy scripts

# 3. Initialize your own git history
git init && git add -A && git commit -m "Initial commit with vibe_bootstrap"

# 4. Open Claude Code in the project, then run, in order:
#    /spec               ← have the agent populate STACK/ARCHITECTURE/CONVENTIONS/API
#    Then hand-curate:
#      docs/spec/GOLDEN_PRINCIPLES.md   ← 12 default rules — keep, edit, or delete
#      docs/spec/LAYERS.md              ← layer model — match your repo structure
#      docs/spec/AGENT_DISPATCH.md      ← dispatch contract — usually fine as-is
#      docs/spec/SMOKE_TEST.md          ← stack-specific browser-test gotchas
#    Then start building:
#      /feature add        ← add F-001
#      /implement F-001    ← multi-agent implementation
```

Need detail? Read [§4.1 Initialize a new project](#41-initialize-a-new-project) below.

---

## End-to-end walkthroughs

The walkthroughs use a single running example: a habit-tracker web app called **Streaks**, built on Django + React. Each shows the *exact* prompts to type, the key decision points, and the common mistakes to avoid.

| Goal | Walkthrough |
|------|-------------|
| Set up a new project the right way | [§4.1](#41-initialize-a-new-project) |
| Build a non-trivial feature end-to-end | [§4.2](#42-implement-a-complex-feature) |
| Reproduce, fix, and verify a bug | [§4.3](#43-debug-a-bug) |
| Refactor without breaking things | [§4.4](#44-refactor) |
| Keep the codebase clean over time | [§4.5](#45-continuous-cleanup) |

---

### 4.1 Initialize a new project

**Goal:** stand up Streaks (a habit-tracker app) with a clean harness in under an hour. The work is mostly *configuration*, not coding — but it pays compound interest for every feature afterward.

#### Step 1 — Bootstrap

```bash
git clone https://github.com/FTKuhnsman/vibe_bootstrap.git streaks
cd streaks
rm -rf .git
python setup.py --preset django-react --with-deploy
git init && git add -A && git commit -m "chore: bootstrap from vibe_bootstrap"
```

The bootstrap writes 8 spec files, 18 slash commands, `.claude/settings.json`, `CLAUDE.md`, `AGENTS.md`, and (with `--with-deploy`) Docker scaffolding.

#### Step 2 — First Claude Code session: orient the agent

Open Claude Code in the `streaks/` directory and start with this prompt:

> Read `CLAUDE.md`, then `docs/spec/GOLDEN_PRINCIPLES.md`, then `docs/spec/AGENT_DISPATCH.md`. This is a greenfield project. I want to build "Streaks" — a habit-tracker where users define habits, mark them complete each day, and see a streak count. Backend is Django + DRF; frontend is React + Vite. Before we write any code, run `/spec` to capture the architecture decisions.

What the agent does:
- Reads CLAUDE.md (the map), then the rules and dispatch contract.
- Invokes `/spec` in greenfield mode — since there's no code yet, it asks you about intended stack, architecture, conventions, and API style.
- Writes the four discovery-driven specs: `STACK.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, `API.md`.

Plan on ~15 minutes of interactive Q&A. Answer with intent, not detail — the specs will evolve.

#### Step 3 — Curate `GOLDEN_PRINCIPLES.md`

The bootstrap ships 12 default rules. Open `docs/spec/GOLDEN_PRINCIPLES.md` and decide for each:
- **Keep as-is** — the rule is universally good (most fall here).
- **Customize** — adjust the auto-fix hint to mention your stack (e.g., GP-002 should mention Pydantic for the backend and Zod for the frontend).
- **Retire** — if you genuinely disagree, mark the rule `RETIRED` rather than deleting. (Keeping the ID prevents future rules from accidentally reusing the number.)

A common addition for Django + React projects:

```markdown
## GP-013 — DRF serializers are the only API boundary

**Rule:** Every API view delegates request validation and response shaping to a DRF serializer. Views never read `request.data` directly.

**Why:** Centralizes validation (instance of GP-002) and makes the API surface enumerable.

**How to apply:** Add a serializer per endpoint. Views call `serializer.is_valid(raise_exception=True)` and return `serializer.data`.

**Auto-fix hint:** Extract the request-body access into a serializer. Replace direct `request.data` reads with `serializer.validated_data`.
```

Commit the curated file: `git commit -am "docs(spec): curate Golden Principles for Streaks"`.

#### Step 4 — Define `LAYERS.md`

The default `docs/spec/LAYERS.md` ships with a 6-layer model (types → config → repo → service → runtime → ui). Open it, replace the example module-mapping table with Streaks-specific patterns, and commit:

```markdown
| Pattern | Layer |
|---------|-------|
| `backend/habits/types.py`, `backend/users/types.py` | `types` |
| `backend/streaks/settings/**` | `config` |
| `backend/*/models.py`, `backend/*/queries.py` | `repo` |
| `backend/*/services/**` | `service` |
| `backend/*/views.py`, `backend/*/urls.py`, `backend/*/serializers.py` | `runtime` |
| `frontend/src/**` | `ui` |
```

Run `/check-layers` to confirm the empty project parses cleanly:

> Run `/check-layers` and tell me if the layer model parses correctly. There's no source code yet, so I expect zero violations and zero warnings.

#### Step 5 — Add the first features

```
/feature add
```

Answer the prompts to add `F-001`. Repeat for `F-002`, `F-003`. Example:

```
F-001: Email/password authentication
  Priority: P0
  Effort: M
  Description: Email/password signup, login, logout. Session via JWT
              with refresh tokens. Unauthenticated users redirect to /login.
  Acceptance: Users can sign up. Users can log in. Users can log out.
              Refresh token works. /api/me returns the current user.

F-002: Habit CRUD
  Priority: P0
  Effort: M
  Description: Authenticated users can create, edit, delete habits with
              a name and a target frequency (daily / weekly / N-times-per-week).
  Acceptance: All four endpoints work and are auth-gated.

F-003: Streak tracking
  Priority: P1
  Effort: L
  Description: When a user marks a habit complete on a given date,
              their streak count increments. Missing a day resets it
              (unless freeze quota applies — see F-005).
  Acceptance: Marking completes increments streaks. Missing resets.
              Timezone handled per user.
```

#### Step 6 — Implement F-001

```
/implement F-001
```

What the agent does:
- Reads all the spec files (GP, AGENT_DISPATCH, LAYERS, ARCHITECTURE, CONVENTIONS, API, plus FEATURES.md and DECISIONS.md).
- Enters plan mode.
- Presents a 5-step plan with explicit agent dispatches per step.

**Your decision point:** review the plan before approving. Look for:
- Each step has a RED (test-writing) sub-step before the GREEN (implementation) sub-step.
- File ownership doesn't overlap between concurrent agents.
- GP-IDs are cited where they apply (e.g., "GP-002: schema-validate the signup payload via a DRF serializer").
- The plan ends with a smoke-test step.

If anything is off, say so:

> Step 3 — split the user model and JWT settings into two agents running in parallel. The user model is in `users/models.py`, the JWT config goes in `streaks/settings/jwt.py`. They don't share files.

The agent revises the plan. When you say "approved," it executes.

**Key takeaways from §4.1:**
- Curating the spec files at setup time is the highest-leverage thing you'll do.
- Don't skip `/spec` — empty spec files mean the agent has to guess, badly.
- Edit `LAYERS.md` *before* any source code lands. Once layers are wrong, fixing them is a refactor.

**Common pitfalls:**
- Running `/implement` before populating the specs. The agent will work, but each decision becomes a one-off rather than a pattern.
- Treating `GOLDEN_PRINCIPLES.md` as boilerplate. Every rule you don't curate is a rule you'll spend reviews arguing about.
- Skipping the `git commit` after each spec change. Spec edits are part of the project's history — version them.

---

### 4.2 Implement a complex feature

**Goal:** ship F-005, "streak freezing with a weekly auto-freeze quota." The feature touches three modules, requires a migration, and changes the API contract. This is the case the multi-agent workflow is designed for.

#### Step 1 — Add the feature

```
/feature add
```

```
F-005: Streak freezing with weekly auto-freeze quota
  Priority: P1
  Effort: L
  Description: Each user gets N free "freezes" per week (configurable
              per habit). A freeze prevents a missed day from resetting
              the streak. Quota refills every Monday at 00:00 user time.
  Acceptance:
    - User can manually freeze a habit for a specific date.
    - Auto-freeze kicks in for the most-recent-streak habit when quota allows.
    - Freezes are visible in the habit detail view.
    - Quota refills at the user's local Monday 00:00.
    - Quota can be configured per-habit via PATCH /api/habits/<id>/.
```

#### Step 2 — Run discovery

For anything non-trivial, run discovery before implementing. Discovery produces a doc that becomes the agent's primary context during `/implement`.

```
/feature discovery F-005
```

The agent enters plan mode and walks you through ~12 sections: Problem & Users, User Stories, Requirements (functional + non-functional), Architecture Fit, UI/UX, Real-Time considerations, Dependencies, Impact Analysis, Technical Approach (with alternatives), Acceptance Criteria, Effort Estimate, Open Questions.

Sample exchange:

> **Agent:** For the auto-freeze logic — should it apply only to habits with streaks above a certain length, or to any active streak? The article suggests "most-recent-streak habit" but that could mean either.
>
> **You:** Any active streak (count ≥ 1). But never apply auto-freeze on the same day a manual freeze was used for the same habit.
>
> **Agent:** Captured. That's worth a new architecture decision (D-007: auto-freeze precedence rule). I'll record it.

When discovery ends, the agent writes:
- `docs/plan/discovery/F-005-streak-freezing.md` — the full discovery doc.
- `docs/plan/DECISIONS.md` — new D-XXX entries for any architecture choices made.
- `docs/plan/FEATURES.md` — updates to F-005 if acceptance criteria firmed up.

Commit:

```
/commit-push-pr
# or manually:
git add docs/plan/
git commit -m "docs: F-005 discovery and decisions"
```

#### Step 3 — Implement

```
/implement F-005
```

What the agent reads (in order):
1. `docs/spec/GOLDEN_PRINCIPLES.md`
2. `docs/spec/AGENT_DISPATCH.md`
3. `docs/spec/LAYERS.md`
4. `docs/plan/discovery/F-005-streak-freezing.md` ← the heaviest context
5. `docs/plan/DECISIONS.md` (esp. D-007)
6. `docs/plan/FEATURES.md` (F-005 + dependencies)
7. `docs/spec/ARCHITECTURE.md`, `CONVENTIONS.md`, `API.md`
8. Affected source code

The agent enters plan mode and presents a structured plan. A realistic one for F-005:

```
Step 0  Setup: branch feature/F-005-streak-freezing, PROGRESS file, ACTIVE.md update
Step 1  RED  — failing tests for Freeze model + FreezeQuota model
Step 2  GREEN — Freeze + FreezeQuota models + migration (1 backend agent)
Step 3  RED  — failing tests for auto-freeze service (priority rules, quota logic)
Step 4  GREEN — auto-freeze service in backend/habits/services/freeze.py (1 backend agent)
Step 5  RED  — failing tests for POST /api/habits/<id>/freeze/ and PATCH quota
Step 6  GREEN — API endpoints (1 backend agent: views + serializers)
Step 7  RED  — failing tests for FreezeBadge + QuotaIndicator React components
Step 8  GREEN — UI components + integration into habit detail page (1 frontend agent,
               parallel with Step 9 if Step 6 is merged)
Step 9  Background — Celery beat task for Monday 00:00 quota refill (1 backend agent)
Step 10 Smoke test — full freeze-and-display flow in browser
Step 11 Finalize — full verification, docs cleanup, final commit
```

**Your decision points:**

(a) **Approve or revise the plan.** Common asks:
> Split Step 2 — the migration should land as a separate commit so we can roll it back independently from the model changes.

> Step 9 can run in parallel with Step 6 since they don't share files. Make them one batch.

(b) **Watch the parallel batches.** When a batch starts, the agent prints the dispatch contract for each sub-agent (the five fields from `AGENT_DISPATCH.md`). Verify the scope guards are tight — "do not modify any view code" is a good scope guard for a service-layer agent.

(c) **Pause if a verify gate fails.** When the test suite breaks after a batch, the agent will try to fix it. If it tries more than once without progress, intervene:
> Stop. Show me the failing test output. Don't dispatch any more fix agents until I've looked at it.

(d) **Review the smoke test in Step 10.** Open the browser when the agent navigates, watch the form interaction, check the console messages it lists. Console errors during the smoke test are a real signal — don't accept "minor warning" hand-waving.

#### Step 4 — After the implementation runs

When `/implement` finishes, the agent reports:
- All tests passing.
- `/check-layers --diff` clean.
- Smoke test completed with zero console errors.
- Commits made (one per logical step).
- Documentation updated (FEATURES.md, ACTIVE.md, DECISIONS.md, PROGRESS file).

Spot-check:

```
git log --oneline feature/F-005-streak-freezing ^main
```

You should see ~11 commits matching the plan. Then:

```
/review
```

The `/review` command does its own pass: GP compliance, security, performance, a11y, error handling, test coverage. If it finds anything, fix and re-run.

Finally:

```
/commit-push-pr
```

#### Step 5 — Session resilience

If your Claude Code session dies mid-implementation:

```
/implement --resume
```

The agent finds the most recent `docs/plan/PROGRESS_F-*.md` with unchecked boxes, picks up at the first unchecked sub-step, and continues. All previously committed work is safe.

**Key takeaways from §4.2:**
- Discovery is the highest-leverage 30 minutes you'll spend on a complex feature.
- The dispatch plan is the contract — review it carefully before approving.
- Parallel batches exist to save time, not to skip verification — every batch ends with a full test run + `/check-layers`.
- The smoke test is a real test. Watch it.

**Common pitfalls:**
- Skipping discovery for "medium" features. If you can't describe the data model and API in one paragraph, you need discovery.
- Approving a plan with overlapping file ownership. The agent will produce conflicting edits.
- Ignoring `/check-layers --diff` failures. GP-006 catches architectural drift early; debt compounds fast.

---

### 4.3 Debug a bug

**Goal:** fix B-007, "streak count off by one when a user crosses midnight in their local timezone." Demonstrates the reproduce → failing test → fix → verify loop, and shows how bugs often point at a Golden Principle the original code violated.

#### Step 1 — Log the bug

```
/bug log
```

```
B-007: Streak count off-by-one across midnight (timezone)
  Severity: high
  Reproduction: User in America/Los_Angeles marks habit "Read 30 min"
                complete at 23:55 local time. Their streak shows N. At
                00:05 the next day (still PT), they mark it again. Streak
                shows N+2 instead of N+1.
  Expected: Streak shows N+1 (one increment per calendar day in user's tz).
  Discovered: 2026-05-12 by user@streaks.app
```

#### Step 2 — Fix

```
/fix-bug B-007
```

What the agent does:

**Reproduce phase** — agent opens a Chrome page via the chrome-devtools MCP, sets the browser timezone, logs in as a test user, manipulates `localStorage` to simulate the late-night state, marks the habit complete, then advances the clock and marks it again. The console shows the off-by-one. Reproduction confirmed.

**Failing-test phase** — agent writes a Django test that simulates the same scenario at the model/service level (no browser needed for this layer). Test fails as expected.

**Diagnosis phase** — agent reports:

> I see two interacting issues, both of which violate Golden Principles:
>
> 1. **GP-002 violation in `backend/habits/services/streak.py:42`** — the streak service receives a `completed_at` datetime and calls `.date()` on it directly, without converting to the user's timezone. That's probing the shape of a datetime instead of validating at the boundary.
>
> 2. **GP-011 violation in `backend/habits/views.py:18`** — the view reads `request.user.timezone` via `request.user.profile.timezone or 'UTC'`, with the fallback inline. The fallback should live in the typed config / user model, not at the call site.
>
> Proposed fix:
> - In `streak.py`: convert `completed_at` to `user.timezone` *before* extracting the date. The streak service should require a `(datetime, timezone)` tuple, not a bare datetime.
> - In `users/models.py`: make `timezone` non-nullable with a default of `'UTC'` at the model layer. Drop the inline fallback in the view.
>
> Both changes are behavior-preserving for users already in UTC (the common case) but fix the off-by-one for non-UTC users.

**Your decision point:** approve, or scope down if needed. Sometimes you want the minimal fix and the GP cleanup as a separate PR:

> Just fix issue 1 in this PR. File issue 2 as B-008 and we'll address it in a follow-up.

The agent then implements only the approved scope.

**Fix + verify phase:**
- Agent applies the fix.
- Failing test now passes.
- Full test suite passes.
- Browser smoke test: reproduce the original scenario; verify the streak now shows N+1 correctly.
- Commit: `fix(B-007): convert completed_at to user timezone before date extraction (GP-002)`.

#### Step 3 — Close the bug

The agent updates `docs/plan/BUGS.md` to mark B-007 closed with the fix date and a one-line description.

If the diagnosis surfaced a GP violation pattern that exists elsewhere, the agent will note this in the closing message:

> Same probing pattern likely exists in `backend/habits/services/aggregate.py` and `backend/habits/services/leaderboard.py`. Suggest scoping a `/garbage-collect --principle GP-002` sweep over the `services/` directory.

That's a future-you favor. Either run the sweep now or capture it as a task:

```
/task add "GP-002 sweep over backend/habits/services/"
```

**Key takeaways from §4.3:**
- The reproduce step is real — the agent uses the browser to confirm the bug, not just intuition.
- Failing tests come *before* fixes. If the test passes immediately, the bug isn't reproduced.
- Most non-trivial bugs are GP violations in disguise. The fix is "follow the rule," not "patch the symptom."

**Common pitfalls:**
- Letting the agent skip the failing-test step "because it's obvious." If the test isn't there, the next regression will catch you.
- Accepting a fix that doesn't cite the underlying GP rule. If the pattern is wrong, the fix is incomplete.
- Trying to scope-creep the fix into a refactor in the same PR. Bug fix and refactor are separate commits, ideally separate PRs.

---

### 4.4 Refactor

**Goal:** extract a shared `HabitFormFields` React component to replace three near-duplicate implementations. The drift was caught by `/garbage-collect` (a GP-001 violation: "centralize invariants in shared utilities"). Demonstrates safe, TDD-driven refactoring.

#### Step 1 — Discover the drift

Either you noticed it, or `/garbage-collect` did:

```
/garbage-collect --principle GP-001 --report
```

The report lands in `docs/plan/GC_REPORT_2026-05-12.md`:

```markdown
## GP-001 — Centralize invariants in shared utilities

### High
- frontend/src/pages/HabitCreate.tsx:18 — `HabitFormFields` (inline) duplicates
  frontend/src/pages/HabitEdit.tsx:22 and frontend/src/components/HabitWizard.tsx:34
  (3 implementations, 80% identical, drift in field labels and validation messages)
```

#### Step 2 — Run refactor

```
/refactor Extract a shared HabitFormFields component from the three duplicate
         implementations in HabitCreate, HabitEdit, and HabitWizard. The
         duplicates were flagged by /garbage-collect on 2026-05-12 as a
         GP-001 violation.
```

What the agent reads:
- `docs/spec/GOLDEN_PRINCIPLES.md` (especially GP-001 and GP-007)
- `docs/spec/AGENT_DISPATCH.md`
- `docs/spec/LAYERS.md` (to confirm the new shared component sits in the right layer)
- `docs/spec/CONVENTIONS.md` (for the project's React patterns)
- The three duplicate files + their existing tests
- `docs/plan/GC_REPORT_2026-05-12.md` (the violation report)

The agent enters plan mode:

```
Step 1  RED  — write tests for the new HabitFormFields component
               (rendering, validation, prop-driven defaults)
Step 2  GREEN — implement HabitFormFields in frontend/src/components/
Step 3  Verify — run frontend tests, /check-layers --diff
Step 4  RED  — write tests that confirm HabitCreate behavior unchanged
               when using HabitFormFields
Step 5  GREEN — migrate HabitCreate to use HabitFormFields (parallel agent A)
Step 5b GREEN — migrate HabitEdit to use HabitFormFields (parallel agent B)
Step 6  Verify — full test suite, /check-layers --diff
Step 7  RED  — write tests that confirm HabitWizard step-3 behavior unchanged
Step 8  GREEN — migrate HabitWizard step-3 to use HabitFormFields
Step 9  Delete — remove the three old inline implementations (no re-exports
                 needed since they were inline)
Step 10 Smoke test — exercise all three pages in browser, zero console errors
Step 11 Finalize — commit, update GC log to note GP-001 sweep completed
```

**Your decision points:**

(a) **Approve or scope.** A common ask:
> Combine Steps 5/5b/8 into one batch. They don't share files, so parallel is fine.

(b) **Verify backward compatibility.** Tests in Steps 4 and 7 are the safety net — they confirm the migrated pages behave identically. If a test fails after the migration step, that's the refactor breaking something.

(c) **Watch the smoke test.** Walk through HabitCreate, HabitEdit, and the HabitWizard step 3 yourself. Pay attention to field labels and validation messages — if the duplicates drifted, the unified component picks one variant; make sure it's the right one.

#### Step 3 — After refactor

The final commits:

```
test(GP-001): add tests for HabitFormFields
refactor(GP-001): extract HabitFormFields component
test(GP-001): preserve behavior tests for HabitCreate, HabitEdit, HabitWizard
refactor(GP-001): migrate HabitCreate to HabitFormFields
refactor(GP-001): migrate HabitEdit to HabitFormFields
refactor(GP-001): migrate HabitWizard step-3 to HabitFormFields
refactor(GP-001): delete old inline form fields
```

Update `docs/plan/GC_LOG.md` (the agent does this automatically):

```
| 2026-05-12 | --report   | 14 across 5 GPs | 0 | |
| 2026-05-13 | --principle GP-001 manual | 1 / 1 fixed | 1 | F-005-shared-HabitFormFields |
```

**Key takeaways from §4.4:**
- Refactors are TDD-driven for the same reason features are: tests are the safety net that lets you move fast.
- Each step leaves the codebase in a working state. The agent never makes you choose between "stop midway" and "wait an hour to verify."
- Commit messages cite the GP rule that motivated the refactor. Six months later, the link from `git log` back to `GOLDEN_PRINCIPLES.md` is what makes the cleanup legible.

**Common pitfalls:**
- "Just do the whole refactor in one commit." That defeats the safety net. If you need to revert one piece, you'll be picking apart files.
- Migrating without behavior-preservation tests (Steps 4 and 7). The migrated component compiles but renders differently — you find out in production.
- Skipping the smoke test because "it's just CSS." Forms are full of subtle controlled-input bugs.

---

### 4.5 Continuous cleanup

**Goal:** make Golden Principle drift a background process, not a periodic crisis. This is the "garbage collection" pattern from the harness-engineering article, adapted with `/loop`.

#### Daily report (low effort)

Run a recurring sweep that produces a report you can review with morning coffee:

```
/loop 1d /garbage-collect --report
```

Each run writes `docs/plan/GC_REPORT_<date>.md` and appends a row to `docs/plan/GC_LOG.md`. Skim the report each morning. When one rule's violation count climbs, schedule a sweep:

```
/garbage-collect --principle GP-008 --fix
```

That opens a focused branch (`gc/2026-05-12/GP-008`) with one commit per fixable violation. Review the diff, run tests, merge.

#### Weekly proactive sweep

A pattern that works well: every Monday morning, run a broader sweep:

```
/garbage-collect --since main~7
```

This scopes the scan to files changed in the last week — fast, focused, catches drift introduced by the team's own work before it becomes habit.

#### CI integration

For projects where drift is a real risk, wire `/check-layers` into CI:

```yaml
# .github/workflows/check-layers.yml (or equivalent)
name: Check architecture layers
on: [pull_request]
jobs:
  check-layers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run check-layers
        run: |
          # invoke Claude Code in headless mode or use a wrapper script that
          # implements the same /check-layers logic in plain Python.
          # Exit non-zero if violations.
```

`/check-layers` exits non-zero when GP-006 violations exist, so CI gating is a one-liner. Use the same pattern for `/garbage-collect --report` if you want CI to fail on critical drift.

**Key takeaways from §4.5:**
- The article calls this "compound interest." Small daily payments beat one quarterly debt sprint.
- Drift is most legible when caught at change time. The weekly `--since main~7` pattern is the sweet spot between noise and lag.
- CI integration turns GP-006 (one-way dependencies) and GP-NNN reports into merge gates — but only after the team has agreed they should be.

**Common pitfalls:**
- Running `--fix` against a codebase with a weak test suite. Behavior degrades silently. Run `--report` first; expand tests; then `--fix`.
- Mixing principles in one sweep branch. Reviews lose focus. Each `--fix` branch should target exactly one GP-NNN.
- Treating low-severity violations as alerts. The log tracks low-severity counts for trend analysis, not for nagging.

---

## Daily operating practices

A few patterns and anti-patterns that come up regardless of which walkthrough you're in.

### Do this

- **Commit spec edits separately.** A commit that changes `GOLDEN_PRINCIPLES.md` should not also include feature code. The spec is the contract; the contract change deserves its own line in the history.
- **Reference GP-IDs in commit messages.** `fix(B-007): convert datetime to user tz (GP-002)` is grep-able six months later.
- **Read the PROGRESS file when you're confused.** If you come back to a half-finished feature and don't know where you are, `docs/plan/PROGRESS_F-XXX.md` is the source of truth.
- **Approve plans before the agent executes.** Plan mode is a checkpoint, not a formality. Bad plans become bad PRs.
- **Run `/check-layers --diff` before every PR.** It's three seconds; it catches GP-006 violations before review.

### Don't do this

- **Don't hand-edit files mid-implementation.** The agent has an in-progress mental model of what each agent owns; your edits create conflicts.
- **Don't approve a plan without reading the dispatch contracts.** Especially the scope guards — "do not modify view code" is the load-bearing constraint that keeps agents from stomping on each other.
- **Don't run `/garbage-collect --fix` against a codebase with low test coverage.** It will degrade behavior silently. Use `--report` and expand tests first.
- **Don't let `BUGS.md` and `ACTIVE.md` go stale.** When the agent reads them as context and they're wrong, every downstream decision starts from a bad premise.
- **Don't conflate `/spec` with the four hand-edited files.** `/spec` rewrites `STACK/ARCHITECTURE/CONVENTIONS/API`. It does **not** touch `GOLDEN_PRINCIPLES/AGENT_DISPATCH/LAYERS/SMOKE_TEST` — those are yours.

---

## Commands reference

### Implementation workflow

| Command | Description |
|---------|-------------|
| `/implement F-XXX` | Full feature implementation: plan → TDD → parallel agents → verify → smoke test |
| `/fix-bug B-XXX` | Bug fix: reproduce → failing test → fix → verify |
| `/refactor [desc]` | Safe refactoring with TDD and parallel agents |
| `/next-phase` | Execute the next development phase automatically |

### Quality & testing

| Command | Description |
|---------|-------------|
| `/review` | Pre-PR code review (GP compliance, security, performance, a11y, correctness) |
| `/test [component]` | Generate comprehensive tests (happy path, errors, edge cases) |
| `/verify-ui [flow]` | Browser smoke test via chrome-devtools MCP |
| `/clean-up` | Code quality review of current diff; applies GP auto-fix hints |
| `/garbage-collect` | Scan for Golden Principle drift; report or open targeted refactor PRs |
| `/check-layers` | Enforce GP-006 — verify dependency direction matches `docs/spec/LAYERS.md` |

### Project management

| Command | Description |
|---------|-------------|
| `/feature [cmd]` | Manage feature backlog (add, list, view, update, discovery) |
| `/bug [cmd]` | Manage bugs (log, fix, close, list) |
| `/task [cmd]` | Manage tasks (add, start, done, block, unblock, next) |
| `/status` | Quick project dashboard |
| `/plan [filter]` | View detailed project status |

### Utilities

| Command | Description |
|---------|-------------|
| `/spec [file]` | Generate/update the discovery-driven spec files (stack, architecture, conventions, API) |
| `/commit-push-pr` | Stage, commit, push, create PR — all automated |
| `/security-audit` | Targeted security review of recent changes |

---

## Spec system

Spec files give the agent deep context. They live in `docs/spec/`:

| File | What it defines | Managed by |
|------|-----------------|------------|
| `STACK.md` | Languages, frameworks, versions, package managers, dev tools | `/spec stack` |
| `ARCHITECTURE.md` | System design, data flow, directory structure, auth, state management | `/spec architecture` |
| `CONVENTIONS.md` | Naming, error handling, validation, testing patterns, code organization | `/spec conventions` |
| `API.md` | Endpoint patterns, auth scheme, request/response formats, errors | `/spec api` |
| `GOLDEN_PRINCIPLES.md` | Mechanical rules (`GP-001`..`GP-012`) every command consults | hand-edited |
| `AGENT_DISPATCH.md` | Five-field dispatch contract; TDD step structure | hand-edited |
| `LAYERS.md` | Canonical dependency direction; enforced by `/check-layers` | hand-edited |
| `SMOKE_TEST.md` | Browser-test playbook for `/verify-ui` | hand-edited |

Run `/spec` after setup to populate the four discovery-driven files. The other four ship pre-populated with sensible defaults — curate them by hand as your project evolves.

---

## Harness engineering alignment

This bootstrap is organized around the principles from OpenAI's [harness engineering](https://openai.com/index/harness-engineering/) post. The vocabulary maps as follows:

| Harness-engineering concept | In `vibe_bootstrap` |
|------------------------------|---------------------|
| Lean `AGENTS.md` as map | `CLAUDE.md` + `AGENTS.md` (identical content, ~120 lines) |
| System-of-record docs/ directory | `docs/spec/` + `docs/plan/` |
| Golden principles | `docs/spec/GOLDEN_PRINCIPLES.md` (`GP-001`..) |
| Layered dependency model | `docs/spec/LAYERS.md` + `/check-layers` |
| Garbage collection (continuous cleanup) | `/garbage-collect` (run on a `/loop` cadence) |
| Executable plans | `docs/plan/PROGRESS_F-XXX.md` |
| Design docs | `docs/plan/discovery/F-XXX-*.md` |
| Product specs | `docs/plan/FEATURES.md` |
| Reference docs | `docs/spec/*.md` |
| Application legibility | `/verify-ui` + `docs/spec/SMOKE_TEST.md` (chrome-devtools MCP) |
| Agent-to-agent review | `/review` + `/clean-up` (with GP auto-fix hints) |
| Architectural enforcement | `/check-layers` + GP-006 |
| Constraints over corrections | Five-field agent dispatch in `docs/spec/AGENT_DISPATCH.md` |

---

## Presets

| Preset | Stack | Backend | Frontend |
|--------|-------|---------|----------|
| `django-react` | Django + React/Vite | pytest, ruff | vitest, eslint, prettier |
| `nextjs` | Next.js fullstack | — | jest/vitest, eslint |
| `fastapi-react` | FastAPI + React/Vite | pytest, ruff | vitest, eslint, prettier |
| `express-react` | Express + React/Vite | jest, eslint | vitest, eslint, prettier |
| `rails-react` | Rails + React/Vite | rspec, rubocop | vitest, eslint, prettier |
| `flask-vue` | Flask + Vue/Vite | pytest, ruff | vitest, eslint, prettier |
| `laravel-vue` | Laravel + Vue/Vite | phpunit, pint | vitest, eslint, prettier |
| `go-htmx` | Go + HTMX | go test, golangci-lint | — |
| `python-only` | Python (no frontend) | pytest, ruff | — |
| `node-only` | Node.js/TypeScript | — | vitest, eslint |

---

## Customization

### Preset + overrides

```bash
python setup.py --preset django-react
# Then edit CLAUDE.md, vibe.config.json, or .claude/settings.json as needed
```

### Custom configuration

```bash
cp vibe.config.example.json vibe.config.json
# Edit vibe.config.json with your stack details
python setup.py --config vibe.config.json
```

### Partial installation

```bash
python setup.py --commands-only   # Just slash commands
python setup.py --docs-only       # Just planning docs
python setup.py --specs-only      # Just spec templates
```

### Opt-in deploy automation

```bash
python setup.py --preset django-react --with-deploy
```

Adds `deploy.sh` + `deploy.ps1` (semver-bump from latest git tag, build + push Docker image, trigger a redeploy webhook), a multi-stage `Dockerfile`, and `docker-entrypoint.sh`. Assumes a Portainer-style webhook deploy model (`PORTAINER_WEBHOOK_URL` / `PORTAINER_DEV_WEBHOOK_URL` in `.env`).

### Two-tier permissions

The generated `.claude/settings.json` is the team-shared, version-controlled permission set. Claude Code also merges `.claude/settings.local.json` if present — that file is gitignored by default. Use it for machine-specific or experimental permission grants without polluting the shared config.

### Browser automation requirement

`/verify-ui`, `/implement`, `/fix-bug`, and `/refactor` reference the [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp). Install and configure it in your Claude Code settings — the commands assume tools named `mcp__chrome-devtools__*` are available. If you skip it, the other commands still work; just do browser testing manually.

### Adding custom commands

Add `.md` files to `.claude/commands/` with YAML frontmatter:

```markdown
---
description: What this command does
allowed-tools:
  - Read
  - Write
  - Bash
---

# Command Name

## Process
1. Step one
2. Step two
```

### Adding a custom Golden Principle

Edit `docs/spec/GOLDEN_PRINCIPLES.md`. Format:

```markdown
## GP-013 — <one-line statement>

**Rule:** <imperative>

**Why:** <past pain or structural reason>

**How to apply:** <when and what>

**Auto-fix hint:** <agent-safe remediation>
```

Bump the highest existing GP number by one. Update the "Commands that consult this file" table if a new command checks the rule.

---

## Project structure (after setup)

```
your-project/
├── .claude/
│   ├── commands/                # 18 slash commands
│   ├── settings.json            # Permissions + auto-format hooks (committed)
│   ├── settings.local.json      # (gitignored) machine-specific perms
│   └── launch.json              # Dev server configs
├── .gitignore                   # Generated; preserves any existing one
├── CLAUDE.md                    # Navigation map for agents (slim, ~120 lines)
├── AGENTS.md                    # Mirror of CLAUDE.md for Codex/Cursor/Copilot
├── docs/
│   ├── plan/
│   │   ├── FEATURES.md          # Feature backlog
│   │   ├── ACTIVE.md            # Sprint tracker
│   │   ├── BUGS.md              # Bug tracker
│   │   ├── DECISIONS.md         # Architecture decisions
│   │   ├── DEPENDENCIES.md      # Impact analysis
│   │   ├── discovery/           # Feature discovery docs
│   │   ├── PROGRESS_F-*.md      # Executable plans (session-resilient)
│   │   ├── GC_LOG.md            # Garbage-collect sweep history
│   │   └── GC_REPORT_*.md       # Per-run garbage-collect reports
│   └── spec/
│       ├── STACK.md             # Technical stack
│       ├── ARCHITECTURE.md      # System design
│       ├── CONVENTIONS.md       # Code patterns
│       ├── API.md               # API contracts
│       ├── GOLDEN_PRINCIPLES.md # GP-001..GP-012 — mechanical rules
│       ├── AGENT_DISPATCH.md    # Five-field dispatch contract
│       ├── LAYERS.md            # Canonical dependency direction
│       └── SMOKE_TEST.md        # Browser-test playbook
├── vibe.config.json             # Bootstrap config (for re-runs)
└── (with --with-deploy:)
    ├── deploy.sh                # bash: bump semver, build, push, redeploy
    ├── deploy.ps1               # PowerShell equivalent
    ├── Dockerfile               # Multi-stage; customize for your stack
    └── docker-entrypoint.sh
```

---

## FAQ

**Q: Can I use this with an existing project?**
Yes. Run `python setup.py --target /path/to/existing/project`. It won't overwrite existing files without `--force`. Then run `/spec --update` to generate specs from your codebase. Curate `GOLDEN_PRINCIPLES.md` and `LAYERS.md` carefully — an existing codebase will violate some of the defaults, and you need to decide rule-by-rule whether to enforce or retire.

**Q: What if my stack isn't in the presets?**
Use `python setup.py` (interactive mode) and select "Custom" to configure manually, or copy the closest preset and edit `vibe.config.json`.

**Q: Do I need the chrome-devtools MCP for `/verify-ui`?**
Yes — `/verify-ui` (and the smoke-test phase of `/implement`, `/fix-bug`, `/refactor`) call tools named `mcp__chrome-devtools__*`. Install the [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) in your Claude Code settings. Skipping the MCP leaves the other 15 commands fully functional — just do browser testing manually.

**Q: How do I update the bootstrap in an existing project?**
Re-run `python setup.py` with your existing `vibe.config.json`. It will regenerate config files and offer to update commands. Spec files you've curated (especially `GOLDEN_PRINCIPLES.md` and `LAYERS.md`) won't be overwritten without `--force`.

**Q: What's the difference between `CLAUDE.md` and `AGENTS.md`?**
Currently, none. Both files are written identically by `setup.py`. `CLAUDE.md` is Claude Code's native convention; `AGENTS.md` is the cross-tool standard (Codex, Cursor, Copilot). Keeping both means you can use this bootstrap regardless of which tool the team adopts. Edit either — but keep them in sync.

**Q: Should I commit the `GC_REPORT_*.md` files?**
Optional. They're useful for trend analysis (drift count over time) but bulky. A reasonable middle ground: commit `GC_LOG.md` (the one-line-per-run summary), gitignore the per-run reports.

**Q: How do I add a new Golden Principle?**
Edit `docs/spec/GOLDEN_PRINCIPLES.md`. Bump to the next `GP-NNN` number — they're append-only, never recycled. Add the four required sections (Rule, Why, How to apply, Auto-fix hint). Commit it with a `docs(spec):` prefix.

**Q: When should I retire a Golden Principle?**
When the team has agreed it's not pulling its weight (more arguments than catches) or when a better rule supersedes it. Don't delete — mark `RETIRED` in the heading and add a one-line note explaining why. Preserving the ID prevents future rules from accidentally reusing it.

**Q: Does `/check-layers` actually parse imports?**
Yes. It reads `docs/spec/LAYERS.md`, builds a file → layer index using your module-mapping patterns, then greps imports per file. Backward imports (lower-layer file importing from a higher layer) are flagged as GP-006 violations. The command supports `--diff`, `--since <ref>`, `--layer <name>`, and `--explain GP-006`.

**Q: Can I run `/garbage-collect` and `/check-layers` outside Claude Code?**
Not directly — they're slash commands that orchestrate Claude. But the logic is documented in `commands/garbage-collect.md` and `commands/check-layers.md`, so a plain Python equivalent for CI is straightforward to write.

---

## License

MIT
