# Modular Data Files - Design Specification

**Date**: December 18, 2025  
**Purpose**: Extract duplicate/common data patterns into reusable libraries  
**Impact**: Reduce 75,000+ lines of duplicate data across 424 frontmatter files

---

## 1. Regulatory Standards Library

**File**: `data/regulatory/RegulatoryStandards.yaml`  
**Purpose**: Centralize regulatory standards referenced across materials/settings  
**Current State**: 7 duplicate patterns across 150+ files

### Schema

```yaml
regulatory_standards:
  # ============================================
  # FEDERAL REGULATIONS
  # ============================================
  fda-laser-product-performance:
    id: fda-laser-product-performance
    title: FDA 21 CFR 1040.10 - Laser Product Performance Standards
    short_title: FDA Laser Product Standards
    authority: FDA
    authority_full: Food and Drug Administration
    url: https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040/section-1040.10
    image: /images/logo/logo-org-fda.png
    description: Federal performance standards for all laser products manufactured or imported into the United States
    applicability: All laser cleaning equipment
    compliance_level: mandatory
    effective_date: 1976-08-02
    jurisdiction: United States
    category: product_safety
    
  osha-ppe-requirements:
    id: osha-ppe-requirements
    title: OSHA 29 CFR 1926.95 - Personal Protective Equipment
    short_title: OSHA PPE Requirements
    authority: OSHA
    authority_full: Occupational Safety and Health Administration
    url: https://www.osha.gov/laws-regs/regulations/standardnumber/1926/1926.102
    image: /images/logo/logo-org-osha.png
    description: Federal requirements for personal protective equipment in construction and industrial operations
    applicability: Workplace safety during laser operations
    compliance_level: mandatory
    effective_date: 1971-04-28
    jurisdiction: United States
    category: workplace_safety
  
  # ============================================
  # INTERNATIONAL STANDARDS
  # ============================================
  ansi-laser-safety:
    id: ansi-laser-safety
    title: ANSI Z136.1 - Safe Use of Lasers
    short_title: ANSI Laser Safety Standard
    authority: ANSI
    authority_full: American National Standards Institute
    url: https://webstore.ansi.org/standards/lia/ansiz1362022
    image: /images/logo/logo-org-ansi.png
    description: Comprehensive safety standard for laser operation, maintenance, and safety programs
    applicability: All laser operators and facilities
    compliance_level: recommended
    effective_date: 2022-08-01
    jurisdiction: International (US-origin)
    category: operational_safety
    
  iec-laser-products:
    id: iec-laser-products
    title: IEC 60825 - Safety of Laser Products
    short_title: IEC Laser Product Safety
    authority: IEC
    authority_full: International Electrotechnical Commission
    url: https://webstore.iec.ch/publication/3587
    image: /images/logo/logo-org-iec.png
    description: International standard for laser product safety classification and requirements
    applicability: Laser product manufacturers and importers
    compliance_level: recommended
    effective_date: 2014-05-07
    jurisdiction: International
    category: product_safety
  
  iso-laser-processing:
    id: iso-laser-processing
    title: ISO 11553 - Laser Processing Safety
    short_title: ISO Laser Processing
    authority: ISO
    authority_full: International Organization for Standardization
    url: https://www.iso.org/standard/73827.html
    image: /images/logo/logo-org-iso.png
    description: Safety requirements for laser processing machines and systems
    applicability: Laser processing equipment and facilities
    compliance_level: recommended
    effective_date: 2020-06-01
    jurisdiction: International
    category: equipment_safety
    
  ce-machinery-directive:
    id: ce-machinery-directive
    title: CE Machinery Directive 2006/42/EC
    short_title: CE Machinery Directive
    authority: EU
    authority_full: European Union
    url: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32006L0042
    image: /images/logo/logo-org-eu.png
    description: European requirements for machinery safety including laser equipment
    applicability: Laser equipment sold in EU markets
    compliance_level: mandatory
    effective_date: 2006-05-17
    jurisdiction: European Union
    category: product_safety
    
  uk-laser-regulations:
    id: uk-laser-regulations
    title: UK Laser Safety Regulations 2018
    short_title: UK Laser Regulations
    authority: HSE
    authority_full: Health and Safety Executive
    url: https://www.hse.gov.uk/radiation/lasers/index.htm
    image: /images/logo/logo-org-hse.png
    description: UK-specific laser safety requirements for workplaces
    applicability: UK-based laser operations
    compliance_level: mandatory
    effective_date: 2018-01-01
    jurisdiction: United Kingdom
    category: workplace_safety

# ============================================
# USAGE IN FRONTMATTER
# ============================================
# Materials/Settings reference by ID:
# relationships:
#   regulatory_standards:
#   - id: fda-laser-product-performance
#   - id: osha-ppe-requirements
#   - id: ansi-laser-safety
```

