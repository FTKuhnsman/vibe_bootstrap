#!/usr/bin/env python3
"""
vibe_bootstrap setup wizard.

Zero-dependency interactive setup for Claude Code projects.
Generates CLAUDE.md, slash commands, planning docs, spec templates,
and .claude/ configuration from presets or custom config.

Usage:
    python setup.py                          # Interactive wizard
    python setup.py --preset django-react    # Non-interactive preset
    python setup.py --config config.json     # From config file
    python setup.py --commands-only           # Only install slash commands
    python setup.py --docs-only              # Only install planning docs
    python setup.py --specs-only             # Only install spec templates
    python setup.py --target /path/to/proj   # Install into different dir
    python setup.py --force                  # Overwrite existing files
"""

import argparse
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PRESETS_DIR = SCRIPT_DIR / "presets"
TEMPLATES_DIR = SCRIPT_DIR / "templates"
COMMANDS_DIR = SCRIPT_DIR / "commands"
DOCS_DIR = SCRIPT_DIR / "docs"

PRESET_CHOICES = [
    ("django-react", "Django + React (Vite)"),
    ("nextjs", "Next.js (fullstack)"),
    ("fastapi-react", "FastAPI + React"),
    ("express-react", "Express + React"),
    ("rails-react", "Rails + React"),
    ("flask-vue", "Flask + Vue"),
    ("laravel-vue", "Laravel + Vue"),
    ("go-htmx", "Go + HTMX"),
    ("python-only", "Python only (no frontend)"),
    ("node-only", "Node only (no frontend)"),
]

# ---------------------------------------------------------------------------
# Template engine
# ---------------------------------------------------------------------------


def render_template(template: str, context: dict) -> str:
    """Simple template engine supporting {{var}}, {{#if}}, {{#each}}."""

    def resolve(path: str, ctx: dict):
        """Resolve a dot-separated path against a context dict."""
        parts = path.strip().split(".")
        val = ctx
        for part in parts:
            if isinstance(val, dict):
                val = val.get(part)
            else:
                return None
            if val is None:
                return None
        return val

    def process(text: str, ctx: dict) -> str:
        # Process {{#each list}}...{{this}}...{{/each}}
        each_re = re.compile(
            r"\{\{#each\s+([\w.]+)\}\}(.*?)\{\{/each\}\}", re.DOTALL
        )
        while each_re.search(text):
            def replace_each(m):
                items = resolve(m.group(1), ctx)
                body = m.group(2)
                if not items or not isinstance(items, list):
                    return ""
                parts = []
                for item in items:
                    parts.append(body.replace("{{this}}", str(item)))
                return "".join(parts)
            text = each_re.sub(replace_each, text)

        # Process {{#if section}}...{{/if}}
        if_re = re.compile(
            r"\{\{#if\s+([\w.]+)\}\}(.*?)\{\{/if\}\}", re.DOTALL
        )
        while if_re.search(text):
            def replace_if(m):
                val = resolve(m.group(1), ctx)
                if val:
                    return m.group(2)
                return ""
            text = if_re.sub(replace_if, text)

        # Process {{variable.path}}
        var_re = re.compile(r"\{\{([\w.]+)\}\}")
        def replace_var(m):
            val = resolve(m.group(1), ctx)
            if val is None:
                return ""
            return str(val)
        text = var_re.sub(replace_var, text)

        return text

    return process(template, context)


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------


def detect_platform() -> str:
    """Return 'windows' or 'unix'."""
    return "windows" if platform.system() == "Windows" else "unix"


def resolve_platform(config: dict) -> str:
    """Resolve the effective platform from config."""
    plat = config.get("platform", "auto")
    if plat == "auto":
        return detect_platform()
    return plat


def load_preset(name: str) -> dict:
    """Load a preset JSON file by name."""
    path = PRESETS_DIR / f"{name}.json"
    if not path.exists():
        print(f"Error: preset '{name}' not found at {path}")
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_config_file(path: str) -> dict:
    """Load a config JSON file from an arbitrary path."""
    p = Path(path)
    if not p.exists():
        print(f"Error: config file not found: {path}")
        sys.exit(1)
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Generation helpers
# ---------------------------------------------------------------------------


def build_cli_prefixes(config: dict) -> list:
    """Collect CLI prefixes from backend and frontend."""
    prefixes = []
    for layer in ("backend", "frontend"):
        section = config.get(layer)
        if section:
            prefixes.extend(section.get("cli_prefixes", []))
    return prefixes


