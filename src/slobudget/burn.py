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
