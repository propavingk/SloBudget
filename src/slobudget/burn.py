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
