"""
Backfill Generator System

Permanent data population for source YAML files.

Unlike export enrichers (temporary), backfill generators write data
permanently to source YAML files, eliminating repeated enrichment work.

Architecture:
- BaseBackfillGenerator: Abstract base for all backfill generators
- Specific generators: CompoundLinkageBackfill, AuthorBackfill, etc.
- Registry-based discovery and instantiation
- Atomic writes (temp file + rename)
- Dry-run support for testing

Usage:
    python3 run.py --backfill --domain materials
    python3 run.py --backfill --domain materials --generator compound_linkage
    python3 run.py --backfill-all

Implementation Status:
- [x] Base system (Dec 26, 2025)
- [ ] Compound linkage backfill
- [ ] Contaminant linkage backfill
- [ ] Author backfill  
- [ ] Intensity backfill
- [ ] Section metadata backfill
"""

from generation.backfill.base import BaseBackfillGenerator
from generation.backfill.registry import BackfillRegistry

__all__ = ['BaseBackfillGenerator', 'BackfillRegistry']
