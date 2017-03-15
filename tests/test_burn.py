"""Tests for burn rate over a window and conditional projection."""

import unittest

from slobudget.burn import burn_rate, project_exhaustion, window_stats
from slobudget.objective import Objective, derive_budget
from slobudget.sli import parse_series


def _series(rows):
