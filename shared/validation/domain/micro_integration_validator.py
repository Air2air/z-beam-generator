"""
Backward-compat shim — implementation at shared.validation.core.content

Date: February 23, 2026
"""

from shared.validation.core.content import MicroIntegrationValidator
from shared.validation.errors import ValidationResult

__all__ = ['MicroIntegrationValidator', 'ValidationResult']