def build_bash_tool_entries(config: dict) -> list:
    """Build Bash(prefix:*) entries for settings.json."""
    prefixes = build_cli_prefixes(config)
    return [f'Bash({p}:*)' for p in prefixes]


def build_cd_entries(config: dict) -> list:
    """Build Bash(cd X:*) entries for backend/frontend dirs."""
    entries = []
    for layer in ("backend", "frontend"):
        section = config.get(layer)
        if section:
            d = section.get("directory", "")
            if d:
                entries.append(f'Bash(cd {d}:*)')
    return entries


def build_format_hook(config: dict) -> str:
    """Build the PostToolUse format hook command."""
    parts = []
    for layer in ("backend", "frontend"):
        section = config.get(layer)
        if not section:
            continue
        tool = section.get("format_tool")
        pattern = section.get("format_pattern")
        if not tool or not pattern:
            continue
        # Build the conditional branch
        grep_flag = "-qE" if "|" in pattern or "(" in pattern else "-q"
        if "ruff" in tool:
            cmd = f'ruff format \\"$file_path\\" 2>/dev/null && ruff check --fix \\"$file_path\\" 2>/dev/null'
        else:
            cmd = f'{tool} \\"$file_path\\" 2>/dev/null'
        parts.append((pattern, grep_flag, cmd))

    if not parts:
        return ""

    # Build chained if/elif
    hook = "jq -r '.tool_input.file_path // empty' | { read file_path; "
    for i, (pattern, grep_flag, cmd) in enumerate(parts):
        keyword = "if" if i == 0 else "elif"
        hook += f'{keyword} echo \\"$file_path\\" | grep {grep_flag} \'{pattern}\'; then {cmd}; '
    hook += "fi; }"
    return hook


def build_block_hook(config: dict) -> str:
    """Build the PreToolUse block hook for env files, lockfiles, .git/."""
    blocked = ["\\.env", "\\.env\\.", "\\.git/"]

    # Add lockfiles based on package managers
    lockfiles = {
        # pip: requirements.txt should NOT be blocked (users edit it)
        "pip": None,
        "pnpm": "pnpm-lock\\.yaml",
        "npm": "package-lock\\.json",
        "yarn": "yarn\\.lock",
        "composer": "composer\\.lock",
        "bundler": "Gemfile\\.lock",
    }
    for layer in ("backend", "frontend"):
        section = config.get(layer)
        if not section:
            continue
        pm = section.get("package_manager", "")
        if pm in lockfiles and lockfiles[pm] is not None:
            blocked.append(lockfiles[pm])

    pattern = "|".join(blocked)
    return (
        f"jq -r '.tool_input.file_path // empty' | "
        f"{{ read file_path; "
        f"if echo \\\"$file_path\\\" | grep -qE '({pattern})'; then "
        f"echo 'blocked: protected file' >&2; exit 2; "
        f"fi; }}"
    )


def build_settings_json(config: dict) -> str:
    """Generate .claude/settings.json content."""
    bash_tools = build_bash_tool_entries(config)
    cd_entries = build_cd_entries(config)
    format_hook = build_format_hook(config)
    block_hook = build_block_hook(config)

    # Build allowedTools list
    base_tools = [
        "Read", "Write", "Edit", "MultiEdit", "Glob", "Grep",
    ]
    git_tools = [
        "Bash(git add:*)", "Bash(git status:*)", "Bash(git commit:*)",
        "Bash(git push:*)", "Bash(git diff:*)", "Bash(git branch:*)",
        "Bash(git checkout:*)", "Bash(git log:*)", "Bash(gh pr:*)",
        "Bash(curl:*)",
    ]
    all_tools = base_tools + bash_tools + git_tools + cd_entries
    tools_json = json.dumps(all_tools, indent=6)
    # Fix indentation for nesting inside the JSON
    tools_lines = tools_json.split("\n")
    tools_formatted = tools_lines[0] + "\n" + "\n".join(
        "    " + line for line in tools_lines[1:]
    )

    deny_list = [
        "Read(./.env)", "Read(./.env.*)",
        "Write(./.env)", "Write(./.env.*)",
    ]

    hooks = {}
    if format_hook:
        hooks["PostToolUse"] = [
            {
                "matcher": "Edit|Write|MultiEdit",
                "hooks": [
                    {"type": "command", "command": format_hook}
                ],
            }
        ]
    if block_hook:
        hooks["PreToolUse"] = [
            {
                "matcher": "Edit|Write|MultiEdit",
                "hooks": [
                    {"type": "command", "command": block_hook}
                ],
            }
        ]

    settings = {
        "permissions": {
            "allowedTools": all_tools,
            "deny": deny_list,
        },
    }
    if hooks:
        settings["hooks"] = hooks

    return json.dumps(settings, indent=2)


