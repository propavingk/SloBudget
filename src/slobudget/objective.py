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
    if not raw:
        raise ObjectiveError("empty window")
    unit = raw[-1]
    if unit.isdigit():
        try:
            seconds = int(raw)
        except ValueError as exc:
            raise ObjectiveError(f"bad window {text!r}") from exc
        if seconds <= 0:
            raise ObjectiveError("window must be positive")
        return seconds
    if unit not in _DURATION_UNITS:
        raise ObjectiveError(
            f"unknown window unit {unit!r} in {text!r}, use one of s m h d w"
        )
    try:
        count = int(raw[:-1])
    except ValueError as exc:
        raise ObjectiveError(f"bad window count in {text!r}") from exc
    if count <= 0:
        raise ObjectiveError("window must be positive")
    return count * _DURATION_UNITS[unit]


def format_duration(seconds: float) -> str:
    """Render a positive duration in seconds as a compact human string.

    Deterministic, no locale, largest sensible unit down to seconds.
    """
    if seconds < 0:
        return "0s"
    total = int(round(seconds))
    parts: list[str] = []
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60), ("s", 1)):
        if total >= size or (unit == "s" and not parts):
