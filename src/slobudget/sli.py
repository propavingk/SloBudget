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
