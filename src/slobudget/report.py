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
    lines.append(f"  compliance window    {format_duration(obj.window_seconds)}")
    lines.append(f"  allowed failure      {_pct(obj.allowed_failure_ratio)}")
    lines.append(f"  total events         {status.total_events}")
    lines.append(f"  bad events           {status.bad_events}")
    lines.append(f"  observed failure     {_pct(status.observed_failure_ratio)}")
    lines.append(f"  budget (events)      {status.budget_events:.3f}")
    lines.append(f"  budget consumed      {_pct(status.consumed_fraction)}")
    lines.append(f"  budget remaining     {_pct(status.remaining_fraction)}")
    lines.append(f"  remaining events     {status.remaining_events:.3f}")
    if has_gaps:
        lines.append("  note                 series has gaps, totals cover recorded data only")
    if status.exhausted:
        lines.append("  status               EXHAUSTED, budget is spent")
    else:
        lines.append("  status               within budget")
    return lines


def render_burn(
