"""End-to-end preset verification.

For every preset, verify that setup.py produces a valid project structure
with all expected directories and files — including the new .claude/agents/.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from setup import install_all, load_preset
from tests.conftest import PRESETS_DIR


def _preset_names() -> list[str]:
    return [p.stem for p in sorted(PRESETS_DIR.glob("*.json"))]


class TestPresetInstallation:
    @pytest.fixture(params=_preset_names())
    def preset_name(self, request) -> str:
        return request.param

    def test_preset_installs_cleanly(self, preset_name: str, tmp_path: Path):
        config = load_preset(preset_name)
        config.setdefault("project", {}).setdefault("name", "Test Project")
        config.setdefault("project", {}).setdefault("description", "")

        install_all(tmp_path, config, force=True)

        # .claude/agents/ populated
        agents_dir = tmp_path / ".claude" / "agents"
        assert agents_dir.exists(), ".claude/agents/ missing"
        agent_files = list(agents_dir.glob("*.md"))
        assert len(agent_files) == 7, (
            f"Expected 7 agents, found {len(agent_files)}"
        )

        # .claude/commands/ populated
        commands_dir = tmp_path / ".claude" / "commands"
        assert commands_dir.exists(), ".claude/commands/ missing"
        cmd_files = list(commands_dir.glob("*.md"))
        assert len(cmd_files) >= 18, (
            f"Expected >=18 commands, found {len(cmd_files)}"
        )

        # docs/spec/ populated
        spec_dir = tmp_path / "docs" / "spec"
        assert spec_dir.exists(), "docs/spec/ missing"
        spec_files = list(spec_dir.glob("*.md"))
        assert len(spec_files) >= 8, (
            f"Expected >=8 spec files, found {len(spec_files)}"
        )

        # docs/plan/ populated
        plan_dir = tmp_path / "docs" / "plan"
        assert plan_dir.exists(), "docs/plan/ missing"

        # CLAUDE.md and AGENTS.md exist
        assert (tmp_path / "CLAUDE.md").exists(), "CLAUDE.md missing"
        assert (tmp_path / "AGENTS.md").exists(), "AGENTS.md missing"

        # vibe.config.json exists
        assert (tmp_path / "vibe.config.json").exists(), "vibe.config.json missing"


class TestBackwardCompat:
    def test_rerun_preserves_user_files(self, tmp_path: Path):
        """Simulate an already-bootstrapped project.

        First run: install everything.
        Modify a spec file (simulating user curation).
        Second run: without --force, spec file must be preserved.
        New files (agents) must still be added.
        """
        config = load_preset("django-react")
        config.setdefault("project", {}).setdefault("name", "Test Project")

        # First install
        install_all(tmp_path, config, force=True)

        # Simulate user curation
        gp_file = tmp_path / "docs" / "spec" / "GOLDEN_PRINCIPLES.md"
        user_content = "# My Custom Golden Principles\n\nCustomized by user.\n"
        gp_file.write_text(user_content, encoding="utf-8")

        # Second install (no --force)
        install_all(tmp_path, config, force=False)

        # User-modified file preserved
        assert gp_file.read_text(encoding="utf-8") == user_content, (
            "User-modified GOLDEN_PRINCIPLES.md was overwritten without --force"
        )

        # Agents still present (they were written in first run, preserved in second)
        agents_dir = tmp_path / ".claude" / "agents"
        assert agents_dir.exists()
        assert len(list(agents_dir.glob("*.md"))) == 7
