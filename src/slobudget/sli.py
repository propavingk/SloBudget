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
    slots that have no data.
    """

    after: datetime
    before: datetime
    missing: int


@dataclass(frozen=True)
class Series:
    """A parsed indicator series.

    interval_seconds is the fixed step between interval starts. intervals are
    sorted by start time. gaps lists every detected discontinuity.
    """

    interval_seconds: int
    intervals: tuple[Interval, ...]
    gaps: tuple[Gap, ...]

    @property
    def has_gaps(self) -> bool:
        return len(self.gaps) > 0

    @property
    def total_good(self) -> int:
        return sum(i.good for i in self.intervals)

    @property
    def total_events(self) -> int:
        return sum(i.total for i in self.intervals)

    @property
    def total_bad(self) -> int:
        return sum(i.bad for i in self.intervals)

    @property
    def window_seconds(self) -> int:
        """Wall clock span the recorded data would cover if it had no gaps.

        This counts one interval per recorded row, so it is the covered time,
        not the span from first to last timestamp.
        """
        return self.interval_seconds * len(self.intervals)

    def span_seconds(self) -> int:
        """Seconds from the first interval start to the end of the last one."""
        if not self.intervals:
            return 0
        first = self.intervals[0].start
        last = self.intervals[-1].start
        return int((last - first).total_seconds()) + self.interval_seconds


def _parse_timestamp(raw: str, line_no: int) -> datetime:
    text = raw.strip()
    # Accept a trailing Z as UTC, which datetime.fromisoformat rejects before 3.11
    # in some builds. Normalise it to +00:00 for portability.
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SliError(f"line {line_no}: bad timestamp {raw!r}: {exc}") from exc
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def parse_series(text: str) -> Series:
    """Parse indicator series text into a validated Series.
