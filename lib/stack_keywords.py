"""Keyword-to-preset-fields mapping for ``--from-stack``.

Zero dependencies.  Each keyword maps to a partial preset dict (backend,
frontend, or both).  Tokens from freeform input are matched against keys.
Matched dicts are deep-merged.  Gaps are filled with sensible defaults.
The output is validated by ``lib.validate.validate_preset_schema``.
"""

from __future__ import annotations

import copy
from typing import Any


# ---------------------------------------------------------------------------
# Keyword database
# ---------------------------------------------------------------------------

STACK_DB: dict[str, dict[str, Any]] = {
    # --- Backend languages / frameworks ---
    "django": {
        "backend": {
            "language": "python",
            "framework": "django",
            "directory": "backend",
            "test_command": "cd backend && pytest",
            "lint_command": "cd backend && ruff check . && ruff format --check .",
            "format_tool": "ruff format",
            "format_pattern": "\\.py$",
            "server_command": "python manage.py runserver",
            "server_port": 8000,
            "package_manager": "pip",
            "install_command": "pip install -r requirements.txt",
            "cli_prefixes": ["python manage.py", "pytest", "ruff"],
        }
    },
    "fastapi": {
        "backend": {
            "language": "python",
            "framework": "fastapi",
            "directory": "backend",
            "test_command": "cd backend && pytest",
            "lint_command": "cd backend && ruff check . && ruff format --check .",
            "format_tool": "ruff format",
            "format_pattern": "\\.py$",
            "server_command": "uvicorn app.main:app --reload",
            "server_port": 8000,
            "package_manager": "pip",
            "install_command": "pip install -r requirements.txt",
            "cli_prefixes": ["uvicorn", "pytest", "ruff"],
        }
    },
    "flask": {
        "backend": {
            "language": "python",
            "framework": "flask",
            "directory": "backend",
            "test_command": "cd backend && pytest",
            "lint_command": "cd backend && ruff check . && ruff format --check .",
            "format_tool": "ruff format",
            "format_pattern": "\\.py$",
            "server_command": "flask run",
            "server_port": 5000,
            "package_manager": "pip",
            "install_command": "pip install -r requirements.txt",
            "cli_prefixes": ["flask", "pytest", "ruff"],
        }
    },
    "express": {
        "backend": {
            "language": "typescript",
            "framework": "express",
            "directory": "backend",
            "test_command": "cd backend && npm test",
            "lint_command": "cd backend && npm run lint",
            "format_tool": "npx prettier --write",
            "format_pattern": "\\.(ts|js|json)$",
            "server_command": "npm run dev",
            "server_port": 3000,
            "package_manager": "npm",
            "install_command": "npm install",
            "cli_prefixes": ["npm", "npx", "node"],
        }
    },
    "rails": {
        "backend": {
            "language": "ruby",
            "framework": "rails",
            "directory": "backend",
            "test_command": "cd backend && bundle exec rspec",
            "lint_command": "cd backend && bundle exec rubocop",
            "format_tool": "bundle exec rubocop -a",
            "format_pattern": "\\.rb$",
            "server_command": "bin/rails server",
            "server_port": 3000,
            "package_manager": "bundler",
            "install_command": "bundle install",
            "cli_prefixes": ["bundle exec", "rails", "rake"],
        }
    },
    "laravel": {
        "backend": {
            "language": "php",
            "framework": "laravel",
            "directory": "backend",
            "test_command": "cd backend && php artisan test",
            "lint_command": "cd backend && ./vendor/bin/pint --test",
            "format_tool": "./vendor/bin/pint",
            "format_pattern": "\\.php$",
            "server_command": "php artisan serve",
            "server_port": 8000,
            "package_manager": "composer",
            "install_command": "composer install",
            "cli_prefixes": ["php artisan", "composer"],
        }
    },
    "go": {
        "backend": {
            "language": "go",
            "framework": "go-stdlib",
            "directory": ".",
            "test_command": "go test ./...",
            "lint_command": "golangci-lint run",
            "format_tool": "gofmt -w",
            "format_pattern": "\\.go$",
            "server_command": "go run .",
            "server_port": 8080,
            "package_manager": "go",
            "install_command": "go mod download",
            "cli_prefixes": ["go", "golangci-lint"],
        }
    },
    "phoenix": {
        "backend": {
            "language": "elixir",
            "framework": "phoenix",
            "directory": "backend",
            "test_command": "cd backend && mix test",
            "lint_command": "cd backend && mix credo",
            "format_tool": "mix format",
            "format_pattern": "\\.ex$|\\.exs$",
            "server_command": "mix phx.server",
            "server_port": 4000,
            "package_manager": "mix",
            "install_command": "mix deps.get",
            "cli_prefixes": ["mix", "iex"],
        }
    },
    # --- Frontend frameworks ---
    "react": {
        "frontend": {
            "language": "typescript",
            "framework": "react",
            "directory": "frontend",
            "test_command": "cd frontend && pnpm test",
            "lint_command": "cd frontend && pnpm lint",
            "build_command": "cd frontend && pnpm build",
            "format_tool": "npx prettier --write",
            "format_pattern": "\\.(ts|tsx|js|jsx|json|css)$",
            "server_command": "pnpm dev",
            "server_port": 5173,
            "package_manager": "pnpm",
            "install_command": "pnpm install",
            "cli_prefixes": ["pnpm", "npx"],
        }
    },
    "vue": {
        "frontend": {
            "language": "typescript",
            "framework": "vue",
            "directory": "frontend",
            "test_command": "cd frontend && pnpm test",
            "lint_command": "cd frontend && pnpm lint",
            "build_command": "cd frontend && pnpm build",
            "format_tool": "npx prettier --write",
            "format_pattern": "\\.(ts|vue|js|json|css)$",
            "server_command": "pnpm dev",
            "server_port": 5173,
            "package_manager": "pnpm",
            "install_command": "pnpm install",
            "cli_prefixes": ["pnpm", "npx"],
        }
    },
    "htmx": {
        "frontend": None,
    },
    "nextjs": {
        "frontend": {
            "language": "typescript",
            "framework": "nextjs",
            "directory": ".",
            "test_command": "npm test",
            "lint_command": "npm run lint",
            "build_command": "npm run build",
            "format_tool": "npx prettier --write",
            "format_pattern": "\\.(ts|tsx|js|jsx|json|css)$",
            "server_command": "npm run dev",
            "server_port": 3000,
            "package_manager": "npm",
            "install_command": "npm install",
            "cli_prefixes": ["npm", "npx", "next"],
        },
        "backend": None,
    },
    "sveltekit": {
        "frontend": {
            "language": "typescript",
            "framework": "sveltekit",
            "directory": ".",
            "test_command": "npm test",
            "lint_command": "npm run lint",
            "build_command": "npm run build",
            "format_tool": "npx prettier --write",
            "format_pattern": "\\.(ts|svelte|js|json|css)$",
            "server_command": "npm run dev",
            "server_port": 5173,
            "package_manager": "npm",
            "install_command": "npm install",
            "cli_prefixes": ["npm", "npx"],
        },
        "backend": None,
    },
    "expo": {
        "frontend": {
            "language": "typescript",
            "framework": "expo",
            "directory": "frontend",
            "test_command": "cd frontend && npx jest",
            "lint_command": "cd frontend && npx eslint .",
            "build_command": "",
            "format_tool": "npx prettier --write",
            "format_pattern": "\\.(ts|tsx|js|jsx|json)$",
            "server_command": "npx expo start",
            "server_port": 8081,
            "package_manager": "npm",
            "install_command": "npm install",
            "cli_prefixes": ["npx expo", "npx jest", "npm"],
        }
    },
    # --- Aliases ---
    "python": {
        "backend": {
            "language": "python",
            "framework": "python",
            "directory": ".",
            "test_command": "pytest",
            "lint_command": "ruff check . && ruff format --check .",
            "format_tool": "ruff format",
            "format_pattern": "\\.py$",
            "server_command": "",
            "server_port": None,
            "package_manager": "pip",
            "install_command": "pip install -r requirements.txt",
            "cli_prefixes": ["python", "pytest", "ruff"],
        }
    },
    "node": {
        "backend": {
            "language": "typescript",
            "framework": "node",
            "directory": ".",
            "test_command": "npm test",
            "lint_command": "npm run lint",
            "format_tool": "npx prettier --write",
            "format_pattern": "\\.(ts|js|json)$",
            "server_command": "npm run dev",
            "server_port": 3000,
            "package_manager": "npm",
            "install_command": "npm install",
            "cli_prefixes": ["npm", "npx", "node"],
        }
    },
    "liveview": {
        "frontend": None,
    },
}


