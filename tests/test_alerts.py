"""Tests for multi-window burn rate alert evaluation."""

import unittest

from slobudget.alerts import (
    AlertPolicy,
    any_fired,
    default_policies,
    evaluate_all,
    evaluate_policy,
)
from slobudget.objective import Objective
from slobudget.sli import load_series, parse_series


class DefaultPolicyTests(unittest.TestCase):
    def test_pair_present(self):
        names = [p.name for p in default_policies()]
        self.assertEqual(names, ["fast-burn", "slow-burn"])


class EvaluateTests(unittest.TestCase):
    def setUp(self):
        self.series = load_series("samples/service-a.sli")
        self.objective = Objective(target=0.999, window_seconds=30 * 86400)

    def test_fast_burn_fires_on_incident(self):
        evals = evaluate_all(self.series, self.objective)
        fast = next(e for e in evals if e.policy.name == "fast-burn")
