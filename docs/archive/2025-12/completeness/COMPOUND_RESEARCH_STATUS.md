# Compound Metadata Research - Batch Processing Instructions

**Status**: Formaldehyde Complete (1/19)  
**Remaining**: 18 compounds  
**Date**: December 15, 2025

---

## ✅ Completed Research

### **Formaldehyde** (CAS: 50-00-0)
- ✅ All 10 field categories populated (~60 data points)
- ✅ Sources: NIOSH, NIST, PubChem, DOT, OSHA, EPA, NFPA
- ✅ Ready for integration into Compounds.yaml

---

## 🔄 Batch Research Strategy

Given the scope (18 compounds × 60 data points = 1,080 data points remaining), we need an efficient approach.

### **Option A: AI-Assisted Sequential Research** ⭐ **RECOMMENDED**
Use Gemini/GPT-4 with structured prompts for each compound:

```python
# For each remaining compound:
compounds_to_research = [
    'benzene', 'pahs', 'chromium-vi',  # Carcinogens
    'carbon-monoxide', 'hydrogen-cyanide', 'acrolein', 
    'nitrogen-oxides', 'sulfur-dioxide', 'phosgene',  # Toxic gases
    'hydrogen-chloride', 'ammonia',  # Corrosive
    'zinc-oxide', 'iron-oxide', 'acetaldehyde', 
    'styrene', 'vocs', 'toluene', 'carbon-dioxide'  # Others
]

# Process in batches of 3-4 for quality control
```

### **Option B: Parallel Research with Multiple AI Queries**
Split compounds across multiple AI sessions simultaneously.

### **Option C: Hybrid - Critical First, Then Batch**
1. **Priority 1** (Next 3): Benzene, Carbon Monoxide, Hydrogen Cyanide (1 hour)
2. **Priority 2** (Next 6): Remaining carcinogens + toxic gases (1.5 hours)
3. **Priority 3** (Remaining 9): All others (1 hour)

---

## 📋 Research Template for Each Compound

Use this prompt structure for AI queries:

