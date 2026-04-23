# vibe_bootstrap

Reusable development workflow for [Claude Code](https://claude.ai/claude-code). Clone this repo, run `setup.py`, and get a full multi-agent coordinated workflow for any tech stack.

## Why

Building software with Claude Code is powerful, but the workflow — slash commands, planning docs, spec files, auto-format hooks, browser smoke testing, session resilience — takes time to set up from scratch. This repo packages all of that into a reusable bootstrap.

**What you get:**
- 16 slash commands for the full development lifecycle
- Planning system (features, bugs, decisions, dependencies, discovery)
- Spec files for deep project context (stack, architecture, conventions, API)
- Auto-format hooks (lint on save) + protected-file blocks
- Browser smoke testing via the [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- Multi-agent coordination with TDD step structure, dispatch specification, and session resilience (progress files survive context loss)
- Two-tier permissions: shared `settings.json` + machine-specific `settings.local.json`
- Optional deploy automation: `--with-deploy` adds `deploy.sh` / `deploy.ps1` (semver-bump + Docker build/push + redeploy webhook), `Dockerfile`, and `docker-entrypoint.sh`

## Quick Start

```bash
# 1. Clone into your project
git clone https://github.com/FTKuhnsman/vibe_bootstrap.git my-project
cd my-project
rm -rf .git  # Remove bootstrap git history

# 2. Run setup with a preset (add --with-deploy if you want Docker/Portainer-style deploy scripts)
python setup.py --preset django-react
# python setup.py --preset django-react --with-deploy

# 3. Initialize your own repo
git init && git add -A && git commit -m "Initial commit with vibe_bootstrap"

# 4. Open Claude Code and populate specs
#    /spec          ← Claude scans your codebase and generates spec files
#    /feature add   ← Start building your backlog
#    /implement F-001  ← Multi-agent coordinated implementation
```

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

## Commands

### Implementation Workflow

| Command | Description |
|---------|-------------|
| `/implement F-XXX` | Full feature implementation: plan → TDD → parallel agents → verify → smoke test |
| `/fix-bug B-XXX` | Bug fix: reproduce → failing test → fix → verify |
| `/refactor [desc]` | Safe refactoring with TDD and parallel agents |
| `/next-phase` | Execute the next development phase automatically |

### Quality & Testing

| Command | Description |
|---------|-------------|
| `/review` | Pre-PR code review (security, performance, a11y, correctness) |
| `/test [component]` | Generate comprehensive tests (happy path, errors, edge cases) |
| `/verify-ui [flow]` | Browser smoke test via chrome-devtools MCP |
| `/clean-up` | Code quality review of current diff |

### Project Management

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
| `/spec [file]` | Generate/update spec files (stack, architecture, conventions, API) |
| `/commit-push-pr` | Stage, commit, push, create PR — all automated |

## Spec System

Spec files give Claude deep context about your project. They live in `docs/spec/`:

| File | What it defines |
|------|----------------|
| `STACK.md` | Languages, frameworks, versions, package managers, dev tools |
| `ARCHITECTURE.md` | System design, data flow, directory structure, auth, state management |
| `CONVENTIONS.md` | Naming, error handling, validation, testing patterns, code organization |
| `API.md` | Endpoint patterns, auth scheme, request/response formats, errors |

Run `/spec` after setup to have Claude scan your codebase and populate these files interactively.

## Workflow Pattern

All implementation follows: **Plan → TDD → Parallel Agents → Verify → Smoke Test → Commit**

```
/implement F-001
  │
  ├─ Phase 1: Plan
  │   Read specs + features → design approach → get approval
  │
  ├─ Phase 2: TDD
  │   Write failing tests that define expected behavior
  │
  ├─ Phase 3: Implement (parallel agents)
  │   Backend agent ──┐
  │   Frontend agent ─┴─→ run tests → fix → commit
  │
  ├─ Phase 4: Browser Smoke Test
  │   Start servers → test flows → check console → log bugs
  │
  └─ Phase 5: Finalize
      Full test suite → update docs → final commit
```

**Session resilience**: Progress is tracked in `docs/plan/PROGRESS_*.md` files. If Claude Code loses context mid-implementation, use `/implement --resume` to pick up exactly where it left off.

## Customization

### Using a preset with overrides

```bash
python setup.py --preset django-react
# Then edit CLAUDE.md, vibe.config.json, or .claude/settings.json as needed
```

### Custom configuration

```bash
# Copy and edit the example config
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

Adds `deploy.sh` + `deploy.ps1` (semver-bump from latest git tag, build + push Docker image, trigger a redeploy webhook), a multi-stage `Dockerfile`, and `docker-entrypoint.sh`. Assumes a Portainer-style webhook deploy model (`PORTAINER_WEBHOOK_URL` / `PORTAINER_DEV_WEBHOOK_URL` in `.env`). Skip the flag if your deploy target is different — the scripts are a starting point, not a hard requirement.

### Settings (two-tier permissions)

The generated `.claude/settings.json` is the team-shared, version-controlled permission set. The runtime also merges `.claude/settings.local.json` if present — that file is gitignored by default. Use it for machine-specific or experimental permission grants without polluting the shared config (e.g., new MCP servers you're trying out, ad-hoc Bash prefixes a teammate doesn't need).

### Browser automation requirement

`/verify-ui`, `/implement`, `/fix-bug`, and `/refactor` reference the [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) for browser smoke testing. Install and configure that MCP in your Claude Code settings — the bootstrap commands assume tools named `mcp__chrome-devtools__*` are available.

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

## Project Structure (after setup)

```
your-project/
├── .claude/
│   ├── commands/          # 16 slash commands
│   ├── settings.json      # Permissions + auto-format hooks (committed)
│   ├── settings.local.json # (gitignored) machine-specific perms — created by Claude Code on demand
│   └── launch.json        # Dev server configs
├── .gitignore             # Generated; preserves any existing one
├── CLAUDE.md              # Project guide (stack, workflow, conventions, dispatch spec, smoke playbook)
├── docs/
│   ├── plan/
│   │   ├── FEATURES.md    # Feature backlog
│   │   ├── ACTIVE.md      # Sprint tracker
│   │   ├── BUGS.md        # Bug tracker
│   │   ├── DECISIONS.md   # Architecture decisions
│   │   ├── DEPENDENCIES.md # Impact analysis
│   │   └── discovery/     # Feature discovery docs
│   └── spec/
│       ├── STACK.md        # Technical stack
│       ├── ARCHITECTURE.md # System design
│       ├── CONVENTIONS.md  # Code patterns
│       └── API.md          # API contracts
├── vibe.config.json        # Bootstrap config (for re-runs)
└── (with --with-deploy:)
    ├── deploy.sh           # bash: bump semver, build, push, redeploy
    ├── deploy.ps1          # PowerShell equivalent
    ├── Dockerfile          # Multi-stage; customize for your stack
    └── docker-entrypoint.sh
```

## FAQ

**Q: Can I use this with an existing project?**
Yes. Run `python setup.py --target /path/to/existing/project`. It won't overwrite existing files without confirmation. Then run `/spec --update` to generate specs from your existing codebase.

**Q: What if my stack isn't in the presets?**
Use `python setup.py` (interactive mode) and select "Custom" to configure manually. Or copy the closest preset and edit `vibe.config.json`.

**Q: Do I need the chrome-devtools MCP for `/verify-ui`?**
Yes — `/verify-ui` (and the smoke-test phase of `/implement`, `/fix-bug`, `/refactor`) call tools named `mcp__chrome-devtools__*`. Install the [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) in your Claude Code settings. If you skip it, the other 15 commands still work — just do browser testing manually.

**Q: How do I update the bootstrap in an existing project?**
Re-run `python setup.py` with your existing `vibe.config.json`. It will regenerate config files and offer to update commands.

## License

MIT
