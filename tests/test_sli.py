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
        starts = [i.start.strftime("%H:%M") for i in series.intervals]
        self.assertEqual(starts, ["00:00", "00:05", "00:10"])


class GapTests(unittest.TestCase):
    def test_detects_single_gap(self):
        text = (
            "2026-03-01T00:00:00Z,1,2\n"
            "2026-03-01T00:05:00Z,1,2\n"
            "2026-03-01T00:20:00Z,1,2\n"  # skips 00:10 and 00:15
        )
        series = parse_series(text)
        self.assertTrue(series.has_gaps)
        self.assertEqual(len(series.gaps), 1)
        gap = series.gaps[0]
        self.assertIsInstance(gap, Gap)
        self.assertEqual(gap.missing, 2)


class ValidationTests(unittest.TestCase):
    def test_rejects_good_over_total(self):
        text = "2026-03-01T00:00:00Z,3,2\n2026-03-01T00:05:00Z,1,2\n"
        with self.assertRaises(SliError):
            parse_series(text)

    def test_rejects_negative_counts(self):
        text = "2026-03-01T00:00:00Z,-1,2\n2026-03-01T00:05:00Z,1,2\n"
        with self.assertRaises(SliError):
            parse_series(text)

    def test_rejects_wrong_field_count(self):
        with self.assertRaises(SliError):
            parse_series("2026-03-01T00:00:00Z,1\n2026-03-01T00:05:00Z,1,2\n")

    def test_rejects_single_row(self):
        with self.assertRaises(SliError):
            parse_series("2026-03-01T00:00:00Z,1,2\n")

    def test_rejects_empty(self):
        with self.assertRaises(SliError):
            parse_series("# only a comment\n")

    def test_rejects_duplicate_timestamp(self):
        text = "2026-03-01T00:00:00Z,1,2\n2026-03-01T00:00:00Z,1,2\n"
        with self.assertRaises(SliError):
            parse_series(text)

    def test_rejects_non_multiple_step(self):
        text = (
            "2026-03-01T00:00:00Z,1,2\n"
            "2026-03-01T00:05:00Z,1,2\n"
            "2026-03-01T00:12:00Z,1,2\n"  # 420s, not a multiple of 300
        )
        with self.assertRaises(SliError):
            parse_series(text)


if __name__ == "__main__":
    unittest.main()
