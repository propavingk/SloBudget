"""End to end tests for the CLI, including exit codes against the samples."""

import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

from slobudget.cli import main


def run(argv):
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class VersionTests(unittest.TestCase):
    def test_version(self):
        code, out, _ = run(["version"])
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("slobudget "))


class BudgetCommandTests(unittest.TestCase):
    def test_within_budget_exit_zero(self):
        code, out, _ = run(
            ["budget", "samples/service-a.sli", "-o", "98", "-w", "30d"]
        )
        self.assertEqual(code, 0)
        self.assertIn("budget remaining", out)
        self.assertIn("within budget", out)

    def test_exhausted_exit_one(self):
        code, out, _ = run(
            ["budget", "samples/service-a.sli", "-o", "99.9", "-w", "30d"]
        )
        self.assertEqual(code, 1)
        self.assertIn("EXHAUSTED", out)


class BurnCommandTests(unittest.TestCase):
    def test_burn_runs(self):
        code, out, _ = run(
            ["burn", "samples/service-a.sli", "-o", "98", "-w", "30d"]
        )
        self.assertEqual(code, 0)
        self.assertIn("burn rate report", out)
        self.assertIn("projection", out)

    def test_burn_refuses_projection_on_gap(self):
