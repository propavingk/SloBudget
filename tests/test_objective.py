"""Tests for objective parsing, window parsing, and budget derivation."""

import unittest

from slobudget.objective import (
    Objective,
    ObjectiveError,
    derive_budget,
    format_duration,