def build_launch_json(config: dict) -> str:
    """Generate .claude/launch.json content."""
    plat = resolve_platform(config)
    configurations = []

    for layer in ("backend", "frontend"):
        section = config.get(layer)
        if not section:
            continue
        server_cmd = section.get("server_command", "")
        server_port = section.get("server_port")
        directory = section.get("directory", "")
        if not server_cmd:
            continue

        if plat == "windows":
            parts = server_cmd.split()
            entry = {
                "name": layer,
                "runtimeExecutable": "cmd",
                "runtimeArgs": ["/c"] + parts,
                "port": server_port,
            }
        else:
            entry = {
                "name": layer,
                "runtimeExecutable": "bash",
                "runtimeArgs": ["-c", server_cmd],
                "port": server_port,
            }

        if directory:
            entry["cwd"] = directory

        configurations.append(entry)

    launch = {
        "version": "0.0.1",
        "configurations": configurations,
    }
    return json.dumps(launch, indent=2)


def render_claude_md(config: dict) -> str:
    """Render CLAUDE.md from template."""
    tmpl_path = TEMPLATES_DIR / "CLAUDE.md.tmpl"
    if not tmpl_path.exists():
        print(f"Warning: template not found: {tmpl_path}")
        return ""
    with open(tmpl_path, "r", encoding="utf-8") as f:
        template = f.read()
    # Build computed fields that the simple template engine can't derive
    pms = []
    if config.get("backend") and config["backend"].get("package_manager"):
        pms.append(config["backend"]["package_manager"])
    if config.get("frontend") and config["frontend"].get("package_manager"):
        pms.append(config["frontend"]["package_manager"])
    config["package_managers"] = ", ".join(pms) if pms else "See stack docs"
    return render_template(template, config)


# ---------------------------------------------------------------------------
# File writer with overwrite protection
# ---------------------------------------------------------------------------


def write_file(target: Path, content: str, force: bool, label: str = "") -> bool:
    """Write content to target, respecting --force flag."""
    display = label or str(target)
    if target.exists() and not force:
        print(f"  {display:<45} SKIPPED (exists, use --force)")
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  {display:<45} ok")
    return True


def copy_tree(src_dir: Path, dest_dir: Path, force: bool, prefix: str = ""):
    """Recursively copy files from src_dir to dest_dir."""
    if not src_dir.exists():
        return
    for item in sorted(src_dir.rglob("*")):
        if item.is_file():
            rel = item.relative_to(src_dir)
            target = dest_dir / rel
            label = prefix + str(rel).replace("\\", "/")
            content = item.read_text(encoding="utf-8")
            write_file(target, content, force, label)


# ---------------------------------------------------------------------------
# Install functions
# ---------------------------------------------------------------------------


def install_commands(target: Path, force: bool):
    """Copy slash commands to .claude/commands/."""
    dest = target / ".claude" / "commands"
    copy_tree(COMMANDS_DIR, dest, force, ".claude/commands/")


def install_docs(target: Path, force: bool):
    """Copy planning doc templates to docs/plan/."""
    src = DOCS_DIR / "plan"
    dest = target / "docs" / "plan"
    copy_tree(src, dest, force, "docs/plan/")


def install_specs(target: Path, force: bool):
    """Copy spec templates to docs/spec/."""
    src = DOCS_DIR / "spec"
    dest = target / "docs" / "spec"
    copy_tree(src, dest, force, "docs/spec/")


def install_config_files(target: Path, config: dict, force: bool):
    """Generate and install rendered config files."""
    # CLAUDE.md
    content = render_claude_md(config)
    if content:
        write_file(target / "CLAUDE.md", content, force, "CLAUDE.md")

    # .claude/settings.json
    settings = build_settings_json(config)
    write_file(
        target / ".claude" / "settings.json", settings, force,
        ".claude/settings.json"
    )

    # .claude/launch.json
    launch = build_launch_json(config)
    write_file(
        target / ".claude" / "launch.json", launch, force,
        ".claude/launch.json"
    )

    # vibe.config.json
    write_file(
        target / "vibe.config.json",
        json.dumps(config, indent=2),
        force,
        "vibe.config.json",
    )


