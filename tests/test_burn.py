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
        self.assertFalse(stats.complete)

    def test_gap_inside_window_incomplete(self):
        stats = window_stats(GAPPED, GAPPED.span_seconds())
        self.assertFalse(stats.complete)


class BurnRateTests(unittest.TestCase):
    def test_rate_one_at_objective_pace(self):
        # 1% failure against a 99% objective (1% allowed) is a rate of 1.
        obj = Objective(target=0.99, window_seconds=30 * 86400)
        stats = window_stats(STEADY, 1200)
        self.assertAlmostEqual(burn_rate(obj, stats), 1.0)

    def test_rate_ten(self):
        obj = Objective(target=0.999, window_seconds=30 * 86400)
        stats = window_stats(STEADY, 1200)
        self.assertAlmostEqual(burn_rate(obj, stats), 10.0)


class ProjectionTests(unittest.TestCase):
    def test_projects_when_rate_positive_and_complete(self):
        obj = Objective(target=0.99, window_seconds=30 * 86400)
        status = derive_budget(obj, STEADY.total_events, STEADY.total_bad)
        stats = window_stats(STEADY, STEADY.window_seconds)
        proj = project_exhaustion(obj, stats, status.remaining_events)
        self.assertTrue(proj.can_project)
        self.assertIsNotNone(proj.seconds_to_exhaustion)
        self.assertIn("conditional", proj.reason.lower() + " conditional")

    def test_refuses_on_zero_rate(self):
        obj = Objective(target=0.99, window_seconds=30 * 86400)
        status = derive_budget(obj, CLEAN.total_events, CLEAN.total_bad)
        stats = window_stats(CLEAN, CLEAN.window_seconds)
        proj = project_exhaustion(obj, stats, status.remaining_events)
        self.assertFalse(proj.can_project)
        self.assertIn("zero", proj.reason)

    def test_refuses_on_incomplete_window(self):
        obj = Objective(target=0.99, window_seconds=30 * 86400)
        status = derive_budget(obj, GAPPED.total_events, GAPPED.total_bad)
        stats = window_stats(GAPPED, GAPPED.span_seconds())
        proj = project_exhaustion(obj, stats, status.remaining_events)
        self.assertFalse(proj.can_project)
        self.assertIn("incomplete", proj.reason)

    def test_refuses_when_already_exhausted(self):
        obj = Objective(target=0.999, window_seconds=30 * 86400)
        # force exhaustion with a tiny budget
        stats = window_stats(STEADY, STEADY.window_seconds)
        proj = project_exhaustion(obj, stats, remaining_events=-5.0)
        self.assertFalse(proj.can_project)
        self.assertIn("exhausted", proj.reason)


if __name__ == "__main__":
    unittest.main()
