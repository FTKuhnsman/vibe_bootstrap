# Feature Backlog

Features organized by phase. Use `/feature add` to add new features, `/feature stub` to create placeholders, `/feature list` to browse.

## Feature Lifecycle

```
stub → backlog → in-progress → done
                 ↕
               blocked
```

- **`stub`** — Placeholder. Cannot be implemented until `/feature discovery` runs and promotes it to `backlog`.
- **`backlog`** — Fully specified and ready to build. `/implement` is allowed.
- **`in-progress`** — Currently being built.
- **`blocked`** — Waiting on an external dependency.
- **`done`** — Shipped and verified. Cannot be re-implemented.

Features without a `status:` field are treated as `backlog` (backward compatibility). The lifecycle gate is enforced by `can_implement()` in `lib/validate.py`.

---

## Phase 1

<!-- Add features using the template at the bottom of this file, or use /feature add -->

---

## Backlog (Unphased)

<!-- Features not yet assigned to a phase -->

---

## Feature Template

Use this format when adding features manually (or use `/feature add`):

```
### F-XXX: [Feature Name]
- **Priority:** P0/P1/P2/P3
- **Status:** `stub` | `backlog` | `in-progress` | `blocked` | `done`
- **Estimated Effort:** S/M/L/XL
- **Phase:** [number]
- **Description:** [what and why]
- **Acceptance Criteria:**
  - [ ] Criterion 1
  - [ ] Criterion 2
- **Dependencies:** None
- **Notes:** [optional]
```

### Priority Reference
- **P0:** Critical path — blocks other features
- **P1:** High value — should ship in v1
- **P2:** Nice-to-have — post-MVP
- **P3:** Low priority — deferred

### Effort Reference
- **S:** 1–2 days | **M:** 3–5 days | **L:** 1–2 weeks | **XL:** 2+ weeks
