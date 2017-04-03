"""Tests for the sli parser, interval validation, and gap detection."""

import unittest

from slobudget.sli import Gap, SliError, parse_series


HEALTHY = """\
2026-03-01T00:00:00Z,1999,2000
2026-03-01T00:05:00Z,1998,2000
2026-03-01T00:10:00Z,2000,2000
