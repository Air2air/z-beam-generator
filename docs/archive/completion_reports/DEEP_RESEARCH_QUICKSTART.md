# Deep Research Quick Start Guide

**Quick commands to populate and use deep research data**

---

## 🚀 Quick Commands

### Discover Alloys for a Material
```bash
python3 scripts/research/populate_deep_research.py --material Aluminum --discover-alloys
```
Output: Creates `materials/data/Aluminum_alloy_research.txt` with alloy variations

### Research Single Property
```bash
python3 scripts/research/populate_deep_research.py --material Aluminum --property density
```
Output: Updates `PropertyResearch.yaml` with multi-source density data

### Research Single Setting
```bash
python3 scripts/research/populate_deep_research.py --material Aluminum --setting wavelength
```
Output: Updates `SettingResearch.yaml` with context-specific wavelength variations

### Research All Properties for a Material
```bash
python3 scripts/research/populate_deep_research.py --material Aluminum --all-properties
```
Researches: density, thermalConductivity, hardness, thermalExpansion, laserAbsorption, laserReflectivity

### Research All Settings for a Material
```bash
python3 scripts/research/populate_deep_research.py --material Aluminum --all-settings
```
Researches: wavelength, powerRange, fluenceThreshold, spotSize, scanSpeed

### Batch Process Multiple Materials
```bash
python3 scripts/research/populate_deep_research.py \
  --materials "Aluminum,Steel,Titanium,Copper" \
  --property density
```

---

## 📚 Using Research Data in Code

### Get Property Research for Specific Material
```python
from materials.data.loader import get_property_research

# Get aluminum density research with alloy variations
research = get_property_research('Aluminum', 'density')

# Access primary value
primary_value = research['primary']['value']  # 2.70
primary_unit = research['primary']['unit']    # g/cm³

# Access research values (multiple sources/alloys)
for source in research['research']['values']:
    print(f"{source['value']} {source['unit']} - {source['source']}")
    print(f"  Context: {source.get('context', {})}")
    print(f"  Citation: {source.get('citation', 'N/A')}")
    print(f"  Confidence: {source.get('confidence', 0)}%")
```

### Get Setting Research with Context Variations
```python
from materials.data.loader import get_setting_research

# Get aluminum wavelength research
research = get_setting_research('Aluminum', 'wavelength')

# Access primary value
primary = research['primary']['value']  # 1064

# Access context variations
for variation in research['research']['values']:
    print(f"{variation['value']} nm")
    print(f"  Application: {variation['context']['application']}")
    print(f"  Advantages: {variation.get('advantages', [])}")
    print(f"  Performance: {variation.get('performance', {})}")
```

### Compare Property Across All Materials
```python
from materials.data.loader import get_all_property_research

# Get density research for all materials
all_density = get_all_property_research('density')

for material, research in all_density.items():
    if research:
        print(f"{material}: {research['primary']['value']} {research['primary']['unit']}")
        print(f"  Sources: {len(research['research']['values'])}")
```

### Get Material Alloy Variations
```python
from materials.data.loader import get_material_variations

# Get aluminum alloy variations
alloys = get_material_variations('Aluminum')

for alloy in alloys:
    print(f"{alloy.get('designation', 'Unknown')}")
    print(f"  Composition: {alloy.get('composition', {})}")
    print(f"  Applications: {alloy.get('applications', [])}")
```

---

## 🎯 Recommended Workflow

### Phase 1: High Priority Materials & Properties

**Step 1**: Discover alloys
```bash
python3 scripts/research/populate_deep_research.py --material Aluminum --discover-alloys
python3 scripts/research/populate_deep_research.py --material Steel --discover-alloys
python3 scripts/research/populate_deep_research.py --material Titanium --discover-alloys
python3 scripts/research/populate_deep_research.py --material Copper --discover-alloys
```

**Step 2**: Research critical properties
```bash
# Density (affects material handling, cooling)
python3 scripts/research/populate_deep_research.py \
  --materials "Aluminum,Steel,Titanium,Copper" --property density

# Thermal conductivity (affects heat dissipation)
python3 scripts/research/populate_deep_research.py \
  --materials "Aluminum,Steel,Titanium,Copper" --property thermalConductivity

# Laser absorption (critical for laser cleaning)
python3 scripts/research/populate_deep_research.py \
  --materials "Aluminum,Steel,Titanium,Copper" --property laserAbsorption
```

**Step 3**: Research critical settings
```bash
# Wavelength (most important setting)
python3 scripts/research/populate_deep_research.py \
  --materials "Aluminum,Steel,Titanium,Copper" --setting wavelength

# Power range (second most important)
python3 scripts/research/populate_deep_research.py \
  --materials "Aluminum,Steel,Titanium,Copper" --setting powerRange
```