def install_all(target: Path, config: dict, force: bool):
    """Full installation: commands + docs + specs + config files."""
    print("\nCreating files...")
    install_commands(target, force)
    install_docs(target, force)
    install_specs(target, force)
    install_config_files(target, config, force)


# ---------------------------------------------------------------------------
# Interactive wizard
# ---------------------------------------------------------------------------


def prompt_input(label: str, default: str = "") -> str:
    """Prompt for input with an optional default."""
    if default:
        raw = input(f"  {label} [{default}]: ").strip()
        return raw if raw else default
    else:
        return input(f"  {label}: ").strip()


def interactive_wizard() -> dict:
    """Run the interactive setup wizard and return a config dict."""
    print("\nWelcome to vibe_bootstrap!\n")
    print("Choose a preset or configure manually:")

    for i, (key, label) in enumerate(PRESET_CHOICES, 1):
        print(f"  {i:>2}. {label}")
    print(f"  {len(PRESET_CHOICES) + 1:>2}. Custom (configure manually)")

    choice = input("\n> ").strip()
    try:
        idx = int(choice)
    except ValueError:
        # Try matching by name
        for i, (key, _) in enumerate(PRESET_CHOICES):
            if choice.lower() == key:
                idx = i + 1
                break
        else:
            print(f"Invalid choice: {choice}")
            sys.exit(1)

    if 1 <= idx <= len(PRESET_CHOICES):
        preset_name, preset_label = PRESET_CHOICES[idx - 1]
        config = load_preset(preset_name)
        print(f"\n  Using preset: {preset_label}")
    elif idx == len(PRESET_CHOICES) + 1:
        config = custom_wizard()
        return config
    else:
        print(f"Invalid choice: {choice}")
        sys.exit(1)

    # Let user customize common fields
    print()
    config["project"]["name"] = prompt_input(
        "Project name", config.get("project", {}).get("name", "My Project")
    )
    config["project"]["description"] = prompt_input(
        "Project description",
        config.get("project", {}).get("description", ""),
    )

    if config.get("backend"):
        config["backend"]["directory"] = prompt_input(
            "Backend directory", config["backend"].get("directory", "backend")
        )
        port = prompt_input(
            "Backend port", str(config["backend"].get("server_port", 8000))
        )
        config["backend"]["server_port"] = int(port)

    if config.get("frontend"):
        config["frontend"]["directory"] = prompt_input(
            "Frontend directory", config["frontend"].get("directory", "frontend")
        )
        port = prompt_input(
            "Frontend port", str(config["frontend"].get("server_port", 5173))
        )
        config["frontend"]["server_port"] = int(port)

    config["git"]["main_branch"] = prompt_input(
        "Git main branch", config.get("git", {}).get("main_branch", "main")
    )

    return config