**Benefits**:
- ✅ Single source of truth for regulatory data
- ✅ Easy to update URLs, images, descriptions
- ✅ Reduces 150 files by ~500 lines each = 75,000 lines
- ✅ Consistent data structure across all references

---

## 2. PPE Requirements Library

**File**: `data/safety/PPELibrary.yaml`  
**Purpose**: Standardized PPE recommendations based on hazard types  
**Current State**: Similar PPE patterns repeated across 19 compound files

### Schema

```yaml
ppe_templates:
  # ============================================
  # GAS/VAPOR HAZARDS
  # ============================================
  irritant-gas-low-concentration:
    id: irritant-gas-low-concentration
    hazard_type: irritant_gas
    concentration_range: "<25 ppm"
    minimum_protection_level: Level C
    requirements:
      respiratory:
        equipment: NIOSH-approved organic vapor respirator
        standard: NIOSH 42 CFR 84
        condition: For concentrations <25 ppm
        upgrade_threshold: ">25 ppm - use SCBA"
      skin:
        equipment: Nitrile or butyl rubber gloves
        standard: ANSI/ISEA 105
        condition: Chemical-resistant clothing for liquid contact
        thickness: "15-18 mil minimum"
      eye:
        equipment: Chemical safety goggles, face shield for splash hazard
        standard: ANSI Z87.1
        condition: Indirect vents, sealed to face
      body:
        equipment: Chemical-resistant apron or suit
        standard: NFPA 1991
        condition: For handling or splash potential
    special_notes:
    - Probable human carcinogen (IARC Group 2B)
    - Extremely flammable - eliminate ignition sources
    - Work in well-ventilated area or use local exhaust
    
  irritant-gas-high-concentration:
    id: irritant-gas-high-concentration
    hazard_type: irritant_gas
    concentration_range: ">25 ppm or unknown"
    minimum_protection_level: Level B
    requirements:
      respiratory:
        equipment: Self-contained breathing apparatus (SCBA)
        standard: NIOSH 42 CFR 84
        condition: For concentrations >25 ppm or unknown
        upgrade_threshold: Always required for unknown concentrations
      skin:
        equipment: Chemical-protective suit with gloves
        standard: NFPA 1991 Level B
        condition: Fully encapsulating when >25 ppm
        material: Butyl rubber or Viton
      eye:
        equipment: Full-face respirator (part of SCBA)
        standard: Integrated with SCBA
        condition: Full face protection required
      body:
        equipment: Level B chemical protective suit
        standard: NFPA 1991 Level B
        condition: Splash-resistant, vapor-tight
    special_notes:
    - SCBA mandatory for concentrations >25 ppm
    - Continuous air monitoring required
    - Emergency shower and eyewash within 10 seconds travel time
  
  # ============================================
  # PARTICULATE HAZARDS
  # ============================================
  particulate-carcinogen:
    id: particulate-carcinogen
    hazard_type: particulate
    hazard_level: carcinogen
    minimum_protection_level: Level C
    requirements:
      respiratory:
        equipment: HEPA-filtered respirator (P100)
        standard: NIOSH 42 CFR 84
        condition: For particles <10 μm
        filter_efficiency: "99.97% @ 0.3 μm"
      skin:
        equipment: Nitrile gloves, disposable coveralls
        standard: ANSI/ISEA 101
        condition: Prevent skin contact with particulates
        disposal: "Contained disposal - hazardous waste"
      eye:
        equipment: Safety goggles with side shields
        standard: ANSI Z87.1
        condition: Impact and particle protection
      body:
        equipment: Disposable Tyvek coveralls
        standard: ANSI/ISEA 101
        condition: Full body coverage, sealed at wrists/ankles
    special_notes:
    - Known or suspected carcinogen
    - Wet methods preferred to suppress dust
    - HEPA vacuum only - never dry sweep
    - Medical surveillance program required
  
  # ============================================
  # CORROSIVE LIQUIDS
  # ============================================
  corrosive-liquid-moderate:
    id: corrosive-liquid-moderate
    hazard_type: corrosive_liquid
    hazard_level: moderate
    minimum_protection_level: Level C
    requirements:
      respiratory:
        equipment: Half-face respirator with acid gas cartridge
        standard: NIOSH 42 CFR 84
        condition: If vapor exposure possible
        cartridge_type: Acid gas/organic vapor combination
      skin:
        equipment: Neoprene or PVC gloves, chemical apron
        standard: ASTM F739
        condition: Elbow-length gloves for handling
        breakthrough_time: ">8 hours"
      eye:
        equipment: Chemical splash goggles and face shield
        standard: ANSI Z87.1
        condition: Face shield over goggles for handling
      body:
        equipment: Chemical-resistant apron or suit
        standard: ASTM F1001
        condition: Full-body coverage for large quantities
    special_notes:
    - Emergency shower and eyewash within 10 seconds
    - Flush eyes for 15 minutes if contact occurs
    - Remove contaminated clothing immediately

# ============================================
# USAGE IN FRONTMATTER
# ============================================
# Compounds reference by ID:
# relationships:
#   ppe_requirements:
#     template_id: irritant-gas-low-concentration
#     overrides:
#       special_notes:
#       - "Additional note specific to this compound"
```

