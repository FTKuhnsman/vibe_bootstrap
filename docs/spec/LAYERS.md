# Layered Architecture

This file defines the canonical dependency order for the project. `GP-006` ("Dependencies flow in one direction") and `/check-layers` both read from this file.

## The layer model

List your layers from lowest (foundational) to highest (consumer). Each layer may depend on layers below it; backward imports are forbidden.

<!-- Edit this list to match your project. The default below is a reasonable starting point
for a typical web stack — delete or rename layers as needed. -->

1. **types** — Pure type definitions, enums, and constants. No runtime logic. No imports from anywhere else in the project.
2. **config** — Configuration loading and validation (see GP-011). May import from `types`.
3. **repo** — Data access: database queries, external API clients, filesystem reads. May import from `types`, `config`.
4. **service** — Business logic. Orchestrates `repo` calls. May import from `types`, `config`, `repo`. Must not import from `runtime` or `ui`.
5. **runtime** — Framework glue: route handlers, controllers, view functions, background tasks. May import from any lower layer. Must not import from `ui`.
6. **ui** — Templates, components, frontend code. May import from any lower layer.

## Module → layer mapping

Map directory or file patterns to the layer they belong to. `/check-layers` uses this to detect violations.

<!-- Example mappings — edit to match your repo's structure: -->

| Pattern | Layer |
|---------|-------|
| `backend/types/**`, `backend/*/types.py`, `frontend/src/types/**` | `types` |
| `backend/config/**`, `backend/settings/**`, `frontend/src/config/**` | `config` |
| `backend/*/models.py`, `backend/*/queries.py`, `backend/*/clients/**`, `frontend/src/api/**` | `repo` |
| `backend/*/services/**`, `backend/*/logic/**` | `service` |
| `backend/*/views.py`, `backend/*/urls.py`, `backend/*/tasks.py` | `runtime` |
| `backend/*/templates/**`, `frontend/src/**` (everything else) | `ui` |

## Allowed exceptions

If a backward import is genuinely necessary, document it here with a reason. `/check-layers` will skip violations matching an entry in this section.

<!-- Format:
- `<file path>` imports from `<higher layer>` because `<one-sentence reason>` — accepted YYYY-MM-DD by <owner>
-->

_(none yet)_

## Anti-patterns

- **`ui` importing from `runtime`** — almost always means a controller responsibility leaked into the view. Move the logic to a service.
- **`repo` importing from `service`** — usually means business logic ended up in a query class. Push it back up.
- **`types` importing from anywhere** — types should be data-only. If you need a runtime dependency, it doesn't belong in `types`.

## Opting out

If your project doesn't have a useful layer model (early prototype, single-file utility), delete the layer list and module map and replace this file's body with:

```markdown
This project does not enforce a layered architecture. `/check-layers` is a no-op.
```

`/check-layers` will detect the opt-out and exit cleanly without scanning.
