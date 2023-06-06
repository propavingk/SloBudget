"""Burn rate over a window and projection to budget exhaustion.

Burn rate is the observed failure ratio in a window divided by the objective's
allowed failure ratio. A burn rate of 1 spends the budget exactly on schedule
over the compliance window. A burn rate of 10 spends it ten times as fast.

Projection to exhaustion is deliberately conservative. It assumes the current
rate continues unchanged, which is a statement about a hypothetical, not a
prediction. The functions here refuse to project when:

    - the burn rate is zero, because a rate of zero never exhausts anything,
    - the requested window extends past the recorded data, or the recorded
      data has a gap inside the window, because then the rate is computed from
      an incomplete or discontiguous sample.

Callers must treat a projection as conditional on the rate holding.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .objective import Objective
from .sli import Series


class BurnError(ValueError):
    """Raised when a burn rate or projection cannot be computed honestly."""


@dataclass(frozen=True)
class WindowStats:
    """Aggregated counts over the tail window of a series.

    intervals is how many recorded intervals fell in the window. good, total
    and bad are the summed counts. complete is False when the window asked for
    more time than the recorded data covers, or a gap sits inside it.
    """

    seconds: int
    intervals: int
    good: int
    total: int
    bad: int
    complete: bool
    reason: str

    @property
    def failure_ratio(self) -> float:
        if self.total == 0:
            return 0.0
        return self.bad / self.total


def window_stats(series: Series, window_seconds: int) -> WindowStats:
    """Sum the tail of the series covering the most recent window_seconds.

    The window is measured back from the end of the last recorded interval.
    Completeness is reported, not enforced, so callers can decide.
    """
    if window_seconds <= 0:
        raise BurnError("window must be positive")
    if not series.intervals:
        raise BurnError("series has no intervals")

    end = series.intervals[-1].start + timedelta(seconds=series.interval_seconds)
    start_cut = end - timedelta(seconds=window_seconds)

    good = total = bad = count = 0
    for interval in series.intervals:
        if interval.start >= start_cut:
            good += interval.good
            total += interval.total
            bad += interval.bad
            count += 1

    complete = True
    reason = "window fully covered by contiguous data"

    covered_start = series.intervals[0].start
    if start_cut < covered_start:
        complete = False
        reason = (
            "window extends before the first recorded interval, "
            "so the rate is computed from less data than requested"
        )
    else:
        for gap in series.gaps:
            # A gap counts if any missing slot lies at or after the window start.
            if gap.before > start_cut and gap.after >= start_cut - timedelta(
                seconds=series.interval_seconds
            ):
                complete = False
                reason = (
                    f"a gap between {gap.after.isoformat()} and "
                    f"{gap.before.isoformat()} falls inside the window"
                )
                break

    return WindowStats(
        seconds=window_seconds,
        intervals=count,
        good=good,
        total=total,
        bad=bad,
        complete=complete,
        reason=reason,
    )


def burn_rate(objective: Objective, stats: WindowStats) -> float:
    """Burn rate for a window: observed failure ratio over allowed failure ratio.

    A rate of 1 means the window spends budget exactly on pace for the
    compliance window. Zero observed failures give a rate of zero.
    """
    allowed = objective.allowed_failure_ratio
    if allowed <= 0.0:
        raise BurnError("objective allows no failures, burn rate is undefined")
    return stats.failure_ratio / allowed


@dataclass(frozen=True)
class Projection:
    """A conditional projection of time to budget exhaustion.

    can_project is False when the rate is zero or the window is incomplete, and
    then seconds_to_exhaustion is None and reason explains the refusal. When
    can_project is True the projection assumes the current rate holds, which is
    stated in conditional wording by the report layer.
    """

    can_project: bool
    burn_rate: float
    remaining_events: float
    seconds_to_exhaustion: float | None
    reason: str


def project_exhaustion(
    objective: Objective,
    stats: WindowStats,
    remaining_events: float,
) -> Projection:
    """Project when the remaining budget runs out if the window rate continues.

    Refuses to project on a zero burn rate or an incomplete window. The rate of
    bad events per second comes from the window: bad / window_seconds.
    """
    rate = burn_rate(objective, stats)

    if remaining_events <= 0.0:
        return Projection(
            can_project=False,
            burn_rate=rate,
            remaining_events=remaining_events,
            seconds_to_exhaustion=None,
            reason="budget is already exhausted, nothing left to project",
        )
    if rate <= 0.0:
        return Projection(
            can_project=False,
            burn_rate=rate,
            remaining_events=remaining_events,
            seconds_to_exhaustion=None,
            reason="burn rate is zero, the budget is not being spent",
        )
    if not stats.complete:
        return Projection(
            can_project=False,
            burn_rate=rate,
            remaining_events=remaining_events,
            seconds_to_exhaustion=None,
            reason="window is incomplete: " + stats.reason,
        )

    bad_per_second = stats.bad / stats.seconds
    if bad_per_second <= 0.0:
        return Projection(
            can_project=False,
            burn_rate=rate,
            remaining_events=remaining_events,
            seconds_to_exhaustion=None,
            reason="no bad events observed in the window, cannot project",
        )

    seconds = remaining_events / bad_per_second
    return Projection(
        can_project=True,
        burn_rate=rate,
        remaining_events=remaining_events,
        seconds_to_exhaustion=seconds,
        reason="projection assumes the current window rate continues unchanged",
