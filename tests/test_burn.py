"""Tests for burn rate over a window and conditional projection."""

import unittest

from slobudget.burn import burn_rate, project_exhaustion, window_stats
from slobudget.objective import Objective, derive_budget
from slobudget.sli import parse_series


def _series(rows):
    return parse_series("\n".join(rows) + "\n")


STEADY = _series(
    [
        "2026-03-01T00:00:00Z,1980,2000",  # 1% failure each
        "2026-03-01T00:05:00Z,1980,2000",
        "2026-03-01T00:10:00Z,1980,2000",
        "2026-03-01T00:15:00Z,1980,2000",
    ]
)

CLEAN = _series(
    [
        "2026-03-01T00:00:00Z,2000,2000",
        "2026-03-01T00:05:00Z,2000,2000",
        "2026-03-01T00:10:00Z,2000,2000",
    ]
)

GAPPED = _series(
    [
        "2026-03-01T00:00:00Z,1980,2000",
        "2026-03-01T00:05:00Z,1980,2000",
        "2026-03-01T00:20:00Z,1980,2000",  # gap
        "2026-03-01T00:25:00Z,1980,2000",
    ]
)


class WindowStatsTests(unittest.TestCase):
    def test_full_window_complete(self):
        stats = window_stats(STEADY, 1200)  # exactly the covered span
        self.assertEqual(stats.intervals, 4)
        self.assertTrue(stats.complete)
        self.assertAlmostEqual(stats.failure_ratio, 0.01)

    def test_window_longer_than_data_incomplete(self):
        stats = window_stats(STEADY, 3600)
