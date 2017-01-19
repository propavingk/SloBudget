"""Command line interface for slobudget.

Subcommands:

    budget   compute the error budget and how much has been consumed
    burn     burn rates over several windows and a conditional projection
    alerts   evaluate the multi-window fast-burn and slow-burn pair
    version  print the package version

Exit codes: 0 clean, 1 findings present (budget exhausted or an alert fired),
2 usage error. argparse itself exits with 2 on argument errors.
"""

from __future__ import annotations

import argparse
import sys

from . import __version__, alerts, report
from .burn import project_exhaustion, window_stats, burn_rate
from .objective import (
    Objective,
    ObjectiveError,
    parse_objective,
    parse_window,
)
from .sli import SliError, load_series


def _build_objective(args: argparse.Namespace) -> Objective:
    target = parse_objective(args.objective)
    window = parse_window(args.window)
    return Objective(target=target, window_seconds=window)


def _cmd_budget(args: argparse.Namespace) -> int:
    series = load_series(args.series)
    objective = _build_objective(args)
    from .objective import derive_budget

    status = derive_budget(objective, series.total_events, series.total_bad)
