"""Tests for compatibility with other flake8 plugins."""

import re
from collections import defaultdict
import subprocess
from unittest import TestCase
import os
from typing import (
    Dict,
    Iterable,
    Set,
)

ERROR = re.compile(r'\[A-Z]{1,3}\d{3}')


class CompatibilityTest(TestCase):
    """A simple compatibility test for Darglint.

    Currently, this test only checks for the presence of certain
    errors which we know to be present.  Ideally, we would run
    the test against a set of repositories, record the errors found,
    and make sure the same errors are found when run along with darglint.
    That may not be easy, though, since flake8 doesn't seem to have a
    command-line option to disable a particular extension.

    """

    def create_darglint_setup(self):
        try:
            with open('.darglint', 'w') as fout:
                fout.write('[darglint]\n')
        except Exception:
            # Do Nothing.
            pass

    def create_no_darglint_setup(self):
        try:
            with open('.darglint', 'w') as fout:
                fout.write('[darglint]\nignore=*\n')
        except Exception:
            # Do Nothing.
            pass

    @classmethod
    def tearDownClass(cls):
        try:
            os.remove('.darglint')
        except Exception:
            # Do Nothing.
            pass

    def yield_modules(self):
        # type: () -> Iterable[str]
        for path, folders, filenames in os.walk('integration_tests/repos'):
            for filename in filenames:
                if not filename.endswith('.py'):
                    continue
                yield os.path.join(path, filename)

    def record_errors(self, collection, filename):
        # type: (Dict[str, Set[str]], str) -> None
        proc = subprocess.run([
            'flake8',
            '--isolated',
            '--enable-extensions=TRUE',
            filename,
        ], stdout=subprocess.PIPE)
        result = proc.stdout.decode('utf8')
        errors = ERROR.findall(result)
        collection[filename] |= set(errors)

    def test_with_darglint_is_superset(self):
        errors = defaultdict(lambda: set())  # type: Dict[str, Set[str]]
        self.create_no_darglint_setup()
        for filename in self.yield_modules():
            self.record_errors(errors, filename)

        errors_with = defaultdict(lambda: set())  # type: Dict[str, Set[str]]  # noqa: E501
        self.create_darglint_setup()
        for filename in self.yield_modules():
            self.record_errors(errors_with, filename)

        for filename in errors.keys():
            self.assertTrue(
                len(errors[filename] - errors_with[filename]) == 0,
            )
