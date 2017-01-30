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
    for line in report.render_budget(status, series.has_gaps):
        print(line)
    return 1 if status.exhausted else 0


def _cmd_burn(args: argparse.Namespace) -> int:
    series = load_series(args.series)
    objective = _build_objective(args)
    from .objective import derive_budget

    status = derive_budget(objective, series.total_events, series.total_bad)

    # Report a set of windows scaled to the recorded data. The primary window
    # is the whole recorded span, which drives the projection.
    labels = [
        ("1h", 3600),
        ("6h", 21600),
        ("1d", 86400),
        ("all", series.window_seconds),
    ]
    windows = []
    seen: set[int] = set()
    for label, secs in labels:
        if secs <= 0 or secs in seen:
            continue
        seen.add(secs)
        stats = window_stats(series, secs)
        windows.append((label, stats, burn_rate(objective, stats)))

    primary = window_stats(series, series.window_seconds)
    projection = project_exhaustion(objective, primary, status.remaining_events)
    for line in report.render_burn(objective, windows, projection):
        print(line)
    return 1 if status.exhausted else 0


def _cmd_alerts(args: argparse.Namespace) -> int:
    series = load_series(args.series)
    objective = _build_objective(args)
    evaluations = alerts.evaluate_all(series, objective)
    for line in report.render_alerts(evaluations):
        print(line)
    return 1 if alerts.any_fired(evaluations) else 0


def _cmd_version(args: argparse.Namespace) -> int:
    print(f"slobudget {__version__}")
    return 0


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("series", help="path to the indicator series file")
    parser.add_argument(
        "--objective",