**Benefits**:
- ✅ Consistent PPE recommendations across compounds
- ✅ Easy to update standards/requirements centrally
- ✅ Override system for compound-specific requirements
- ✅ Reduces duplicate data in 19 compound files

---

## 3. Emergency Response Library

**File**: `data/safety/EmergencyResponseLibrary.yaml`  
**Purpose**: Standardized emergency response procedures by hazard type  
**Current State**: Similar procedures repeated across 19 compound files

### Schema

```yaml
response_templates:
  # ============================================
  # FLAMMABLE GAS
  # ============================================
  flammable-gas-extremely:
    id: flammable-gas-extremely
    hazard_type: flammable_gas
    severity: extreme
    flash_point: "<-18°C"
    explosive_range: "LEL <10%"
    
    fire_hazard:
      description: EXTREMELY FLAMMABLE. Wide explosive range.
      ignition_sensitivity: Vapors heavier than air - travel to ignition sources
      explosion_risk: May polymerize explosively in fire
      propagation: Vapors spread rapidly along ground level
      
    fire_suppression:
      immediate_action: EVACUATE - explosion hazard
      flow_control: Stop flow if safe to approach
      extinguishing_agents:
      - Dry chemical (preferred)
      - CO2
      - Alcohol-resistant foam
      prohibited_agents:
      - Water jet (may spread fire)
      cooling: Water spray to cool containers from distance
      special_considerations:
      - Do not direct water jet on liquid
      - Allow fire to burn if flow cannot be stopped safely
      
    spill_procedures:
      immediate_action: EVACUATE area immediately
      hazard_control:
      - Eliminate ALL ignition sources
      - Prohibit smoking, flames, sparks within 50 feet
      ppe_required: SCBA for large spills or confined spaces
      containment:
      - Contain with dry sand or earth
      - Absorb with vermiculite or clay
      - Use explosion-proof equipment only
      neutralization: Sodium bisulfite solution for acetaldehyde
      disposal: Containerize as hazardous waste
      ventilation: Maximum ventilation, explosion-proof fans
      
    exposure_immediate_actions:
      inhalation:
      - Remove victim to fresh air IMMEDIATELY
      - Administer oxygen if breathing is difficult
      - Seek medical attention
      - Monitor for delayed respiratory effects
      skin_contact:
      - Remove contaminated clothing
      - Flush skin with water for 15 minutes
      - Wash with soap and water
      - Seek medical attention
      eye_contact:
      - Flush with water for 15 minutes
      - Remove contact lenses if present
      - Continue flushing during transport
      - Seek immediate medical attention
      ingestion:
      - DO NOT induce vomiting
      - Rinse mouth with water
      - Never give anything by mouth if unconscious
      - Seek immediate medical attention
        
    environmental_hazards:
      aquatic_toxicity: Toxic to aquatic life
      volatilization: Rapidly volatilizes from water
      biodegradation: Biodegrades quickly in soil/water
      reporting:
      - Report spills to NRC: 1-800-424-8802
      - Reportable quantity: 1000 lbs
      containment: Prevent entry to waterways/sewers
      
    special_hazards:
    - PROBABLE HUMAN CARCINOGEN (IARC 2B)
    - Respiratory tract carcinogen in animals
    - May polymerize violently when contaminated
    - Narcotic effects at high concentrations
    - Extremely irritating to eyes and respiratory tract
  
  # ============================================
  # CORROSIVE LIQUID
  # ============================================
  corrosive-liquid-strong:
    id: corrosive-liquid-strong
    hazard_type: corrosive_liquid
    severity: high
    ph_range: "<2 or >12.5"
    
    fire_hazard:
      description: Non-flammable but may intensify fire
      decomposition: May release toxic fumes in fire
      reaction_risk: Reacts violently with water/bases/metals
      container_risk: Containers may rupture in heat
      
    fire_suppression:
      immediate_action: Use appropriate extinguisher for surrounding fire
      special_considerations:
      - Do NOT use water jet directly on acid
      - Use water spray to cool containers
      - Neutralize small fires before extinguishing
      
    spill_procedures:
      immediate_action: Evacuate non-essential personnel
      ppe_required: Level B protection with acid suit
      containment:
      - Dike to contain spill
      - Prevent entry to waterways
      - Use acid-resistant absorbent
      neutralization:
      - Small spills - neutralize with soda ash/lime
      - Large spills - call HazMat team
      - Test pH before handling
      ventilation: Ensure adequate ventilation
      
    exposure_immediate_actions:
      inhalation:
      - Move to fresh air immediately
      - Administer oxygen if needed
      - Seek medical attention immediately
      skin_contact:
      - Flush with water for 15+ minutes
      - Remove contaminated clothing under water
      - Apply calcium gluconate gel if available
      - Seek immediate medical attention
      eye_contact:
      - CRITICAL - flush immediately for 15 minutes minimum
      - Hold eyelids open, rotate eye
      - Continue flushing during transport
      - IMMEDIATE medical attention required
      ingestion:
      - DO NOT induce vomiting
      - Rinse mouth, drink water to dilute
      - Never neutralize in stomach
      - IMMEDIATE medical attention required
        
    environmental_hazards:
      water_contamination: Severe water pollution risk
      reporting: Report all releases to local authorities
      soil_impact: May contaminate soil/groundwater
      
    special_hazards:
    - Causes severe burns to skin and eyes
    - Permanent tissue damage possible
    - May be fatal if swallowed or inhaled
    - Reacts violently with many chemicals

# ============================================
# USAGE IN FRONTMATTER
# ============================================
# Compounds reference by ID:
# relationships:
#   emergency_response:
#     template_id: flammable-gas-extremely
#     overrides:
#       special_hazards:
#       - "Compound-specific hazard note"
```

