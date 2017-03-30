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
