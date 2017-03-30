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
