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


