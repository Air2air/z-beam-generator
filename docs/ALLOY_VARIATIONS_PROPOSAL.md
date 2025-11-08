# Material Alloy & Composition Variations Proposal

**Version**: 1.0.0  
**Date**: November 7, 2024  
**Purpose**: Define alloy and composition variations for deep research data population

---

## Overview

This document proposes specific alloy and composition variations for each material in the Z-Beam system. These variations will be populated in `PropertyResearch.yaml` to enable drill-down pages showing how properties vary across alloys.

---

## Aluminum Alloys

### Pure Aluminum
- **Designation**: Al 99.99, 1050, 1100
- **Purity**: 99.0% - 99.99% Al
- **Applications**: Chemical equipment, food industry, electrical conductors
- **Key Properties**: 
  - Highest thermal/electrical conductivity
  - Lowest strength
  - Excellent corrosion resistance
  - Density: ~2.70 g/cm³
- **Laser Cleaning**: Easiest to clean, lowest power requirements

### 2xxx Series (Copper Alloys)
- **2024-T3** (Aircraft Grade)
  - Composition: Al-4.4Cu-1.5Mg-0.6Mn
  - Applications: Aircraft structures, rivets
  - Density: ~2.78 g/cm³
  - Thermal conductivity: ~120 W/(m·K)
  - Laser cleaning: Moderate difficulty, watch for Cu oxidation

### 6xxx Series (Structural)
- **6061-T6** (General Purpose)
  - Composition: Al-1.0Mg-0.6Si-0.3Cu
  - Applications: Marine, automotive, structural
  - Density: ~2.70 g/cm³
  - Thermal conductivity: ~167 W/(m·K)
  - Laser cleaning: Standard parameters, most common

- **6063-T5** (Architectural)
  - Composition: Al-0.7Mg-0.4Si
  - Applications: Extrusions, window frames
  - Density: ~2.69 g/cm³
  - Lower strength than 6061

### 7xxx Series (High Strength)
- **7075-T6** (Aerospace)
  - Composition: Al-5.6Zn-2.5Mg-1.6Cu
  - Applications: Aircraft, high-stress parts
  - Density: ~2.81 g/cm³
  - Thermal conductivity: ~130 W/(m·K)
  - Laser cleaning: Higher power needed, watch for cracking

---

## Steel Alloys

### Carbon Steel
- **Mild Steel / Low Carbon (< 0.3% C)**
  - Examples: AISI 1020, A36
  - Applications: Structural, general fabrication
  - Density: ~7.85 g/cm³
  - Laser absorption: High (~90% at 1064nm)
  - Laser cleaning: Standard, prone to rust post-cleaning

- **Medium Carbon (0.3-0.6% C)**
  - Examples: AISI 1045, 4140
  - Applications: Machinery, shafts, gears
  - Higher hardness than low carbon
  - Laser cleaning: Higher fluence needed

- **High Carbon (0.6-1.4% C)**
  - Examples: AISI 1095, tool steels
  - Applications: Cutting tools, springs
  - Laser cleaning: Risk of hardening/tempering changes

### Stainless Steel
- **304 (18-8 Austenitic)**
  - Composition: Fe-18Cr-8Ni
  - Applications: Food, medical, architectural
  - Density: ~8.00 g/cm³
  - Thermal conductivity: ~16 W/(m·K) (low!)
  - Laser cleaning: Excellent results, passivation layer forms

- **316 (Marine Grade)**
  - Composition: Fe-18Cr-10Ni-2Mo
  - Applications: Marine, chemical processing
  - Similar to 304 but better corrosion resistance
  - Laser cleaning: Similar to 304

- **430 (Ferritic)**
  - Composition: Fe-17Cr
  - Applications: Automotive trim, appliances
  - Lower cost than 304
  - Magnetic (unlike 304/316)

### Tool Steel
- **D2 (High Carbon, High Chrome)**
  - Composition: Fe-1.5C-12Cr-1Mo-1V
  - Applications: Cutting tools, dies
  - Very hard (HRC 58-62 after hardening)
  - Laser cleaning: Risk of thermal damage to hardness

- **A2 (Air Hardening)**
  - Composition: Fe-1.0C-5Cr-1Mo-1V
  - Applications: Punches, dies, cutting tools
  - Medium wear resistance

---

## Stainless Steel (Expanded)

### Austenitic (300 Series)
- **301**: Higher strength, lower corrosion resistance
- **304L**: Low carbon version (< 0.03% C), better weldability
- **310**: High temperature applications (heat resistant)
- **316L**: Low carbon version for welding

### Ferritic (400 Series)
- **409**: Automotive exhaust systems
- **430**: Appliances, trim
- **446**: High temperature oxidation resistance

### Martensitic
- **410**: Cutlery, valve trim (hardenable)
- **420**: Surgical instruments, knife blades
- **440C**: Highest hardness stainless

