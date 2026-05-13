"""
Bootstrap integrity validators.

Every function here enforces a structural invariant of the vibe_bootstrap
system.  Tests import these directly — the architecture IS the test suite.
Bypassing any invariant requires modifying this file, which shows in the
PR diff for human review.

Zero external dependencies.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# YAML-frontmatter parser (no PyYAML dependency)
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(
    r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL
)

_YAML_LIST_ITEM = re.compile(r"^\s*-\s+(.+)$")


def parse_agent_frontmatter(agent_path: Path) -> dict:
    """Parse YAML frontmatter from an agent .md file.

    Returns dict with keys: name, description, tools, model (all optional
    except name).  Raises ValueError on missing/malformed frontmatter.
    """
    text = agent_path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise ValueError(f"No YAML frontmatter in {agent_path.name}")

    raw = m.group(1)
    result: dict = {}
    current_key: str | None = None
    current_list: list[str] | None = None

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        list_match = _YAML_LIST_ITEM.match(line)
        if list_match and current_key is not None:
            if current_list is None:
                current_list = []
                result[current_key] = current_list
            current_list.append(list_match.group(1).strip().strip("'\""))
            continue

        if ":" in stripped:
            if current_list is not None:
                current_list = None
            key, _, val = stripped.partition(":")
            key = key.strip()
            val = val.strip().strip("'\"")
            current_key = key
            if val:
                result[key] = val
                current_list = None
            else:
                current_list = []
                result[key] = current_list

    return result


# ---------------------------------------------------------------------------
# Subagent tool-grant invariants
# ---------------------------------------------------------------------------

AGENT_TOOL_POLICY: dict[str, dict] = {
    "test-writer": {
        "required": {"Read", "Grep", "Glob", "Write", "Edit"},
        "forbidden": {"Bash"},
    },
    "implementer": {
        "required": {"Read", "Write", "Edit", "Bash"},
        "forbidden": set(),
    },
    "code-reviewer": {
        "required": {"Read", "Grep", "Glob"},
        "forbidden": {"Write", "Edit"},
    },
    "layer-checker": {
        "required": {"Read", "Grep", "Glob"},
        "forbidden": {"Write", "Edit"},
    },
    "garbage-collector": {
        "required": {"Read", "Grep", "Glob"},
        "forbidden": set(),
    },
    "doc-gardener": {
        "required": {"Read", "Grep", "Glob"},
        "forbidden": set(),
    },
    "discovery-interviewer": {
        "required": {"Read", "Grep", "Glob", "Write", "Edit"},
        "forbidden": {"Bash"},
    },
}


def _base_tool(tool_str: str) -> str:
    """Extract the base tool name from a potentially scoped grant.

    'Bash(git diff:*)' → 'Bash', 'Read' → 'Read'.
    """
    paren = tool_str.find("(")
    return tool_str[:paren] if paren != -1 else tool_str


def validate_agent_tools(agents_dir: Path) -> list[str]:
    """Check every agent's tool list against AGENT_TOOL_POLICY.

    Returns a list of violation strings (empty means all clear).
    """
    violations: list[str] = []

    for agent_name, policy in AGENT_TOOL_POLICY.items():
        agent_path = agents_dir / f"{agent_name}.md"
        if not agent_path.exists():
            violations.append(f"{agent_name}: agent file missing")
            continue

        try:
            fm = parse_agent_frontmatter(agent_path)
        except ValueError as exc:
            violations.append(f"{agent_name}: {exc}")
            continue

        tools_raw = fm.get("tools", [])
        if isinstance(tools_raw, str):
            tools_raw = [tools_raw]
        base_tools = {_base_tool(t) for t in tools_raw}

        for req in policy["required"]:
            if req not in base_tools:
                violations.append(
                    f"{agent_name}: missing required tool '{req}'"
                )

        for forbid in policy["forbidden"]:
            if forbid in base_tools:
                violations.append(
                    f"{agent_name}: has forbidden tool '{forbid}'"
                )

    return violations


# ---------------------------------------------------------------------------
# Command → agent reference validator
# ---------------------------------------------------------------------------

_AGENT_REF_RE = re.compile(
    r"`(test-writer|implementer|code-reviewer|layer-checker"
    r"|garbage-collector|doc-gardener|discovery-interviewer)`"
)


def validate_command_agent_refs(
    commands_dir: Path, agents_dir: Path
) -> list[str]:
    """Verify every agent name referenced in commands resolves to a file."""
    violations: list[str] = []

    for cmd_path in sorted(commands_dir.glob("*.md")):
        text = cmd_path.read_text(encoding="utf-8")
        for m in _AGENT_REF_RE.finditer(text):
            agent_name = m.group(1)
            agent_file = agents_dir / f"{agent_name}.md"
            if not agent_file.exists():
                violations.append(
                    f"{cmd_path.name}: references agent '{agent_name}' "
                    f"but {agent_file} does not exist"
                )

    return violations


# ---------------------------------------------------------------------------
# Preset schema validator
# ---------------------------------------------------------------------------

_REQUIRED_BACKEND_KEYS = {
    "language", "framework", "test_command", "directory",
    "server_command", "server_port",
}
_REQUIRED_FRONTEND_KEYS = {
    "language", "framework", "test_command", "directory",
    "server_command", "server_port",
}


def validate_preset_schema(preset_path: Path) -> list[str]:
    """Validate a preset JSON against the required schema."""
    violations: list[str] = []

    try:
        with open(preset_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return [f"{preset_path.name}: cannot load — {exc}"]

    if not isinstance(data, dict):
        return [f"{preset_path.name}: root is not a JSON object"]

    project = data.get("project")
    if not isinstance(project, dict) or "name" not in project:
        violations.append(f"{preset_path.name}: missing project.name")

    git = data.get("git")
    if not isinstance(git, dict) or "main_branch" not in git:
        violations.append(f"{preset_path.name}: missing git.main_branch")

    backend = data.get("backend")
    if isinstance(backend, dict):
        missing = _REQUIRED_BACKEND_KEYS - set(backend.keys())
        for key in sorted(missing):
            violations.append(
                f"{preset_path.name}: backend missing '{key}'"
            )

    frontend = data.get("frontend")
    if isinstance(frontend, dict):
        missing = _REQUIRED_FRONTEND_KEYS - set(frontend.keys())
        for key in sorted(missing):
            violations.append(
                f"{preset_path.name}: frontend missing '{key}'"
            )

    return violations


# ---------------------------------------------------------------------------
# Feature lifecycle
# ---------------------------------------------------------------------------

_IMPLEMENTABLE_STATUSES = {"backlog", "in-progress", "blocked"}
_NON_IMPLEMENTABLE_STATUSES = {"stub", "done"}

_FEATURE_RE = re.compile(r"^###\s+F-\d{3}:\s+", re.MULTILINE)
_STATUS_RE = re.compile(
    r"-\s+\*\*Status:\*\*\s+`([^`]+)`", re.MULTILINE
)


def can_implement(feature_status: str | None) -> bool:
    """Gate: can a feature with this status be implemented?

    True for: backlog, in-progress, blocked, None (backward compat).
    False for: stub, done.
    """
    if feature_status is None:
        return True
    return feature_status.lower() in _IMPLEMENTABLE_STATUSES


def parse_features(features_path: Path) -> list[dict]:
    """Parse FEATURES.md into a list of {id, name, status} dicts."""
    text = features_path.read_text(encoding="utf-8")
    features: list[dict] = []

    sections = re.split(r"(?=^###\s+F-\d{3}:)", text, flags=re.MULTILINE)
    for section in sections:
        header_match = re.match(
            r"^###\s+(F-\d{3}):\s+(.+?)$", section, re.MULTILINE
        )
        if not header_match:
            continue
        fid = header_match.group(1)
        name = header_match.group(2).strip()
        status_match = _STATUS_RE.search(section)
        status = status_match.group(1) if status_match else None
        features.append({"id": fid, "name": name, "status": status})

    return features


def validate_features_lifecycle(features_path: Path) -> list[str]:
    """Validate lifecycle rules in FEATURES.md."""
    violations: list[str] = []
    features = parse_features(features_path)

    for f in features:
        status = f["status"]
        if status is not None and status.lower() not in (
            _IMPLEMENTABLE_STATUSES | _NON_IMPLEMENTABLE_STATUSES
        ):
            violations.append(
                f"{f['id']}: unknown status '{status}'"
            )

        if status and status.lower() == "stub":
            # stub features should not have filled acceptance criteria
            # (this is a soft check — the full text isn't parsed here)
            pass

    return violations


# ---------------------------------------------------------------------------
# Coverage gate for /garbage-collect --fix
# ---------------------------------------------------------------------------


def check_coverage_gate(
    min_coverage: float, actual_coverage: float
) -> tuple[bool, str]:
    """Decide whether --fix is allowed given coverage.

    Returns (passed, reason).
    """
    if actual_coverage >= min_coverage:
        return True, (
            f"Coverage {actual_coverage:.1f}% meets minimum "
            f"{min_coverage:.1f}%."
        )
    return False, (
        f"Coverage {actual_coverage:.1f}% is below the minimum "
        f"{min_coverage:.1f}% required for --fix mode. "
        f"Run with --force to override (requires explicit confirmation "
        f"and is logged in GC_LOG.md with force-used: true)."
    )


# ---------------------------------------------------------------------------
# Layer model parser
# ---------------------------------------------------------------------------

_LAYER_ITEM_RE = re.compile(
    r"^\d+\.\s+\*\*(\w+)\*\*", re.MULTILINE
)
_MAPPING_ROW_RE = re.compile(
    r"^\|\s*`([^`]+(?:`,\s*`[^`]+)*)`\s*\|\s*`(\w+)`\s*\|",
    re.MULTILINE,
)
_OPT_OUT_SENTINEL = "does not enforce a layered architecture"


def parse_layer_model(
    layers_path: Path,
) -> tuple[list[str], dict[str, str], bool]:
    """Parse LAYERS.md.

    Returns (ordered_layers, pattern_to_layer_map, opted_out).
    Raises ValueError if unparseable.
    """
    text = layers_path.read_text(encoding="utf-8")

    if _OPT_OUT_SENTINEL in text:
        return [], {}, True

    layers = _LAYER_ITEM_RE.findall(text)
    if not layers:
        raise ValueError("No layers found in LAYERS.md")

    pattern_map: dict[str, str] = {}
    for m in _MAPPING_ROW_RE.finditer(text):
        patterns_str = m.group(1)
        layer = m.group(2)
        for pat in patterns_str.split("`,"):
            pat = pat.strip().strip("`").strip()
            if pat:
                pattern_map[pat] = layer

    if not pattern_map:
        raise ValueError("No module→layer mappings found in LAYERS.md")

    return layers, pattern_map, False
