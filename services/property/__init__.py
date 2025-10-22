#!/usr/bin/env python3
"""
Property Services Module

Property management and auditing services.
Part of system consolidation to organize property functionality.

Services:
- PropertyManager: Unified property lifecycle management
- MaterialAuditor: Comprehensive material auditing system

Last Updated: October 22, 2025
"""

from .property_manager import PropertyManager
from .material_auditor import MaterialAuditor, MaterialAuditResult

__all__ = [
    'PropertyManager',
    'MaterialAuditor',
    'MaterialAuditResult',
]