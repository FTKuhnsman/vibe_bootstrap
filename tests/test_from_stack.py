"""Tests for the --from-stack keyword resolution."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from lib.stack_keywords import STACK_DB, resolve_stack
from lib.validate import validate_preset_schema

import json
import tempfile


class TestResolveStack:
    def test_single_backend_keyword(self):
        config, unknown = resolve_stack("django")
        assert config is not None
        assert unknown == []
        assert config["backend"]["framework"] == "django"
        assert config["backend"]["language"] == "python"
        assert config["frontend"] is None

    def test_single_frontend_keyword(self):
        config, unknown = resolve_stack("react")
        assert config is not None
        assert config["frontend"]["framework"] == "react"
        assert config["backend"] is None

    def test_backend_plus_frontend(self):
        config, unknown = resolve_stack("django react")
        assert config is not None
        assert config["backend"]["framework"] == "django"
        assert config["frontend"]["framework"] == "react"

    def test_plus_separator(self):
        config, unknown = resolve_stack("fastapi+vue")
        assert config is not None
        assert config["backend"]["framework"] == "fastapi"
        assert config["frontend"]["framework"] == "vue"

    def test_comma_separator(self):
        config, unknown = resolve_stack("flask, react")
        assert config is not None
        assert config["backend"]["framework"] == "flask"
        assert config["frontend"]["framework"] == "react"

    def test_fullstack_keyword_sets_both(self):
        config, unknown = resolve_stack("nextjs")
        assert config is not None
        assert config["frontend"]["framework"] == "nextjs"
        assert config["backend"] is None

    def test_sveltekit(self):
        config, unknown = resolve_stack("sveltekit")
        assert config is not None
        assert config["frontend"]["framework"] == "sveltekit"
        assert config["backend"] is None

    def test_phoenix(self):
        config, unknown = resolve_stack("phoenix")
        assert config is not None
        assert config["backend"]["framework"] == "phoenix"
        assert config["backend"]["language"] == "elixir"

    def test_unknown_token_reported(self):
        config, unknown = resolve_stack("django bogus-framework")
        assert config is not None
        assert "bogus-framework" in unknown
        assert config["backend"]["framework"] == "django"

    def test_all_unknown_returns_none(self):
        config, unknown = resolve_stack("totally-made-up stack")
        assert config is None
        assert "totally-made-up" in unknown
        assert "stack" in unknown

    def test_empty_input_returns_none(self):
        config, unknown = resolve_stack("")
        assert config is None
        assert unknown == []

    def test_case_insensitive(self):
        config, unknown = resolve_stack("Django React")
        assert config is not None
        assert config["backend"]["framework"] == "django"
        assert config["frontend"]["framework"] == "react"

    def test_expo_django(self):
        config, unknown = resolve_stack("expo django")
        assert config is not None
        assert config["backend"]["framework"] == "django"
        assert config["frontend"]["framework"] == "expo"

    def test_go_htmx(self):
        config, unknown = resolve_stack("go htmx")
        assert config is not None
        assert config["backend"]["framework"] == "go-stdlib"
        assert config["frontend"] is None

    def test_defaults_included(self):
        config, _ = resolve_stack("django")
        assert "project" in config
        assert "git" in config
        assert config["git"]["main_branch"] == "main"
        assert config["platform"] == "auto"


class TestSchemaCompliance:
    """Every keyword combo that produces a config must pass preset schema validation."""

    COMBOS = [
        "django", "django react", "fastapi vue", "flask react",
        "express react", "rails react", "laravel vue",
        "go htmx", "phoenix", "nextjs", "sveltekit",
        "expo django", "python", "node",
    ]

    @pytest.fixture(params=COMBOS)
    def stack_input(self, request) -> str:
        return request.param

    def test_generated_preset_passes_schema(self, stack_input: str, tmp_path: Path):
        config, _ = resolve_stack(stack_input)
        assert config is not None, f"resolve_stack({stack_input!r}) returned None"
        preset_path = tmp_path / "test_preset.json"
        preset_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        violations = validate_preset_schema(preset_path)
        assert violations == [], (
            f"--from-stack '{stack_input}' schema violations: {violations}"
        )
