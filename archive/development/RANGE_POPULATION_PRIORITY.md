# Range Population Priority System

**Last Updated**: October 14, 2025  
**Status**: Priority order documented, deep web search implementation needed

---

## 🎯 Priority Order for Populating Null Ranges

When frontmatter properties have `min: null` and `max: null`, populate them using this strict priority order:

### Priority 1: Categories.yaml Published Ranges ✅ IMPLEMENTED
**Source**: `data/Categories.yaml`  
**Status**: Already working in current system  

If a property has a published range defined in Categories.yaml for that category, use it.

**Example**:
```yaml
# Categories.yaml
metal:
  properties:
    meltingPoint:
      range:
        min: 232
        max: 3695
        unit: °C
```

This range automatically populates all metal materials' `meltingPoint` fields.

---

### Priority 2: Deep Web Search for Authoritative Ranges ⚠️ NOT YET IMPLEMENTED
**Source**: Scientific databases, academic papers, industry standards  
**Status**: **MUST BE IMPLEMENTED BEFORE USING SIBLING CALCULATION**

Conduct comprehensive web searches for published scientific ranges for each property-category combination.

**Search Strategy**:
1. **Academic Sources**: 
   - Google Scholar
   - ResearchGate
   - IEEE Xplore
   - Materials databases (ASM, MatWeb)

2. **Industry Standards**:
   - ASTM specifications
   - ISO standards
   - Industry handbooks
   - Manufacturer specifications

3. **Search Query Format**:
   ```
   "[property name] range [category name] materials"
   "typical [property name] values [category name]"
   "[property name] variation [category name] alloys"
   ```

4. **Validation Criteria**:
   - Source must be peer-reviewed or from recognized authority
   - Multiple sources should corroborate the range
   - Range should be specific to the material category
   - Units must be clearly defined

**Example Searches**:
```
"surface roughness range metal alloys"
"typical reflectivity values metallic materials"
"ablation threshold variation ceramic materials"
"oxidation resistance range industrial metals"
```

**Implementation Requirements**:
- Create `scripts/search_published_ranges.py`
- Store results in `data/PublishedRanges.yaml`
- Include source citations and confidence scores
- Validate against multiple authoritative sources

---

### Priority 3: Sibling Material Calculation ✅ IMPLEMENTED (FALLBACK ONLY)
**Source**: Our own Materials.yaml data  
**Status**: Implemented in `populate_sibling_ranges.py`  
**⚠️ USE ONLY AFTER**: Completing deep web searches (Priority 2)

Calculate min/max from materials within the same category in our database.

**Algorithm**:
```python
# For each property with null ranges:
1. Collect all numeric values from sibling materials in same category
2. Calculate min = minimum value
3. Calculate max = maximum value
4. Require at least 2 materials for valid range
5. Store source as 'sibling_materials'
```

**Example**:
```yaml
# Calculated from 35 metal materials in database
surfaceRoughness:
  min: 0.8
  max: 0.8
  unit: μm Ra
  source: sibling_materials
  sample_size: 7
```

**Limitations**:
- Only as comprehensive as our current material database
- May not represent full industry spectrum
- Limited to materials we've already documented
- Cannot capture industry-wide variations

---

## 🚨 Critical Implementation Rule

**BEFORE RUNNING `populate_sibling_ranges.py`:**

1. ✅ Verify Categories.yaml has all known published ranges
2. ⚠️ **CONDUCT DEEP WEB SEARCHES** for remaining properties (Priority 2)
3. ✅ Document search results in `data/PublishedRanges.yaml`
4. ✅ Update frontmatter with published ranges found
5. ✅ ONLY THEN run sibling calculation for truly unknown ranges

---

## 📊 Current Status

### Properties Already Populated (Priority 1):
- ✅ **11 core properties** have ranges from Categories.yaml
- ✅ **3,247 property instances** across 122 materials
- ✅ Includes: meltingPoint, density, thermalConductivity, etc.

### Properties Needing Deep Web Search (Priority 2):
- ⚠️ **surfaceRoughness** (many materials lack category ranges)
- ⚠️ **reflectivity** (material-specific, needs category baselines)
- ⚠️ **ablationThreshold** (laser-specific, category variation unknown)
- ⚠️ **oxidationResistance** (many metals lack published ranges)
- ⚠️ **absorptionCoefficient** (wavelength-dependent, needs research)
- ⚠️ **chemicalStability** (subjective scaling, needs standardization)
- ⚠️ **porosity** (wide variation, category ranges needed)

