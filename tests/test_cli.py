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
