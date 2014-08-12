"""Parse and validate a service level indicator (SLI) series.

Input format is line oriented so it diffs cleanly in git. Each data row is:

    <iso8601-utc-timestamp>,<good>,<total>

Blank lines and lines beginning with '#' are ignored. The timestamp marks the
start of a fixed length interval. Every interval must have the same duration,
inferred from the first two rows. A gap is any place where the observed step
between consecutive timestamps is not equal to that inferred interval.

The parser does no network access and no wall-clock reads. Given identical
bytes it produces an identical Series.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


class SliError(ValueError):
    """Raised when the indicator series cannot be parsed or is invalid."""


@dataclass(frozen=True)
class Interval:
    """One measured interval of the indicator series.

    start is a timezone aware UTC datetime marking the interval start.
    good is the count of good events, total is the count of all events.
    """

    start: datetime
    good: int
    total: int

    @property
    def bad(self) -> int:
        return self.total - self.good

    @property
    def failure_ratio(self) -> float:
        """Fraction of events in this interval that were bad, in [0, 1]."""
        if self.total == 0:
            return 0.0
        return self.bad / self.total


@dataclass(frozen=True)
class Gap:
    """A missing stretch between two recorded intervals.

    after is the timestamp of the interval just before the gap, before is the
    timestamp of the next recorded interval. missing is the count of interval
