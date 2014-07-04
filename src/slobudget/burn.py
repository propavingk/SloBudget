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
