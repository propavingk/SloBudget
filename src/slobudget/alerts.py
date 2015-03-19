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
