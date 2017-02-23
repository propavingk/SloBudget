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