### Properties Currently Using Sibling Calculation (Priority 3):
- ⚠️ **704 properties** populated from sibling materials
- ⚠️ **Should be reviewed** after deep web search implementation
- ⚠️ Some may have published ranges we haven't found yet

### Properties Correctly Null:
- ✅ **laserType** (59 files) - Categorical, not numeric
- ✅ **crystallineStructure** (52 files) - Descriptive text
- ✅ **wavelength** (3 files) - Single material has property
- ✅ Total: 160 properties correctly have no ranges

---

## 🔧 Implementation Checklist

### Phase 1: Deep Web Search (PRIORITY - Not Yet Started)
- [ ] Create `scripts/search_published_ranges.py`
- [ ] Define search queries for each property-category combination
- [ ] Compile authoritative sources list (academic, industry, standards)
- [ ] Conduct systematic searches for all properties with null ranges
- [ ] Document findings with sources and confidence scores
- [ ] Create `data/PublishedRanges.yaml` with structured results
- [ ] Validate ranges against multiple sources
- [ ] Update frontmatter files with published ranges

### Phase 2: Sibling Calculation (FALLBACK - Completed)
- [x] Create `scripts/populate_sibling_ranges.py`
- [x] Implement category grouping logic
- [x] Calculate min/max from sibling materials
- [x] Add dry-run mode for testing
- [x] Generate comprehensive reports
- [x] Update 121 frontmatter files
- [x] Populate 704 properties

### Phase 3: Validation (After Phase 1 Complete)
- [ ] Compare sibling-calculated ranges vs published ranges
- [ ] Identify discrepancies requiring investigation
- [ ] Update ranges where published data is more authoritative
- [ ] Document confidence levels for each range source
- [ ] Create quality report showing range sources

---

## 📝 Range Source Attribution

Each populated range should track its source:

```yaml
materialProperties:
  physical:
    properties:
      surfaceRoughness:
        value: 0.8
        unit: μm Ra
        min: 0.5        # From which source?
        max: 10.0       # From which source?
        rangeSource: "published"  # or "sibling_materials"
        rangeConfidence: 85       # 0-100 scale
        rangeCitation: "ASM Metals Handbook, Vol. 2, 2023"  # if published
```

---

## 🎓 Best Practices

1. **Always prioritize published data** over calculated ranges
2. **Document sources** for all published ranges with citations
3. **Validate** published ranges against multiple authorities
4. **Use sibling calculation** only when no published data exists
5. **Re-validate** sibling ranges when more materials are added
6. **Flag uncertainties** with confidence scores
7. **Update regularly** as new research is published

---

## 📚 Recommended Resources for Deep Web Search

### Materials Databases:
- **ASM International**: Materials property data
- **MatWeb**: Comprehensive material property database
- **NIST Materials Data**: National Institute of Standards
- **SpringerMaterials**: Peer-reviewed property data

### Academic Search:
- **Google Scholar**: Academic papers and citations
- **ResearchGate**: Researcher networks and publications
- **IEEE Xplore**: Engineering and technology papers
- **ScienceDirect**: Scientific journal articles

### Standards Organizations:
- **ASTM International**: Material testing standards
- **ISO**: International standards
- **SAE International**: Aerospace and automotive standards
- **ASME**: Mechanical engineering standards

### Industry Handbooks:
- ASM Metals Handbook series
- Handbook of Materials Science
- CRC Materials Science and Engineering Handbook
- Springer Handbook of Materials Measurement Methods

---

## 🚀 Next Steps

1. **IMMEDIATE**: Implement deep web search system (Priority 2)
2. **THEN**: Run comprehensive searches for all null-range properties
3. **VALIDATE**: Compare published ranges vs sibling-calculated ranges
4. **UPDATE**: Replace sibling ranges with published ranges where found
5. **DOCUMENT**: Create range source attribution for all properties
6. **MAINTAIN**: Regular updates as new research is published

---

**Remember**: The goal is not just to populate ranges, but to provide **accurate, authoritative, scientifically-backed** range data that users can trust for their laser cleaning applications.
