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

