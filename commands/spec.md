---
description: Interactive spec discovery and generation. Scan codebase, infer patterns, populate spec files.
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
  - Agent
---

# Spec

Interactive discovery and generation of project specification files in `docs/spec/`.

## Usage

```
/spec                    # Full discovery (all 4 files)
/spec stack              # Just STACK.md
/spec architecture       # Just ARCHITECTURE.md
/spec conventions        # Just CONVENTIONS.md
/spec api                # Just API.md
/spec --update           # Re-scan codebase and update existing specs
```

## Spec Files

| File | Purpose |
|------|---------|
| `docs/spec/STACK.md` | Languages, frameworks, versions, package managers, dev tools |
| `docs/spec/ARCHITECTURE.md` | System design, data flow, directory structure, auth, state management |
| `docs/spec/CONVENTIONS.md` | Naming, error handling, validation, testing patterns, code organization |
| `docs/spec/API.md` | Endpoint patterns, auth scheme, request/response formats, errors |

## Process

### 1. Scan Codebase

Read existing files to infer the stack and patterns:
- **Package files:** `package.json`, `requirements.txt`, `Pipfile`, `pyproject.toml`, `go.mod`, `Gemfile`, `Cargo.toml`, `composer.json`
- **Config files:** `tsconfig.json`, `.eslintrc*`, `.prettierrc*`, `ruff.toml`, `pyproject.toml`
- **Framework configs:** `vite.config.*`, `next.config.*`, `webpack.config.*`, `settings.py`, `manage.py`
- **Directory structure:** `ls` top-level and key subdirectories
- **Sample code:** Read 2-3 representative source files per layer to identify patterns
- **Existing specs:** Read any existing `docs/spec/*.md` files

### 2. Infer Patterns

From the scan, determine:
- **Stack:** Languages, framework versions, package manager
- **Architecture:** Monorepo vs single-app, backend/frontend split, API style (REST/GraphQL/RPC)
- **Conventions:** Naming patterns, import organization, error handling approach, test structure
- **API:** Endpoint naming, auth mechanism, response format, error handling

### 3. Ask User to Confirm and Fill Gaps

Present inferences and ask for confirmation. For gaps that can't be inferred from code:
- Deployment targets (cloud provider, containerization)
- Auth strategy (JWT, session, OAuth, API keys)
- Performance requirements (SLAs, caching strategy)
- Naming preferences not yet established in code
- Any patterns they want to enforce going forward

### 4. Write Spec Files

Generate rich, structured content for each requested spec file:
- Fill every section with concrete, project-specific detail
- Include code examples from the actual codebase where helpful
- Cross-reference between spec files (e.g., CONVENTIONS.md references ARCHITECTURE.md patterns)
- Replace template guidance comments with actual content

### 5. Update CLAUDE.md

If CLAUDE.md exists, verify it references the spec files. If Architecture or Conventions sections exist as placeholders, note that the detailed specs are in `docs/spec/`.

## For Greenfield Projects

When the codebase is empty or minimal:
1. Skip the scan phase
2. Ask the user about their intended stack, architecture, and conventions
3. Use the selected preset (from `vibe.config.json`) as a starting point
4. Generate spec files based on best practices for the chosen stack
5. These specs then guide the initial implementation via `/implement`

## For Existing Projects

When using `--update`:
1. Read existing spec files to understand what was previously documented
2. Re-scan the codebase for changes since specs were last written
3. Highlight discrepancies between specs and current code
4. Ask the user whether discrepancies are intentional (code changed) or accidental (code drifted)
5. Update specs to match current reality (with user confirmation)

## Per-File Discovery

### /spec stack
Scan package files and configs. Ask about deployment targets and external services.

### /spec architecture
Read directory structure, entry points, config files. Ask about data flow, auth strategy, state management. Read model definitions and component trees.

### /spec conventions
Read 3-5 source files per layer, identify naming patterns, error handling, test structure. Ask about preferences not yet established in code.

### /spec api
Read route definitions, serializers/controllers, middleware. Infer endpoint patterns, auth scheme, response format. Document existing endpoints in inventory table.
