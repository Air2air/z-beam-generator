================================================================================
MATERIALS.YAML ↔ CATEGORIES.YAML SYNCHRONIZATION REPORT
================================================================================

❌ VALIDATION FAILED - 5 issues found

SUMMARY:
  Missing in Categories: 5
  Out of Range Values: 0
  Range Updates Needed: 0
  Orphaned Properties: 0
  Subcategory Issues: 74

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
⚠️  SUBCATEGORY ASSIGNMENT ISSUES
================================================================================

Materials with missing or incorrect subcategory assignments.

Material: Aluminum (metal)
Issue: missing_subcategory
Expected: non_ferrous
Action: Add subcategory: non_ferrous

Material: Chromium (metal)
Issue: missing_subcategory
Expected: specialty
Action: Add subcategory: specialty

Material: Manganese (metal)
Issue: missing_subcategory
Expected: ferrous
Action: Add subcategory: ferrous

Material: Beryllium (metal)
Issue: missing_subcategory
Expected: specialty
Action: Add subcategory: specialty

Material: Brass (metal)
Issue: missing_subcategory
Expected: non_ferrous
Action: Add subcategory: non_ferrous

Material: Bronze (metal)
Issue: missing_subcategory
Expected: non_ferrous
Action: Add subcategory: non_ferrous

Material: Cobalt (metal)
Issue: missing_subcategory
Expected: specialty
Action: Add subcategory: specialty

Material: Copper (metal)
Issue: missing_subcategory
Expected: non_ferrous
Action: Add subcategory: non_ferrous

Material: Gallium (metal)
Issue: missing_subcategory
Expected: specialty
Action: Add subcategory: specialty

Material: Gold (metal)
Issue: missing_subcategory
Expected: precious
Action: Add subcategory: precious

Material: Hafnium (metal)
Issue: missing_subcategory
Expected: refractory
Action: Add subcategory: refractory

Material: Hastelloy (metal)
Issue: missing_subcategory
Expected: specialty
Action: Add subcategory: specialty

Material: Inconel (metal)
Issue: missing_subcategory
Expected: specialty
Action: Add subcategory: specialty

Material: Indium (metal)
Issue: missing_subcategory
Expected: specialty
Action: Add subcategory: specialty

Material: Iridium (metal)
Issue: missing_subcategory
Expected: precious
Action: Add subcategory: precious

Material: Iron (metal)
Issue: missing_subcategory
Expected: ferrous
Action: Add subcategory: ferrous

Material: Lead (metal)
Issue: missing_subcategory
Expected: non_ferrous
Action: Add subcategory: non_ferrous

Material: Magnesium (metal)
Issue: missing_subcategory
Expected: specialty
Action: Add subcategory: specialty

Material: Molybdenum (metal)
Issue: missing_subcategory
Expected: refractory
Action: Add subcategory: refractory

Material: Nickel (metal)
Issue: missing_subcategory
Expected: specialty
Action: Add subcategory: specialty

... and 54 more

================================================================================
🎯 RECOMMENDED ACTIONS
================================================================================

1. HIGH PRIORITY: Add missing properties to Categories.yaml
   Command: python3 scripts/research_tools/validate_materials_categories_sync.py --auto-fix
