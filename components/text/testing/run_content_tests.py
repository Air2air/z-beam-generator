#!/usr/bin/env python3
"""
Content Component Test Suite Runner

Orchestrates all content generation tests following CLAUDE_INSTRUCTIONS.md principles.
Fail-fast architecture with comprehensive validation and no mocks in production.
"""

import logging
import sys
import time
from pathlib import Path
import unittest

import pytest

from components.text.testing.test_persona_validation import (
from components.text.testing.test_silicon_nitride_case_study import (
from components.text.testing.test_technical_content_validation import (
from components.text.testing.test_content_end_to_end_updated import (
import traceback


        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