# ---------------------------------------------------------------------------
# Resolution logic
# ---------------------------------------------------------------------------


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge *override* into a copy of *base*."""
    result = copy.deepcopy(base)
    for key, val in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(val, dict)
        ):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = copy.deepcopy(val)
    return result


def _tokenize(freeform: str) -> list[str]:
    """Normalize freeform input into lookup tokens."""
    raw = freeform.lower().replace(",", " ").replace("+", " ").replace("/", " ")
    return [t.strip() for t in raw.split() if t.strip()]


def resolve_stack(freeform: str) -> tuple[dict | None, list[str]]:
    """Resolve freeform stack description into a preset-shaped config dict.

    Returns ``(config, unrecognized_tokens)``.
    *config* is ``None`` if no tokens matched anything.
    *unrecognized_tokens* lists tokens that didn't match any keyword.
    The returned config always includes ``project``, ``git``, and ``platform``
    defaults so it can be passed straight to ``validate_preset_schema``.
    """
    tokens = _tokenize(freeform)
    if not tokens:
        return None, []

    merged: dict[str, Any] = {}
    unrecognized: list[str] = []

    for token in tokens:
        if token in STACK_DB:
            merged = _deep_merge(merged, STACK_DB[token])
        else:
            unrecognized.append(token)

    if not merged:
        return None, unrecognized

    merged.setdefault("project", {"name": "My Project", "description": ""})
    merged.setdefault("git", {"main_branch": "main", "commit_convention": "conventional"})
    merged.setdefault("platform", "auto")
    merged.setdefault("backend", None)
    merged.setdefault("frontend", None)

    return merged, unrecognized
