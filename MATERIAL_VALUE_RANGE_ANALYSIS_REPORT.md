================================================================================
MATERIAL VALUE RANGE ANALYSIS REPORT
================================================================================
Generated: Mon Sep 29 12:41:52 PDT 2025

📊 ANALYSIS SUMMARY
----------------------------------------
Files processed: 121
Total values checked: 1351
Out-of-range values found: 26
Missing range definitions: 1357
Error rate: 1.9%

🚨 HIGH SEVERITY VIOLATIONS (>50% deviation)
--------------------------------------------------
Material: Silicon Carbide (semiconductor)
Property: hardness (materialProperty)
Issue: Value 28.0 is above maximum 7
Expected range: 2 - 7 Mohs
Deviation: 21.00 (300.0%)
Source: category_ranges

Material: Silicon Carbide (semiconductor)
Property: youngsModulus (materialProperty)
Issue: Value 410.0 is above maximum 190
Expected range: 5 - 190 GPa
Deviation: 220.00 (115.8%)
Source: category_ranges

Material: Beryllium (metal)
Property: specificHeat (materialProperty)
Issue: Value 1825.0 is above maximum 900
Expected range: 100 - 900 J/kg·K
Deviation: 925.00 (102.8%)
Source: category_ranges

Material: Thermoplastic Elastomer (composite)
Property: tensileStrength (materialProperty)
Issue: Value 15.0 is below minimum 50
Expected range: 50 - 6000 MPa
Deviation: -35.00 (-70.0%)
Source: category_ranges

Material: Onyx (stone)
Property: tensileStrength (materialProperty)
Issue: Value 48.0 is above maximum 25
Expected range: 2 - 25 MPa
Deviation: 23.00 (92.0%)
Source: category_ranges

⚠️  MEDIUM SEVERITY VIOLATIONS (<50% deviation)
--------------------------------------------------
Material: Silicon (semiconductor)
Property: density (materialProperty)
Issue: Value 2.329 is below minimum 2.33
Expected range: 2.33 - 7.13 g/cm³
Deviation: -0.00 (-0.0%)
Source: category_ranges

Material: Silicon (semiconductor)
Property: hardness (materialProperty)
Issue: Value 9.5 is above maximum 7
Expected range: 2 - 7 Mohs
Deviation: 2.50 (35.7%)
Source: category_ranges

Material: Magnesium (metal)
Property: specificHeat (materialProperty)
Issue: Value 1025.0 is above maximum 900
Expected range: 100 - 900 J/kg·K
Deviation: 125.00 (13.9%)
Source: category_ranges

Material: MDF (wood)
Property: tensileStrength (materialProperty)
Issue: Value 15.0 is below minimum 20
Expected range: 20 - 200 MPa
Deviation: -5.00 (-25.0%)
Source: category_ranges

Material: Rhenium (metal)
Property: youngsModulus (materialProperty)
Issue: Value 463.0 is above maximum 411
Expected range: 5 - 411 GPa
Deviation: 52.00 (12.7%)
Source: category_ranges

Material: Zinc (metal)
Property: thermalExpansion (materialProperty)
Issue: Value 30.2 is above maximum 29.1
Expected range: 0.5 - 29.1 µm/m·K
Deviation: 1.10 (3.8%)
Source: category_ranges

Material: Indium (metal)
Property: thermalExpansion (materialProperty)
Issue: Value 32.1 is above maximum 29.1
Expected range: 0.5 - 29.1 µm/m·K
Deviation: 3.00 (10.3%)
Source: category_ranges

Material: Silicon Germanium (semiconductor)
Property: hardness (materialProperty)
Issue: Value 10.5 is above maximum 7
Expected range: 2 - 7 Mohs
Deviation: 3.50 (50.0%)
Source: category_ranges

Material: MMCs (composite)
Property: hardness (materialProperty)
Issue: Value 120.0 is above maximum 90
Expected range: 20 - 90 HRC
Deviation: 30.00 (33.3%)
Source: category_ranges

Material: Ruthenium (metal)
Property: youngsModulus (materialProperty)
Issue: Value 447.0 is above maximum 411
Expected range: 5 - 411 GPa
Deviation: 36.00 (8.8%)
Source: category_ranges

Material: Urethane Composites (composite)
Property: tensileStrength (materialProperty)
Issue: Value 45.0 is below minimum 50
Expected range: 50 - 6000 MPa
Deviation: -5.00 (-10.0%)
Source: category_ranges

Material: Plaster (masonry)
Property: youngsModulus (materialProperty)
Issue: Value 3.8 is below minimum 5
Expected range: 5 - 50 GPa
Deviation: -1.20 (-24.0%)
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

Material: Rubber (composite)
Property: tensileStrength (materialProperty)
Issue: Value 25.0 is below minimum 50
Expected range: 50 - 6000 MPa
Deviation: -25.00 (-50.0%)
Source: category_ranges

Material: Rubber (composite)
Property: specificHeat (materialProperty)
Issue: Value 1900.0 is above maximum 1500
Expected range: 500 - 1500 J/kg·K
Deviation: 400.00 (26.7%)
Source: category_ranges

Material: Rubber (composite)
Property: thermalDiffusivity (materialProperty)
Issue: Value 0.068 is below minimum 0.1
Expected range: 0.1 - 180 mm²/s
Deviation: -0.03 (-32.0%)
Source: category_ranges

Material: Iridium (metal)
Property: youngsModulus (materialProperty)
Issue: Value 528.0 is above maximum 411
Expected range: 5 - 411 GPa
Deviation: 117.00 (28.5%)
Source: category_ranges

Material: Cement (masonry)
Property: porosity (materialProperty)
Issue: Value 28.0 is above maximum 25.0
Expected range: 10.0 - 25.0 %
Deviation: 3.00 (12.0%)
Source: chemicalProperties

Material: Gallium Arsenide (semiconductor)
Property: hardness (materialProperty)
Issue: Value 7.5 is above maximum 7
Expected range: 2 - 7 Mohs
Deviation: 0.50 (7.1%)
Source: category_ranges

Material: Thermoplastic Elastomer (composite)
Property: specificHeat (materialProperty)
Issue: Value 1800.0 is above maximum 1500
Expected range: 500 - 1500 J/kg·K
Deviation: 300.00 (20.0%)
Source: category_ranges

📋 ISSUES BY CATEGORY
------------------------------
composite: 7 violations in 4 materials
masonry: 3 violations in 2 materials
metal: 8 violations in 8 materials
semiconductor: 6 violations in 4 materials
stone: 1 violations in 1 materials
wood: 1 violations in 1 materials

📋 ISSUES BY PROPERTY TYPE
-----------------------------------
materialProperty: 26 violations

📋 MOST COMMON VIOLATIONS
-----------------------------------
hardness: 5 violations
tensileStrength: 5 violations
youngsModulus: 5 violations
specificHeat: 4 violations
thermalExpansion: 2 violations
porosity: 2 violations
density: 1 violations
electricalResistivity: 1 violations
thermalDiffusivity: 1 violations