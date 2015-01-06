"""Objective parsing and error budget derivation.

An objective is a target success ratio, for example 99.9 percent. The
compliance window is the span over which that objective is measured, for
example 30 days. From those two the total error budget follows directly:

    budget_events = (1 - objective) * expected_total_events

We express the budget as a fraction of events, because the indicator series
counts events, not time. The tool reports both the budget as a ratio and, when
a series is supplied, the budget consumed by the observed bad events.
"""

from __future__ import annotations

from dataclasses import dataclass


