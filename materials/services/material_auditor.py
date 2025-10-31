#!/usr/bin/env python3
"""
Material Auditor - Redirect Module

This module redirects to the canonical material_auditor in services/property/.
The duplicate implementation has been archived.

MIGRATION NOTE: Update your imports to use:
    from shared.services.property.material_auditor import MaterialAuditor

This redirect will be removed in a future release.
"""

# Redirect to canonical implementation
from shared.services.property.material_auditor import *

# Deprecated warning
import warnings
warnings.warn(
    "Importing from materials.services.material_auditor is deprecated. "
    "Use 'from shared.services.property.material_auditor import MaterialAuditor' instead.",
    DeprecationWarning,
    stacklevel=2
)
