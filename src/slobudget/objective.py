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


class ObjectiveError(ValueError):
    """Raised when an objective or window string cannot be parsed."""


_DURATION_UNITS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}


def parse_objective(text: str) -> float:
    """Parse an objective such as '99.9', '99.9%' or '0.999' into a ratio.

    Values with a percent sign, or bare values greater than 1, are read as
    percentages. Bare values in (0, 1] are read as ratios. The result is the
    target success ratio in the open interval (0, 1).
    """
    raw = text.strip()
    if not raw:
        raise ObjectiveError("empty objective")
    is_percent = raw.endswith("%")
    if is_percent:
        raw = raw[:-1].strip()
    try:
        value = float(raw)
    except ValueError as exc:
        raise ObjectiveError(f"bad objective {text!r}") from exc
    if is_percent or value > 1.0:
        value = value / 100.0
    if not (0.0 < value < 1.0):
        raise ObjectiveError(
            f"objective must be a ratio in (0, 1), got {value} from {text!r}"
        )
    return value


def parse_window(text: str) -> int:
    """Parse a duration such as '30d', '1h', '2w' into seconds.

    Accepts a single integer count followed by one unit suffix from
    s, m, h, d, w. A bare integer is read as seconds.
    """
    raw = text.strip().lower()
