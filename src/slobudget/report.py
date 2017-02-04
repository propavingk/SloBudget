"""Line oriented renderers for the budget, burn, and alerts reports.

Every renderer returns a list of strings, one per output line, so results diff
cleanly in git and are trivial to test. No wall-clock time or randomness enters
the output. Floating point values are formatted with fixed precision so runs
are byte identical.
"""

from __future__ import annotations