**Benefits**:
- ✅ Consistent emergency procedures by hazard type
- ✅ Comprehensive, professionally structured responses
- ✅ Easy to update procedures centrally
- ✅ Override system for compound-specific details

---

## 4. Implementation in Generators

### Enricher Pattern (Recommended)

```python
# export/enrichment/regulatory_enricher.py
class RegulatoryStandardsEnricher:
    """Enrich frontmatter with regulatory standards from library"""
    
    def __init__(self):
        # Load library
        with open('data/regulatory/RegulatoryStandards.yaml') as f:
            self.library = yaml.safe_load(f)['regulatory_standards']
    
    def enrich(self, frontmatter: dict, config: dict) -> dict:
        """
        Expand regulatory standard IDs to full details
        
        Input frontmatter:
          relationships:
            regulatory_standards:
            - id: fda-laser-product-performance
            - id: osha-ppe-requirements
        
        Output frontmatter:
          relationships:
            regulatory_standards:
            - id: fda-laser-product-performance
              title: FDA 21 CFR 1040.10 - Laser Product...
              authority: FDA
              url: https://...
              image: /images/logo/logo-org-fda.png
              # ... all fields from library
        """
        if 'relationships' not in frontmatter:
            return frontmatter
        
        if 'regulatory_standards' not in frontmatter['relationships']:
            return frontmatter
        
        # Expand each ID reference
        standards = frontmatter['relationships']['regulatory_standards']
        expanded = []
        
        for standard in standards:
            if isinstance(standard, dict) and 'id' in standard:
                std_id = standard['id']
                if std_id in self.library:
                    # Merge library data with any overrides
                    full_data = {**self.library[std_id], **standard}
                    expanded.append(full_data)
                else:
                    # Keep original if not in library
                    expanded.append(standard)
            else:
                expanded.append(standard)
        
        frontmatter['relationships']['regulatory_standards'] = expanded
        return frontmatter
```

