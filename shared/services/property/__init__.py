#!/usr/bin/env python3
"""
Property Services Module

Property management and auditing services.
Part of system consolidation to organize property functionality.

Services:
- PropertyManager: Unified property lifecycle management (now in components/frontmatter/services/)
- MaterialAuditor: Comprehensive material auditing system

Last Updated: October 30, 2025 - Removed PropertyManager (moved to components/frontmatter/services/)
"""

# PropertyManager moved to components/frontmatter/services/property_manager.py
# Import from there if needed, or use redirect wrapper below
from .material_auditor import MaterialAuditor, MaterialAuditResult

__all__ = [
    'MaterialAuditor',
    'MaterialAuditResult',
]