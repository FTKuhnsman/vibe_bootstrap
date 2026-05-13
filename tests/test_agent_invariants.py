"""Subagent tool-grant invariants.

These tests ARE the architecture.  Adding Bash to test-writer, or Write to
code-reviewer, breaks a test here — which shows in the PR diff for human
review.  That's the mechanical enforcement.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.validate import (
    AGENT_TOOL_POLICY,
    _base_tool,
    parse_agent_frontmatter,
    validate_agent_tools,
)
from tests.conftest import AGENTS_DIR


# ---------------------------------------------------------------------------
# Individual tool-grant invariants (the load-bearing tests)
# ---------------------------------------------------------------------------


def _tools_for(agent_name: str) -> set[str]:
    """Read an agent file and return its base tool set."""
    fm = parse_agent_frontmatter(AGENTS_DIR / f"{agent_name}.md")
    raw = fm.get("tools", [])
    if isinstance(raw, str):
        raw = [raw]
    return {_base_tool(t) for t in raw}


class TestTestWriter:
    def test_has_read_write_edit(self):
        tools = _tools_for("test-writer")
        assert {"Read", "Write", "Edit"} <= tools

    def test_cannot_bash(self):
        """test-writer must never have Bash — it writes tests, not implementations."""
        tools = _tools_for("test-writer")
        assert "Bash" not in tools


class TestImplementer:
    def test_has_bash(self):
        """implementer needs Bash for running tests and build commands."""
        tools = _tools_for("implementer")
        assert "Bash" in tools

    def test_has_write_edit(self):
        tools = _tools_for("implementer")
        assert {"Write", "Edit"} <= tools


class TestCodeReviewer:
    def test_is_read_only(self):
        """code-reviewer must never have Write or Edit — it reports, it doesn't fix."""
        tools = _tools_for("code-reviewer")
        assert "Write" not in tools
        assert "Edit" not in tools

    def test_has_read_and_grep(self):
        tools = _tools_for("code-reviewer")
        assert {"Read", "Grep", "Glob"} <= tools


class TestLayerChecker:
    def test_is_read_only(self):
        """layer-checker must never have Write or Edit."""
        tools = _tools_for("layer-checker")
        assert "Write" not in tools
        assert "Edit" not in tools


class TestDiscoveryInterviewer:
    def test_cannot_bash(self):
        """discovery-interviewer gathers info and writes docs, no shell needed."""
        tools = _tools_for("discovery-interviewer")
        assert "Bash" not in tools

    def test_can_write(self):
        tools = _tools_for("discovery-interviewer")
        assert {"Write", "Edit"} <= tools


# ---------------------------------------------------------------------------
# Structural checks across all agents
# ---------------------------------------------------------------------------


def test_all_agents_have_required_frontmatter():
    """Every agent file must have name, description, and tools in frontmatter."""
    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        fm = parse_agent_frontmatter(agent_file)
        assert "name" in fm, f"{agent_file.name}: missing 'name'"
        assert "description" in fm, f"{agent_file.name}: missing 'description'"
        assert "tools" in fm, f"{agent_file.name}: missing 'tools'"


def test_agent_descriptions_are_unique():
    """No two agents share a description — orchestrator delegation depends on this."""
    descriptions: dict[str, str] = {}
    for agent_file in sorted(AGENTS_DIR.glob("*.md")):
        fm = parse_agent_frontmatter(agent_file)
        desc = fm.get("description", "")
        for other_name, other_desc in descriptions.items():
            assert desc != other_desc, (
                f"{agent_file.name} and {other_name} share description"
            )
        descriptions[agent_file.name] = desc


def test_all_agents_in_policy_exist():
    """Every agent defined in AGENT_TOOL_POLICY has a corresponding .md file."""
    for agent_name in AGENT_TOOL_POLICY:
        agent_path = AGENTS_DIR / f"{agent_name}.md"
        assert agent_path.exists(), f"Policy defines '{agent_name}' but file missing"


def test_validate_agent_tools_returns_clean():
    """The full validator must return no violations for the current agent files."""
    violations = validate_agent_tools(AGENTS_DIR)
    assert violations == [], f"Agent tool violations: {violations}"
