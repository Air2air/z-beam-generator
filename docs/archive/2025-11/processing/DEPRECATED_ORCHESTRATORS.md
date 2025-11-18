"""
DEPRECATED ORCHESTRATORS - DO NOT USE

The files in this directory (orchestrator.py and generator.py) are DEPRECATED
as of November 15, 2025.

REASON FOR DEPRECATION:
These two files contained ~70% duplicate code implementing essentially the same
workflow. This created maintenance burden, testing complexity, and cognitive overhead.

NEW ARCHITECTURE:
Use processing/unified_orchestrator.py with the adapter pattern:

OLD CODE (deprecated):
    from processing.orchestrator import Orchestrator
    orchestrator = Orchestrator(api_client)
    result = orchestrator.generate(
        material="Aluminum",
        component_type="caption",
        author_id=2,
        length=100
    )

NEW CODE (use this):
    from processing.unified_orchestrator import UnifiedOrchestrator
    from processing.adapters import MaterialsAdapter
    
    adapter = MaterialsAdapter()
    orchestrator = UnifiedOrchestrator(
        api_client=api_client,
        data_adapter=adapter
    )
    result = orchestrator.generate(
        identifier="Aluminum",
        component_type="caption"
    )

BENEFITS OF NEW ARCHITECTURE:
1. Single source of truth (no duplicate logic)
2. Data source abstraction (works with Materials, Regions, Applications, etc.)
3. Winston integration facade (centralized, testable)
4. Better separation of concerns
5. Easier to test and maintain
6. Extensible to new content types

MIGRATION GUIDE:
- Replace Orchestrator → UnifiedOrchestrator
- Replace DynamicGenerator → UnifiedOrchestrator
- Add data adapter (MaterialsAdapter for materials)
- Update parameter names (material → identifier)
- All learning features preserved
- All Winston integration preserved
- All adaptive parameters preserved

These files will be moved to .archive/ in a future cleanup.
"""
