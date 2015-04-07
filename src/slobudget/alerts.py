"""Multi-window burn rate alerting.

A single window burn rate alert is a trade off. A short window reacts fast but
flaps on brief spikes. A long window is stable but slow to fire. The multi
window approach used by the Google SRE workbook pairs a long window with a
short one: the long window sets the sensitivity, and the short window confirms
the burn is still happening right now, which suppresses alerts on incidents
that already recovered.

This module evaluates the standard fast-burn and slow-burn pair against a
recorded series by sliding both windows across every interval boundary and
reporting the first boundary where the condition held.

Default conditions, expressed as burn rate thresholds over (long, short)
window pairs for a 30 day compliance window:

    fast burn:  long 1h and short 5m, threshold 14.4
    slow burn:  long 6h and short 30m, threshold 6.0

A threshold of 14.4 over 1 hour burns 2 percent of a 30 day budget in that
hour, which is the workbook's page worthy fast burn. 6.0 over 6 hours burns
5 percent, the slower ticket worthy burn. Both require the short window to also
exceed the threshold, so a recovered incident stops firing.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from .burn import burn_rate, window_stats
from .objective import Objective
from .sli import Series


@dataclass(frozen=True)
class AlertPolicy:
    """One multi-window burn rate alert definition.

    name is a short label. long_seconds and short_seconds are the two window
    lengths. threshold is the burn rate both windows must exceed to fire.
    budget_fraction records the share of budget the long window would burn at
    the threshold, for documentation in the report.
    """

    name: str
    long_seconds: int
    short_seconds: int
    threshold: float
    budget_fraction: float


def default_policies() -> tuple[AlertPolicy, ...]:
    """The standard fast-burn and slow-burn pair for a 30 day window."""
    return (
        AlertPolicy(
            name="fast-burn",
            long_seconds=3600,
            short_seconds=300,
            threshold=14.4,
            budget_fraction=0.02,
        ),
        AlertPolicy(
            name="slow-burn",
            long_seconds=21600,
            short_seconds=1800,
            threshold=6.0,
            budget_fraction=0.05,
        ),
    )


@dataclass(frozen=True)
class AlertEvaluation:
    """The result of evaluating one policy against a series.

    fired is True when the condition held at some boundary. fired_at is the
    interval end timestamp of the first firing, or None. long_rate and
    short_rate are the burn rates at that boundary. skipped is True when the
    series is too short to hold either window, with reason set.
    """

    policy: AlertPolicy
    fired: bool
    fired_at: datetime | None
    long_rate: float | None
    short_rate: float | None
    skipped: bool
    reason: str


def _rate_ending_at(
    series: Series,
    objective: Objective,
    boundary_end: datetime,
    window_seconds: int,
) -> tuple[float, bool]:
    """Burn rate for the window ending exactly at boundary_end.

    Returns (rate, complete). Builds a synthetic tail-limited view by summing
    intervals whose start lies in [boundary_end - window, boundary_end).
    """
    start_cut = boundary_end - timedelta(seconds=window_seconds)
    good = total = bad = count = 0
    for interval in series.intervals:
        if start_cut <= interval.start < boundary_end:
            good += interval.good
            total += interval.total
            bad += interval.bad
            count += 1
    failure_ratio = 0.0 if total == 0 else bad / total
    allowed = objective.allowed_failure_ratio
    rate = 0.0 if allowed <= 0 else failure_ratio / allowed
    # Complete when the window start is at or after the first recorded interval
    # and the number of covered intervals matches the window length exactly.
    expected = window_seconds // series.interval_seconds
    complete = (
        start_cut >= series.intervals[0].start and count == expected and expected > 0
    )
    return rate, complete