**Step 4**: Manual validation
1. Open `materials/data/PropertyResearch.yaml`
2. Review AI-generated values and sources
3. Verify citations (check DOIs, ISBNs, URLs)
4. Replace placeholders with validated data
5. Add missing sources if needed

---

## ⚠️ Important Notes

### AI-Generated Data Requires Validation
- AI responses are stored with `needs_validation: true`
- Always verify sources and values before production use
- Check that citations are real and accessible
- Ensure values are scientifically accurate

### Automatic Backups
- Script creates backups before updating files
- Backups stored as: `PropertyResearch_backup_YYYYMMDD_HHMMSS.yaml`
- Safe to run multiple times

### File Locations
- **PropertyResearch.yaml**: `materials/data/PropertyResearch.yaml`
- **SettingResearch.yaml**: `materials/data/SettingResearch.yaml`
- **Alloy Research Notes**: `materials/data/{Material}_alloy_research.txt`
- **Backups**: `materials/data/*_backup_*.yaml`

---

## 🔍 Example: Complete Aluminum Research Workflow

```bash
# 1. Discover aluminum alloys (1100, 2024, 6061, 7075, etc.)
python3 scripts/research/populate_deep_research.py --material Aluminum --discover-alloys

# 2. Research all properties with alloy variations
python3 scripts/research/populate_deep_research.py --material Aluminum --all-properties

# 3. Research all settings with context variations
python3 scripts/research/populate_deep_research.py --material Aluminum --all-settings

# 4. Review and validate data
cat materials/data/PropertyResearch.yaml | grep -A 50 "Aluminum:"
cat materials/data/SettingResearch.yaml | grep -A 50 "Aluminum:"

# 5. Use in code
python3 -c "
from materials.data.loader import get_property_research
research = get_property_research('Aluminum', 'density')
print(f\"Primary: {research['primary']['value']} {research['primary']['unit']}\")
print(f\"Research sources: {len(research['research']['values'])}\")
"
```

---

## 📊 Expected Output Structure

### PropertyResearch.yaml
```yaml
Aluminum:
  density:
    primary:
      value: 2.70
      unit: g/cm³
      confidence: 95
      source: ASM Handbook Vol. 2
    research:
      values:
        - value: 2.699
          unit: g/cm³
          confidence: 100
          source: NIST Database
          source_type: government_database
          context:
            purity: "99.99%"
            alloy: Pure
          citation:
            url: "https://webbook.nist.gov/..."
        - value: 2.70
          unit: g/cm³
          confidence: 95
          source: ASM Handbook Vol. 2
          source_type: reference_handbook
          context:
            alloy: "6061-T6"
            standard: AA-6061
          citation:
            isbn: "978-0-87170-378-1"
        # ... more sources
      metadata:
        total_sources: 6
        value_range: {min: 2.699, max: 2.81}
        alloy_variations: [Pure, 1100, 2024, 6061, 7075]
```

### SettingResearch.yaml
```yaml
Aluminum:
  wavelength:
    primary:
      value: 1064
      unit: nm
      description: Standard near-infrared wavelength
    research:
      values:
        - value: 355
          unit: nm
          confidence: 90
          source: Laser Cleaning Research
          context:
            application: precision_cleaning
            material_condition: polished
          advantages:
            - Minimal heat affected zone
            - High precision
          disadvantages:
            - Slower processing
            - Higher cost
          performance:
            removal_rate: 0.5
            removal_rate_unit: μm/pass
            surface_roughness: Ra 0.2 μm
            damage_risk: low
        - value: 1064
          unit: nm
          is_primary: true
          industry_adoption: 95
          # ... more context
      metadata:
        primary_wavelength: 1064
        selection_guide:
          precision: 355
          general: 532
          industrial: 1064
```

---

## 🎓 Next Steps

1. **Populate Phase 1 Data**: Run research for Aluminum, Steel, Titanium, Copper
2. **Validate Data**: Manually review and verify all AI-generated research
3. **Expand Coverage**: Add more materials (Phase 2: Brass, Bronze, Stainless, Nickel)
4. **Build Templates**: Create Astro components for drill-down pages
5. **Enable Search**: Add filtering by alloy, context, application
6. **Add Calculators**: Interactive tools based on research data

---

## 📖 Documentation

- **Full Guide**: `DEEP_RESEARCH_IMPLEMENTATION_COMPLETE.md`
- **Alloy Catalog**: `docs/ALLOY_VARIATIONS_PROPOSAL.md`
- **Schema Details**: `docs/schemas/DEEP_RESEARCH_SCHEMA.md`
- **Script Source**: `scripts/research/populate_deep_research.py`
- **Loader API**: `materials/data/loader.py` (lines 652-973)
