================================================================================
MATERIALS.YAML ↔ CATEGORIES.YAML SYNCHRONIZATION REPORT
================================================================================

❌ VALIDATION FAILED - 5 issues found

SUMMARY:
  Missing in Categories: 5
  Out of Range Values: 0
  Range Updates Needed: 0
  Orphaned Properties: 0
  Subcategory Issues: 0

================================================================================
❌ CRITICAL: PROPERTIES MISSING IN CATEGORIES.YAML
================================================================================

These properties exist in Materials.yaml but are not defined in Categories.yaml.
ACTION REQUIRED: Add these properties to category_ranges in Categories.yaml

Category: ceramic
Missing Properties: 4
  - compressiveStrength (no numeric values found)
  - flexuralStrength (no numeric values found)
  - fractureToughness (no numeric values found)
  - meltingPoint (no numeric values found)

Category: masonry
Missing Properties: 1
  - compressiveStrength (no numeric values found)

Category: metal
Missing Properties: 3
  - corrosionResistance (no numeric values found)
  - electricalResistivity (no numeric values found)
  - meltingPoint (no numeric values found)

Category: semiconductor
Missing Properties: 1
  - meltingPoint (no numeric values found)

Category: stone
Missing Properties: 1
  - compressiveStrength (no numeric values found)

================================================================================
🎯 RECOMMENDED ACTIONS
================================================================================

1. HIGH PRIORITY: Add missing properties to Categories.yaml
   Command: python3 scripts/research_tools/validate_materials_categories_sync.py --auto-fix