def custom_wizard() -> dict:
    """Walk through manual configuration."""
    config = {
        "project": {},
        "backend": None,
        "frontend": None,
        "git": {"main_branch": "main", "commit_convention": "conventional"},
        "platform": "auto",
    }

    print()
    config["project"]["name"] = prompt_input("Project name", "My Project")
    config["project"]["description"] = prompt_input("Project description")

    # Backend
    has_backend = input("\n  Include backend? [Y/n]: ").strip().lower()
    if has_backend != "n":
        config["backend"] = {}
        config["backend"]["language"] = prompt_input("Backend language", "python")
        config["backend"]["framework"] = prompt_input("Backend framework", "django")
        config["backend"]["directory"] = prompt_input("Backend directory", "backend")
        config["backend"]["test_command"] = prompt_input(
            "Backend test command", "cd backend && pytest"
        )
        config["backend"]["lint_command"] = prompt_input(
            "Backend lint command", "cd backend && ruff check . && ruff format --check ."
        )
        config["backend"]["format_tool"] = prompt_input(
            "Backend format tool", "ruff format"
        )
        config["backend"]["format_pattern"] = prompt_input(
            "Backend format pattern (regex)", "\\.py$"
        )
        config["backend"]["server_command"] = prompt_input(
            "Backend server command", "python manage.py runserver"
        )
        port = prompt_input("Backend server port", "8000")
        config["backend"]["server_port"] = int(port)
        config["backend"]["package_manager"] = prompt_input(
            "Backend package manager", "pip"
        )
        config["backend"]["install_command"] = prompt_input(
            "Backend install command", "pip install -r requirements.txt"
        )
        cli_raw = prompt_input(
            "Backend CLI prefixes (comma-separated)",
            "python manage.py, pytest, ruff",
        )
        config["backend"]["cli_prefixes"] = [
            s.strip() for s in cli_raw.split(",") if s.strip()
        ]

    # Frontend
    has_frontend = input("\n  Include frontend? [Y/n]: ").strip().lower()
    if has_frontend != "n":
        config["frontend"] = {}
        config["frontend"]["language"] = prompt_input("Frontend language", "typescript")
        config["frontend"]["framework"] = prompt_input("Frontend framework", "react")
        config["frontend"]["directory"] = prompt_input("Frontend directory", "frontend")
        config["frontend"]["test_command"] = prompt_input(
            "Frontend test command", "cd frontend && pnpm test"
        )
        config["frontend"]["lint_command"] = prompt_input(
            "Frontend lint command", "cd frontend && pnpm lint"
        )
        config["frontend"]["build_command"] = prompt_input(
            "Frontend build command", "cd frontend && pnpm build"
        )
        config["frontend"]["format_tool"] = prompt_input(
            "Frontend format tool", "npx prettier --write"
        )
        config["frontend"]["format_pattern"] = prompt_input(
            "Frontend format pattern (regex)", "\\.(ts|tsx|js|jsx|json|css)$"
        )
        config["frontend"]["server_command"] = prompt_input(
            "Frontend server command", "pnpm dev"
        )
        port = prompt_input("Frontend server port", "5173")
        config["frontend"]["server_port"] = int(port)
        config["frontend"]["package_manager"] = prompt_input(
            "Frontend package manager", "pnpm"
        )
        config["frontend"]["install_command"] = prompt_input(
            "Frontend install command", "pnpm install"
        )
        cli_raw = prompt_input(
            "Frontend CLI prefixes (comma-separated)", "pnpm, npx"
        )
        config["frontend"]["cli_prefixes"] = [
            s.strip() for s in cli_raw.split(",") if s.strip()
        ]

    config["git"]["main_branch"] = prompt_input("Git main branch", "main")

    return config


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="vibe_bootstrap setup wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--preset",
        choices=[k for k, _ in PRESET_CHOICES],
        help="Use a named preset (non-interactive)",
    )
    parser.add_argument(
        "--config",
        metavar="PATH",
        help="Path to a pre-filled config JSON file",
    )
    parser.add_argument(
        "--commands-only",
        action="store_true",
        help="Only install slash commands",
    )
    parser.add_argument(
        "--docs-only",
        action="store_true",
        help="Only install planning docs",
    )
    parser.add_argument(
        "--specs-only",
        action="store_true",
        help="Only install spec templates",
    )
    parser.add_argument(
        "--target",
        metavar="PATH",
        default=".",
        help="Target directory (default: current directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without prompting",
    )
    return parser.parse_args()


def print_next_steps():
    print("\nDone! Next steps:")
    print("  1. Review and customize CLAUDE.md")
    print("  2. Run /spec to populate spec files with Claude")
    print("  3. Add features with /feature add")
    print("  4. Start building with /implement F-001")
    print()


def main():
    args = parse_args()
    target = Path(args.target).resolve()

    # Partial install modes (no config needed)
    if args.commands_only:
        print("Installing slash commands...")
        install_commands(target, args.force)
        print("\nDone!")
        return

    if args.docs_only:
        print("Installing planning docs...")
        install_docs(target, args.force)
        print("\nDone!")
        return

    if args.specs_only:
        print("Installing spec templates...")
        install_specs(target, args.force)
        print("\nDone!")
        return

    # Full install: need config
    if args.config:
        config = load_config_file(args.config)
    elif args.preset:
        config = load_preset(args.preset)
        # Set defaults for project if missing
        config.setdefault("project", {})
        config["project"].setdefault("name", "My Project")
        config["project"].setdefault("description", "")
    else:
        config = interactive_wizard()

    install_all(target, config, args.force)
    print_next_steps()


if __name__ == "__main__":
    main()
