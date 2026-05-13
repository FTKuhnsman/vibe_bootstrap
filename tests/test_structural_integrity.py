"""Cross-file consistency tests.

These verify that the various pieces of the bootstrap (commands, agents,
presets, specs) are wired together correctly.  A dangling reference — a
command that mentions an agent that doesn't exist, or a preset missing a
required key — breaks a test here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.validate import (
    parse_layer_model,
    validate_command_agent_refs,
    validate_preset_schema,
)
from tests.conftest import AGENTS_DIR, COMMANDS_DIR, DOCS_SPEC_DIR, PRESETS_DIR


def test_commands_reference_existing_agents():
    """Every agent name referenced in commands/ resolves to a file in agents/."""
    violations = validate_command_agent_refs(COMMANDS_DIR, AGENTS_DIR)
    assert violations == [], f"Dangling agent refs: {violations}"


class TestPresetSchema:
    @pytest.fixture(params=sorted(PRESETS_DIR.glob("*.json")))
    def preset_path(self, request) -> Path:
        return request.param

    def test_preset_conforms_to_schema(self, preset_path: Path):
        violations = validate_preset_schema(preset_path)
        assert violations == [], (
            f"{preset_path.name} schema violations: {violations}"
        )


def test_layer_model_is_parseable():
    """LAYERS.md can be parsed without errors."""
    layers_path = DOCS_SPEC_DIR / "LAYERS.md"
    layers, mapping, opted_out = parse_layer_model(layers_path)
    if opted_out:
        return
    assert len(layers) > 0, "No layers parsed from LAYERS.md"
    assert len(mapping) > 0, "No module mappings parsed from LAYERS.md"


def test_expected_agent_count():
    """The bootstrap ships exactly 7 subagents."""
    agent_files = list(AGENTS_DIR.glob("*.md"))
    assert len(agent_files) == 7, (
        f"Expected 7 agents, found {len(agent_files)}: "
        f"{[f.name for f in agent_files]}"
    )


def test_expected_command_count():
    """The bootstrap ships at least 18 slash commands (19 after garden-docs)."""
    cmd_files = list(COMMANDS_DIR.glob("*.md"))
    assert len(cmd_files) >= 18, (
        f"Expected >=18 commands, found {len(cmd_files)}: "
        f"{[f.name for f in cmd_files]}"
    )
