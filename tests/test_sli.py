"""Tests for the sli parser, interval validation, and gap detection."""

import unittest

from slobudget.sli import Gap, SliError, parse_series


HEALTHY = """\
2026-03-01T00:00:00Z,1999,2000
2026-03-01T00:05:00Z,1998,2000
2026-03-01T00:10:00Z,2000,2000
"""


class ParseSeriesTests(unittest.TestCase):
    def test_parses_basic_series(self):
        series = parse_series(HEALTHY)
        self.assertEqual(series.interval_seconds, 300)
        self.assertEqual(len(series.intervals), 3)
        self.assertEqual(series.total_events, 6000)
        self.assertEqual(series.total_good, 5997)
        self.assertEqual(series.total_bad, 3)
        self.assertFalse(series.has_gaps)

    def test_ignores_comments_and_blank_lines(self):
        text = "# header\n\n" + HEALTHY + "\n# trailing\n"
        series = parse_series(text)
        self.assertEqual(len(series.intervals), 3)

    def test_window_and_span_seconds(self):
        series = parse_series(HEALTHY)
        # three intervals of 300s covered
        self.assertEqual(series.window_seconds, 900)
        # first start to end of last interval
        self.assertEqual(series.span_seconds(), 900)

    def test_accepts_offset_timestamps(self):
        text = (
            "2026-03-01T00:00:00+00:00,1,2\n"
            "2026-03-01T00:05:00+00:00,1,2\n"
        )
        series = parse_series(text)
        self.assertEqual(series.interval_seconds, 300)

    def test_sorts_out_of_order_rows(self):
        text = (
            "2026-03-01T00:10:00Z,2000,2000\n"
            "2026-03-01T00:00:00Z,1999,2000\n"
            "2026-03-01T00:05:00Z,1998,2000\n"
        )
        series = parse_series(text)
