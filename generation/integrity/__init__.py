"""
System Integrity Module
=======================

Pre-generation health checks to ensure end-to-end system cohesion.

This module verifies:
- Configuration value mapping accuracy (1-10 scale normalization)
- Parameter propagation through the processing chain
- API connectivity and health (Winston, Grok)
- Documentation-to-code alignment
- Test coverage and validity
"""

from .integrity_checker import IntegrityChecker, IntegrityStatus, IntegrityResult

__all__ = ['IntegrityChecker', 'IntegrityStatus', 'IntegrityResult']
