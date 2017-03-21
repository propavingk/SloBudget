"""End to end tests for the CLI, including exit codes against the samples."""

import io
import unittest
from contextlib import redirect_stdout, redirect_stderr

from slobudget.cli import main
