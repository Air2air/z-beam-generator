================================================================================
MATERIAL VALUE RANGE ANALYSIS REPORT
================================================================================
Generated: Mon Sep 29 19:40:30 PDT 2025

📊 ANALYSIS SUMMARY
----------------------------------------
Files processed: 121
Total values checked: 1863
Out-of-range values found: 5
Missing range definitions: 1122
Error rate: 0.3%

⚠️  MEDIUM SEVERITY VIOLATIONS (<50% deviation)
--------------------------------------------------
Material: MDF (wood)
Property: tensileStrength (materialProperty)
Issue: Value 15.0 is below minimum 20
Expected range: 20 - 200 MPa
Deviation: -5.00 (-25.0%)
Source: category_ranges

Material: MMCs (composite)
Property: hardness (materialProperty)
Issue: Value 120.0 is above maximum 90
Expected range: 20 - 90 HRC
Deviation: 30.00 (33.3%)
Source: category_ranges

Material: Plaster (masonry)
Property: porosity (materialProperty)
Issue: Value 35.0 is above maximum 25.0
Expected range: 10.0 - 25.0 %
Deviation: 10.00 (40.0%)
Source: chemicalProperties

Material: Hastelloy (metal)
Property: electricalResistivity (materialProperty)
Issue: Value 130.0 is above maximum 100.0
Expected range: 1.0 - 100.0 nΩ·m
Deviation: 30.00 (30.0%)
Source: electricalProperties

Material: Cement (masonry)
Property: porosity (materialProperty)
Issue: Value 28.0 is above maximum 25.0
Expected range: 10.0 - 25.0 %
Deviation: 3.00 (12.0%)
Source: chemicalProperties

📋 ISSUES BY CATEGORY
------------------------------
composite: 1 violations in 1 materials
masonry: 2 violations in 2 materials
metal: 1 violations in 1 materials
wood: 1 violations in 1 materials

📋 ISSUES BY PROPERTY TYPE
-----------------------------------
materialProperty: 5 violations

📋 MOST COMMON VIOLATIONS
-----------------------------------
porosity: 2 violations
tensileStrength: 1 violations
hardness: 1 violations
electricalResistivity: 1 violations