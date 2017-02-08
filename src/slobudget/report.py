"""Line oriented renderers for the budget, burn, and alerts reports.

Every renderer returns a list of strings, one per output line, so results diff
cleanly in git and are trivial to test. No wall-clock time or randomness enters
the output. Floating point values are formatted with fixed precision so runs
are byte identical.
"""

from __future__ import annotations

from .alerts import AlertEvaluation
from .burn import Projection, WindowStats
from .objective import BudgetStatus, Objective, format_duration


def _pct(value: float) -> str:
    """Format a ratio as a percentage with three decimals."""
    return f"{value * 100:.3f}%"


def _ratio(value: float) -> str:
    return f"{value:.6f}"


def render_budget(status: BudgetStatus, has_gaps: bool) -> list[str]:
    """Render the budget accounting report."""
    obj = status.objective
    lines: list[str] = []
    lines.append("error budget report")
    lines.append(f"  objective            {_pct(obj.target)} success")
