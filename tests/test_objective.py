"""Tests for objective parsing, window parsing, and budget derivation."""

import unittest

from slobudget.objective import (
    Objective,
    ObjectiveError,
    derive_budget,
    format_duration,
    parse_objective,
    parse_window,
)


class ParseObjectiveTests(unittest.TestCase):
    def test_percent_sign(self):
        self.assertAlmostEqual(parse_objective("99.9%"), 0.999)

    def test_bare_percentage(self):
        self.assertAlmostEqual(parse_objective("99.9"), 0.999)

    def test_ratio(self):
        self.assertAlmostEqual(parse_objective("0.98"), 0.98)

    def test_rejects_zero(self):
        with self.assertRaises(ObjectiveError):
            parse_objective("0")

    def test_rejects_one(self):
        with self.assertRaises(ObjectiveError):
            parse_objective("100%")

    def test_rejects_garbage(self):
        with self.assertRaises(ObjectiveError):
            parse_objective("high")


class ParseWindowTests(unittest.TestCase):
    def test_days(self):
        self.assertEqual(parse_window("30d"), 30 * 86400)

    def test_hours(self):
        self.assertEqual(parse_window("24h"), 86400)

    def test_weeks(self):
        self.assertEqual(parse_window("2w"), 2 * 604800)

    def test_bare_seconds(self):
        self.assertEqual(parse_window("300"), 300)

    def test_rejects_bad_unit(self):
        with self.assertRaises(ObjectiveError):
            parse_window("5y")

    def test_rejects_zero(self):
        with self.assertRaises(ObjectiveError):
            parse_window("0d")


class FormatDurationTests(unittest.TestCase):
    def test_days_hours(self):
        self.assertEqual(format_duration(90000), "1d 1h")

    def test_seconds_only(self):
        self.assertEqual(format_duration(45), "45s")

    def test_zero(self):
        self.assertEqual(format_duration(0), "0s")

    def test_thirty_days(self):
        self.assertEqual(format_duration(30 * 86400), "30d")


class DeriveBudgetTests(unittest.TestCase):
    def test_within_budget(self):
        obj = Objective(target=0.98, window_seconds=30 * 86400)
        status = derive_budget(obj, total_events=96000, bad_events=1536)
        self.assertAlmostEqual(status.budget_events, 1920.0)
        self.assertAlmostEqual(status.consumed_fraction, 0.8)
        self.assertAlmostEqual(status.remaining_fraction, 0.2)