```
Research [COMPOUND NAME] (CAS: [CAS NUMBER], Formula: [FORMULA])

Provide complete metadata in the following structured format:

### TIER 1: SAFETY CRITICAL

**PPE Requirements:**
- Respiratory: [NIOSH-approved equipment type]
- Skin: [Glove materials, clothing]
- Eye: [Goggles/face shield requirements]
- Minimum Level: [EPA Level A/B/C/D]
- Special Notes: [Any special precautions]

**Physical Properties:**
- Boiling Point: [°C]
- Melting Point: [°C]
- Vapor Pressure: [mmHg @ 20°C]
- Vapor Density: [(Air=1)]
- Specific Gravity: [value]
- Flash Point: [°C if applicable]
- Autoignition Temp: [°C]
- Explosive Limits: [LEL/UEL %]
- Appearance: [description]
- Odor: [description + threshold ppm]

**Emergency Response:**
- Fire Hazard: [description]
- Fire Suppression: [methods]
- Spill Procedures: [step-by-step]
- Exposure Immediate Actions: [first aid]
- Environmental Hazards: [impacts]
- Special Hazards: [decomposition, reactions]

**Storage Requirements:**
- Temperature Range: [limits]
- Ventilation: [requirements]
- Incompatibilities: [list materials]
- Container Material: [approved types]
- Segregation: [requirements]
- Quantity Limits: [if any]
- Special Requirements: [notes]

### TIER 2: REGULATORY COMPLIANCE

**Regulatory Classification:**
- UN Number: [DOT code]
- DOT Hazard Class: [class number]
- DOT Label: [label text]
- NFPA Codes: H:[0-4] F:[0-4] R:[0-4] Special:[code if any]
- EPA Hazard Categories: [list]
- SARA Title III: [yes/no]
- CERCLA RQ: [pounds]
- RCRA Code: [if listed]

**Workplace Exposure:**
- OSHA PEL: TWA:[ppm] STEL:[ppm] Ceiling:[ppm]
- NIOSH REL: TWA:[ppm] STEL:[ppm] Ceiling:[ppm] IDLH:[ppm]
- ACGIH TLV: TWA:[ppm] STEL:[ppm] Ceiling:[ppm]
- Biological Exposure Indices: [metabolite, specimen, timing, value]

**Synonyms & Identifiers:**
- Synonyms: [list common names]
- Trade Names: [list if applicable]
- RTECS Number: [code]
- EC Number: [code]
- PubChem CID: [number]

### TIER 3: OPERATIONAL CONTEXT

**Reactivity:**
- Stability: [description]
- Polymerization: [potential]
- Incompatible Materials: [list]
- Hazardous Decomposition: [products]
- Conditions to Avoid: [list]
- Reactivity Hazard: [description]

**Environmental Impact:**
- Aquatic Toxicity: [description + LC50 if available]
- Biodegradability: [readily/not readily + % degradation]
- Bioaccumulation: [log Kow value]
- Soil Mobility: [high/medium/low]
- Atmospheric Fate: [half-life, reactions]
- Ozone Depletion: [yes/no]
- Global Warming Potential: [value or N/A]
- Reportable Releases: Water:[threshold] Air:[threshold]

**Detection & Monitoring:**
- Sensor Types: [list]
- Detection Range: [ppm]
- Alarm Setpoints: Low:[ppm] High:[ppm] Evacuate:[ppm]
- Colorimetric Tubes: [brands/models]
- Analytical Methods: [method #, technique, detection limit]
- Odor Threshold: [reliability statement]

**Sources**: NIOSH Pocket Guide, NIST Chemistry WebBook, PubChem, DOT ERG, 29 CFR 1910, 40 CFR, NFPA 704
```

---

## 🚀 Next Steps

**Immediate** (30 minutes):
1. Research Benzene, Carbon Monoxide, Hydrogen Cyanide (Priority 1 - highest risk)
2. Create standardized YAML structure for integration

**Short-term** (2-3 hours):
3. Research remaining 15 compounds in priority order
4. Quality check: Cross-reference 3-4 compounds against SDS sheets
5. Integrate all researched metadata into Compounds.yaml

**Documentation** (30 minutes):
6. Update domain documentation with new field descriptions
7. Add research methodology notes
8. Document data sources used

---

## 📊 Progress Tracking

| Compound | Status | Data Points | Time |
|----------|--------|-------------|------|
| Formaldehyde | ✅ Complete | 60/60 | 30 min |
| Benzene | ⏳ Next | 0/60 | - |
| Carbon Monoxide | ⏳ Next | 0/60 | - |
| Hydrogen Cyanide | ⏳ Next | 0/60 | - |
| ... (15 more) | ⏸️ Pending | 0/60 | - |

**Total Progress**: 60/1,140 data points (5.3%)  
**Estimated Completion**: 2-3 hours with AI assistance

---

## ⚠️ Quality Control Checkpoints

After each batch of 3-4 compounds:
- [ ] All 10 field categories populated
- [ ] No placeholder text ("TBD", "N/A" without justification)
- [ ] Units are consistent (ppm, mg/m³, °C)
- [ ] Sources are authoritative (NIOSH, NIST, EPA, DOT)
- [ ] Cross-reference 1 compound with SDS sheet for verification

---

## 🎯 Success Criteria

**Metadata Enhancement Complete When:**
- ✅ All 19 compounds have all 10 field categories populated
- ✅ 1,140 total data points researched and verified
- ✅ Quality spot-checks passed (3-4 compounds vs SDS)
- ✅ Documentation updated with field descriptions
- ✅ Compounds.yaml updated and validated (YAML syntax check)

**Then Ready For**: Phase 1 content generation (formaldehyde test)
