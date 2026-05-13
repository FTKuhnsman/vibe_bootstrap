"""Shared fixtures for the vibe_bootstrap test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO_ROOT / "agents"
COMMANDS_DIR = REPO_ROOT / "commands"
PRESETS_DIR = REPO_ROOT / "presets"
DOCS_SPEC_DIR = REPO_ROOT / "docs" / "spec"
DOCS_PLAN_DIR = REPO_ROOT / "docs" / "plan"


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def agents_dir() -> Path:
    return AGENTS_DIR


@pytest.fixture
def commands_dir() -> Path:
    return COMMANDS_DIR


@pytest.fixture
def presets_dir() -> Path:
    return PRESETS_DIR
