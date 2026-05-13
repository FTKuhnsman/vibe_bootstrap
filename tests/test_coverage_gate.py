"""Coverage guard tests for /garbage-collect --fix.

The check_coverage_gate() function is called before --fix applies changes.
These tests ensure the threshold logic is correct and the bypass path
(--force) is documented in the reason string.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.validate import check_coverage_gate


class TestCoverageGate:
    def test_below_threshold_blocks(self):
        passed, reason = check_coverage_gate(
            min_coverage=70.0, actual_coverage=45.0
        )
        assert not passed
        assert "45.0%" in reason
        assert "70.0%" in reason

    def test_at_threshold_passes(self):
        passed, reason = check_coverage_gate(
            min_coverage=70.0, actual_coverage=70.0
        )
        assert passed

    def test_above_threshold_passes(self):
        passed, reason = check_coverage_gate(
            min_coverage=70.0, actual_coverage=95.0
        )
        assert passed

    def test_zero_coverage_blocks(self):
        passed, _ = check_coverage_gate(
            min_coverage=70.0, actual_coverage=0.0
        )
        assert not passed

    def test_force_flag_documented_in_reason(self):
        """When blocked, the reason string mentions --force as an override."""
        passed, reason = check_coverage_gate(
            min_coverage=70.0, actual_coverage=30.0
        )
        assert not passed
        assert "--force" in reason

    def test_pass_reason_is_informative(self):
        passed, reason = check_coverage_gate(
            min_coverage=70.0, actual_coverage=85.0
        )
        assert passed
        assert "85.0%" in reason
