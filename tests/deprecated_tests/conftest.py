# This directory contains deprecated tests that are no longer maintained
# They reference modules that have been removed or refactored
# Pytest should not collect tests from this directory

import pytest

collect_ignore_glob = ["*.py"]
