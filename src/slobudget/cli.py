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
