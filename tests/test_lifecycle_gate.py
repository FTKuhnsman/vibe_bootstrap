"""Feature lifecycle enforcement tests.

The can_implement() gate is the mechanical enforcement of the
stub → backlog → in-progress → done lifecycle.  These tests ensure
the gate cannot be silently weakened.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.validate import can_implement


class TestCanImplementGate:
    def test_stub_cannot_be_implemented(self):
        assert can_implement("stub") is False

    def test_backlog_can_be_implemented(self):
        assert can_implement("backlog") is True

    def test_in_progress_can_be_implemented(self):
        assert can_implement("in-progress") is True

    def test_blocked_can_be_implemented(self):
        """Blocked features can be resumed — the block is informational."""
        assert can_implement("blocked") is True

    def test_done_cannot_be_reimplemented(self):
        assert can_implement("done") is False

    def test_none_status_is_backward_compat(self):
        """Features without a status field can be implemented (backward compat)."""
        assert can_implement(None) is True

    def test_case_insensitive(self):
        assert can_implement("Stub") is False
        assert can_implement("BACKLOG") is True
        assert can_implement("Done") is False
        assert can_implement("IN-PROGRESS") is True