---

## Titanium Alloys

### Commercially Pure (CP)
- **Grade 1** (99.5% Ti)
  - Lowest strength, highest ductility
  - Applications: Chemical processing
  - Density: ~4.51 g/cm³
  - Laser cleaning: Low power, high absorption

- **Grade 2** (99.2% Ti)
  - Most common CP grade
  - Good balance of properties
  - Applications: Aerospace, medical implants

- **Grade 4**
  - Highest strength CP titanium
  - Applications: Airframes, power plant condensers

### Alpha-Beta Alloys
- **Grade 5 (Ti-6Al-4V)**
  - Composition: Ti-6Al-4V
  - Most common titanium alloy (50% of Ti market)
  - Applications: Aerospace, medical, automotive
  - Density: ~4.43 g/cm³
  - Thermal conductivity: ~7.2 W/(m·K)
  - Laser cleaning: Standard parameters for titanium

- **Ti-6Al-2Sn-4Zr-2Mo** (Ti-6242)
  - High temperature applications
  - Aircraft engines

---

## Copper Alloys

### Pure Copper
- **C11000 (Electrolytic Tough Pitch)**
  - 99.9% Cu
  - Highest electrical conductivity
  - Density: ~8.96 g/cm³
  - Thermal conductivity: ~401 W/(m·K)
  - Laser cleaning: High reflectivity challenge

### Brass (Cu-Zn)
- **C26000 (Cartridge Brass, 70/30)**
  - Composition: 70% Cu, 30% Zn
  - Applications: Cartridge cases, plumbing
  - Density: ~8.53 g/cm³
  - Thermal conductivity: ~125 W/(m·K)
  - Laser cleaning: Zn vaporization concern

- **C36000 (Free Cutting Brass)**
  - Composition: 61.5% Cu, 35.5% Zn, 3% Pb
  - Applications: Machined parts
  - Laser cleaning: Lead concerns

### Bronze (Cu-Sn)
- **C51000 (Phosphor Bronze)**
  - Composition: 95% Cu, 5% Sn, traces P
  - Applications: Springs, bearings
  - Density: ~8.86 g/cm³
  - Laser cleaning: Standard parameters

- **C52100 (High Phosphor Bronze)**
  - 8% Sn for higher strength
  - Applications: Heavy-duty bearings

### Copper-Nickel
- **C70600 (90/10 Cupronickel)**
  - Composition: 90% Cu, 10% Ni
  - Applications: Marine condensers, seawater piping
  - Excellent corrosion resistance

---

## Nickel Alloys

### Pure Nickel
- **Nickel 200/201**
  - 99% Ni minimum
  - Applications: Caustic environments
  - Density: ~8.89 g/cm³
  - Laser cleaning: High melting point, moderate difficulty

### Nickel-Based Superalloys
- **Inconel 600**
  - Composition: Ni-15Cr-8Fe
  - Applications: Furnaces, heat exchangers
  - Laser cleaning: High power required

- **Inconel 625**
  - Composition: Ni-22Cr-9Mo-3.5Nb
  - Applications: Aerospace, chemical processing
  - Exceptional corrosion resistance

- **Inconel 718**
  - Composition: Ni-19Cr-18Fe-5Nb-3Mo
  - Applications: Turbine blades, rocket engines
  - Age hardenable

---

## Brass (Expanded Detail)

### Alpha Brasses (< 37% Zn)
- **Gilding Metal (C21000)**: 5% Zn - coins, bullets
- **Commercial Bronze (C22000)**: 10% Zn - grillwork
- **Red Brass (C23000)**: 15% Zn - plumbing

### Alpha-Beta Brasses (37-45% Zn)
- **Muntz Metal (C28000)**: 40% Zn - marine hardware
- **Naval Brass (C46400)**: 39.25% Zn + 1% Sn - marine applications

---

## Bronze (Expanded Detail)

### Tin Bronzes
- **C90700 (Tin Bronze)**: 88% Cu, 10% Sn, 2% Zn - bearings
- **C93200 (Bearing Bronze)**: 83% Cu, 7% Sn, 7% Pb, 3% Zn

### Aluminum Bronze
- **C95400**: 85% Cu, 11% Al, 4% Fe - marine propellers
- Very high strength and corrosion resistance

---

## Zinc Alloys

### Die-Cast Alloys
- **Zamak 3 (Zinc Alloy 3)**
  - Composition: Zn-4Al-0.04Mg
  - Applications: Die castings, hardware
  - Density: ~6.6 g/cm³
  - Laser cleaning: Low melting point risk

- **Zamak 5**
  - Higher copper content
  - Better creep resistance

---

## Magnesium Alloys

