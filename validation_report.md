# Hierarchical Validation Report
Generated: 2025-09-29T14:40:21.418951

## Overall Status: WARNING

### Categories.yaml: PASSED
### Materials.yaml: PASSED
### Hierarchy Consistency: PASSED
### AI Validation: PASSED
### Frontmatter Files: WARNING

## Issue Summary
- Total Issues: 12
- Critical Issues: 0

## Recommendations
1. Fix invalid property ranges in Categories.yaml

## Detailed Results
ai_cross_validation:
  ai_recommendations: {}
  api_errors:
  - 'AI validation error: ''str'' object has no attribute ''get'''
  categories_validated: 1
  enabled: true
  properties_validated: 0
  validation_issues: []
categories_validation:
  categories_found:
  - ceramic
  - composite
  - glass
  - masonry
  - metal
  - plastic
  - semiconductor
  - stone
  - wood
  file_valid: true
  invalid_ranges:
  - 'ceramic.thermalConductivity: Thermal conductivity range (0.03-2000.0) unrealistic'
  - 'ceramic.thermalDestructionType: Invalid range format'
  - 'composite.thermalDestructionType: Invalid range format'
  - 'glass.thermalDestructionType: Invalid range format'
  - 'masonry.thermalDestructionType: Invalid range format'
  - 'metal.thermalDestructionType: Invalid range format'
  - 'plastic.hardness: Non-numeric range values'
  - 'plastic.thermalDestructionType: Invalid range format'
  - 'semiconductor.thermalDestructionType: Invalid range format'
  - 'stone.thermalDestructionType: Invalid range format'
  - 'wood.thermalDestructionType: Invalid range format'
  issues: []
  missing_ranges: []
  property_ranges_validated:
    ceramic:
      issues:
      - 'ceramic.thermalConductivity: Thermal conductivity range (0.03-2000.0) unrealistic'
      - 'ceramic.thermalDestructionType: Invalid range format'
      properties_checked: 12
      valid: false
    composite:
      issues:
      - 'composite.thermalDestructionType: Invalid range format'
      properties_checked: 12
      valid: false
    glass:
      issues:
      - 'glass.thermalDestructionType: Invalid range format'
      properties_checked: 12
      valid: false
    masonry:
      issues:
      - 'masonry.thermalDestructionType: Invalid range format'
      properties_checked: 12
      valid: false
    metal:
      issues:
      - 'metal.thermalDestructionType: Invalid range format'
      properties_checked: 12
      valid: false
    plastic:
      issues:
      - 'plastic.hardness: Non-numeric range values'
      - 'plastic.thermalDestructionType: Invalid range format'
      properties_checked: 12
      valid: false
    semiconductor:
      issues:
      - 'semiconductor.thermalDestructionType: Invalid range format'
      properties_checked: 12
      valid: false
    stone:
      issues:
      - 'stone.thermalDestructionType: Invalid range format'
      properties_checked: 12
      valid: false
    wood:
      issues:
      - 'wood.thermalDestructionType: Invalid range format'
      properties_checked: 12
      valid: false
frontmatter_validation:
  files_checked: 10
  files_passed: 0
  hierarchy_violations:
  - 'Category mismatch: frontmatter=''Ceramic'', materials=''ceramic'''
  - 'Category mismatch: frontmatter=''Metal'', materials=''metal'''
  - 'Category mismatch: frontmatter=''Wood'', materials=''wood'''
  - 'Category mismatch: frontmatter=''Metal'', materials=''metal'''
  - 'Category mismatch: frontmatter=''Stone'', materials=''stone'''
  - 'Category mismatch: frontmatter=''Wood'', materials=''wood'''
  - 'Category mismatch: frontmatter=''Metal'', materials=''metal'''
  - 'Category mismatch: frontmatter=''Semiconductor'', materials=''semiconductor'''
  - 'Property violation: density = 2.329 (range: 2.33-7.13)'
  - 'Property violation: hardness = 9.5 (range: 2.0-7.0)'
  - 'Category mismatch: frontmatter=''Plastic'', materials=''plastic'''
  - 'Category mismatch: frontmatter=''Masonry'', materials=''masonry'''
  sample_issues: []
hierarchy_consistency:
  category_alignment: {}
  consistent: true
  issues: []
  missing_categories: []
  orphaned_materials: []
  property_coverage:
    ceramic:
      covered: []
      material_properties: []
      schema_properties:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
      uncovered_materials: []
      uncovered_schema:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
    composite:
      covered: []
      material_properties: []
      schema_properties:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
      uncovered_materials: []
      uncovered_schema:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
    glass:
      covered: []
      material_properties: []
      schema_properties:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
      uncovered_materials: []
      uncovered_schema:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
    masonry:
      covered: []
      material_properties: []
      schema_properties:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
      uncovered_materials: []
      uncovered_schema:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
    metal:
      covered: []
      material_properties: []
      schema_properties:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
      uncovered_materials: []
      uncovered_schema:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
    plastic:
      covered: []
      material_properties: []
      schema_properties:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
      uncovered_materials: []
      uncovered_schema:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
    semiconductor:
      covered: []
      material_properties: []
      schema_properties:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
      uncovered_materials: []
      uncovered_schema:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
    stone:
      covered: []
      material_properties: []
      schema_properties:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
      uncovered_materials: []
      uncovered_schema:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
    wood:
      covered: []
      material_properties: []
      schema_properties:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
      uncovered_materials: []
      uncovered_schema:
      - density
      - specificHeat
      - thermalDestructionPoint
      - hardness
      - tensileStrength
      - thermalConductivity
      - thermalDestructionType
      - thermalExpansion
      - laserAbsorption
      - youngsModulus
      - thermalDiffusivity
      - laserReflectivity
materials_validation:
  category_mismatches: []
  file_valid: true
  issues: []
  materials_validated: 121
  missing_properties: []
  property_violations: []