### Config Integration

```yaml
# export/config/materials.yaml
enrichments:
  # ... existing enrichments ...
  
  - type: regulatory_standards
    library: data/regulatory/RegulatoryStandards.yaml
    field: relationships.regulatory_standards
    
  - type: ppe_requirements
    library: data/safety/PPELibrary.yaml
    field: relationships.ppe_requirements
    
  - type: emergency_response
    library: data/safety/EmergencyResponseLibrary.yaml
    field: relationships.emergency_response
```

---

## 5. Migration Strategy

### Step 1: Create Libraries (Week 1)
1. Create 3 YAML files with complete data
2. Validate structure and content
3. Test loading and parsing

### Step 2: Update Generators (Week 1)
1. Create enricher classes for each library
2. Register in enrichment registry
3. Add to domain configs

### Step 3: Update Source Data (Week 2)
1. Replace full objects with ID references in Materials.yaml, etc.
2. Keep old data commented out for rollback
3. Test export with new enrichers

### Step 4: Regenerate Frontmatter (Week 2)
1. Run --export-all with new enrichers
2. Validate output contains full data (not just IDs)
3. Compare before/after for consistency

### Step 5: Cleanup (Week 3)
1. Remove commented-out old data
2. Update documentation
3. Archive old frontmatter files

---

## 6. Validation

### Pre-Migration Checklist
- [ ] Libraries contain all data currently in frontmatter
- [ ] Enrichers tested with sample data
- [ ] Backup of current frontmatter exists
- [ ] Rollback plan documented

### Post-Migration Validation
- [ ] All 424 files export successfully
- [ ] Regulatory standards expanded correctly
- [ ] PPE requirements match originals
- [ ] Emergency response procedures complete
- [ ] Website renders correctly
- [ ] No data loss detected

---

**Status**: Design Complete - Ready for Implementation (Week 1)  
**Next**: Create data/regulatory/RegulatoryStandards.yaml