### Cast Alloys
- **AZ91D**
  - Composition: Mg-9Al-1Zn
  - Most common magnesium alloy
  - Density: ~1.81 g/cm³ (lightest structural metal)
  - Laser cleaning: Fire risk - extreme caution

### Wrought Alloys
- **AZ31B**
  - Composition: Mg-3Al-1Zn
  - Applications: Aerospace, electronics
  - Good formability

---

## Cast Iron

### Gray Cast Iron
- **Class 20/30/40**
  - Composition: Fe-3.5C-2.5Si (graphite flakes)
  - Applications: Engine blocks, machinery bases
  - Density: ~7.2 g/cm³
  - Laser cleaning: Graphite absorption aids cleaning

### Ductile Iron (Nodular)
- **65-45-12, 80-55-06**
  - Graphite in nodular form
  - Higher strength than gray iron
  - Laser cleaning: Similar to gray iron

---

## Lead Alloys

### Pure Lead
- **99.9% Pb**
  - Applications: Radiation shielding, batteries
  - Density: ~11.34 g/cm³
  - Laser cleaning: Vaporization toxicity concerns

### Lead Alloys
- **Lead-Antimony**: Battery grids
- **Lead-Tin (Solder)**: Electronics
  - Laser cleaning: Environmental/health regulations

---

## Cobalt Alloys

### Cobalt-Chromium
- **Stellite 6**
  - Composition: Co-28Cr-4W-1C
  - Applications: Wear-resistant parts, valve seats
  - Laser cleaning: Very hard, high power needed

---

## Tungsten & Molybdenum

### Pure Tungsten
- **99.95% W**
  - Highest melting point (3422°C)
  - Density: ~19.25 g/cm³
  - Laser cleaning: Extreme parameters needed

### Molybdenum
- **99.95% Mo**
  - High temperature applications
  - Density: ~10.28 g/cm³

---

## Implementation Priority

### Phase 1 (High Priority)
Research these alloys first - most common in laser cleaning applications:
1. **Aluminum**: 1100, 6061-T6, 7075-T6
2. **Steel**: Mild steel (A36), 304 stainless, 316 stainless
3. **Titanium**: Grade 2, Ti-6Al-4V
4. **Copper**: C11000, C26000 brass

### Phase 2 (Medium Priority)
5. **Aluminum**: 2024-T3, 6063-T5
6. **Steel**: 430 stainless, 4140 carbon steel
7. **Copper**: C51000 phosphor bronze
8. **Nickel**: Inconel 625, 718

### Phase 3 (Lower Priority)
9. Tool steels, cast iron, zinc alloys
10. Specialty alloys, high-temp materials

---

## Research Data Required Per Alloy

For EACH alloy variation, populate:

### Material Properties
- **density**: Exact value + source
- **thermalConductivity**: At room temp + temperature variations
- **hardness**: Vickers/Rockwell + heat treatment state
- **meltingPoint**: Solidus/liquidus if applicable
- **thermalExpansion**: Coefficient
- **laserAbsorption**: At common wavelengths (355, 532, 1064, 10640 nm)
- **laserReflectivity**: Complement of absorption

### Laser Cleaning Settings
- **wavelength**: Optimal + alternatives with trade-offs
- **powerRange**: Min/typical/max for different applications
- **fluenceThreshold**: Damage threshold
- **spotSize**: Recommended range
- **scanSpeed**: Based on contamination type

### Citations
- **Handbook references**: ASM, CRC, Materials Handbooks
- **Industry standards**: ISO, ASTM, AA, SAE, AISI
- **Academic sources**: Peer-reviewed papers
- **Manufacturer data**: Alcoa, ThyssenKrupp, etc.

---

## Automation Strategy

Use `populate_deep_research.py` to automate research:

```bash
# Discover alloys for aluminum
python3 scripts/research/populate_deep_research.py --material Aluminum --discover-alloys

# Research density for all aluminum alloys
python3 scripts/research/populate_deep_research.py --material Aluminum --property density

# Research wavelength settings for stainless steel
python3 scripts/research/populate_deep_research.py --material "Stainless Steel" --setting wavelength

# Batch process multiple materials
python3 scripts/research/populate_deep_research.py --materials "Aluminum,Steel,Titanium,Copper" --all-properties
```

---

## Next Steps

1. ✅ **Created**: Alloy variations proposal (this document)
2. 🔄 **Review & Approve**: User validation of alloy list
3. 🔄 **Populate**: Run populate_deep_research.py for Phase 1 materials
4. 🔄 **Validate**: Manual review of AI-generated research
5. 🔄 **Expand**: Add Phase 2 and 3 alloys
6. 🔄 **Build**: Drill-down page templates

---

## Notes

- All alloy designations follow international standards (AA, AISI, ASTM, UNS)
- Laser cleaning implications based on material science principles
- Priority based on industrial laser cleaning usage frequency
- Each alloy adds 7+ property values + 5+ setting variations to research database
