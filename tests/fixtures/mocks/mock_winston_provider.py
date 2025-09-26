#!/usr/bin/env python3
"""
Mock Winston Provider

DISABLED - AIDetectionConfig and related components have been removed.
"""

import pytest

# Skip all tests in this file since AI detection components don't exist
pytestmark = pytest.mark.skip(reason="AIDetectionConfig and text components have been removed")

# File is disabled - all mock classes removed to prevent collection errors
