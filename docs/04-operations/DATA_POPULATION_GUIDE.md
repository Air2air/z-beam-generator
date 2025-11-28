# Non-Text Data Population Guide
**How to Research and Populate Material Properties**

---

## 🔬 Overview

Non-text data refers to **numeric material properties** like density, thermal conductivity, melting point, etc. These properties are researched using AI (DeepSeek) and stored in `Materials.yaml`.

---

## 📊 What Properties Are Researched

### Physical Properties
- **density** - Mass per unit volume (g/cm³)
- **meltingPoint** - Temperature at which material melts (°C)
- **hardness** - Material hardness (Mohs, Vickers, etc.)
- **porosity** - Percentage of void space (%)

### Thermal Properties
- **thermalConductivity** - Heat transfer rate (W/m·K)
- **thermalExpansion** - Expansion coefficient (µm/m·K)
- **thermalDiffusivity** - Heat diffusion rate (mm²/s)
- **thermalShockResistance** - Resistance to thermal stress
- **thermalDestructionPoint** - Temperature limit (°C)

### Optical Properties
- **absorptionCoefficient** - Light absorption rate
- **reflectivity** - Surface reflection percentage (%)
- **emissivity** - Thermal radiation efficiency

### Electrical Properties
- **electricalResistivity** - Resistance to electric current (Ω·m)
- **electricalConductivity** - Ability to conduct electricity

### Laser-Specific Properties
- **ablationThreshold** - Energy needed for ablation (J/cm²)
- **laserAbsorptionCoefficient** - Laser energy absorption
- **damageThreshold** - Energy limit before damage (J/cm²)

---

## 🎯 How to Populate Properties

### Method 1: Single Material Research
```bash
# Research properties for one material
python3 run.py --research-missing-properties --research-materials "Boron Nitride"
```

### Method 2: Multiple Materials
```bash
# Research properties for multiple materials
python3 run.py --research-missing-properties --research-materials "Boron Nitride,Titanium Nitride,Yttria-Stabilized Zirconia"
```

### Method 3: All Missing Properties
```bash
# Research ALL materials with missing properties
python3 run.py --research-missing-properties
```

### Method 4: Check What's Missing
```bash
# See which materials need property research
python3 run.py --data-gaps
```

---

## 🔧 The Research Process

### Step 1: AI Research
- **AI Provider**: DeepSeek (configured in `.env`)
- **Research Method**: Multi-strategy approach
  1. Scientific databases lookup
  2. Technical literature search
  3. Material handbooks
  4. Industry standards
  5. Peer-reviewed publications

### Step 2: Data Validation
- **Confidence Scoring**: Each property gets a confidence score (0-100)
- **Unit Verification**: Ensures correct units (e.g., g/cm³ for density)
- **Range Validation**: Checks values are physically reasonable
- **Source Tracking**: Records where data came from

### Step 3: Storage
- **Primary Storage**: `data/materials/Materials.yaml`
- **Structure**:
```yaml
Aluminum:
  name: Aluminum
  category: metal
  materialProperties:
    density:
      value: 2.70
      unit: g/cm³
      confidence: 95
      min: 2.63
      max: 2.80
      description: "Typical range for common aluminum alloys"
    thermalConductivity:
      value: 205
      unit: W/m·K
      confidence: 90
      description: "At room temperature (25°C)"
```

### Step 4: Export
```bash
# Export to frontmatter after research
python3 run.py --deploy
```

---

## 📋 Example: Complete Workflow

### Scenario: Add 3 New Ceramic Materials

**Step 1: Import Materials** (Manual - add to Materials.yaml)
```yaml
Boron Nitride:
  name: Boron Nitride
  category: ceramic
  subcategory: technical
  title: Boron Nitride Laser Cleaning
```

**Step 2: Research Properties**
```bash
python3 run.py --research-missing-properties --research-materials "Boron Nitride,Titanium Nitride,Yttria-Stabilized Zirconia"
```

**Output**:
```
🔬 STAGE 0: AI RESEARCH & DATA COMPLETION
📂 Loading Materials.yaml...
🔍 Analyzing data gaps...
📊 Found 42 missing property values (3 materials × 14 properties)

🎯 Research Priorities:
   • Boron Nitride: 14 properties
   • Titanium Nitride: 14 properties
   • YSZ: 14 properties

🔬 Researching Boron Nitride...
   ✅ density: 2.1 g/cm³ (confidence: 92%)
   ✅ thermalConductivity: 30 W/m·K (confidence: 88%)
   ✅ meltingPoint: 2973 °C (confidence: 95%)
   ... (11 more properties)

📊 Research Complete:
   • Total properties researched: 42
   • Success rate: 95% (40/42)
   • Average confidence: 89%
   • Time: 3m 15s
```

**Step 3: Verify Research**
```bash
# Check what was saved
python3 << 'EOF'
import yaml
with open('data/materials/Materials.yaml', 'r') as f:
    data = yaml.safe_load(f)
    bn = data['materials']['Boron Nitride']
    props = bn.get('materialProperties', {})
    print(f"Boron Nitride: {len(props)} properties")
    for key, val in list(props.items())[:3]:
        if isinstance(val, dict):
            print(f"  • {key}: {val.get('value')} {val.get('unit')}")
EOF
```

**Step 4: Generate Text Content**
```bash
# Generate descriptions, captions, etc.
python3 run.py --material-description "Boron Nitride"
python3 run.py --caption "Boron Nitride"
python3 run.py --faq "Boron Nitride"
```

**Step 5: Export**
```bash
python3 run.py --deploy
```

---

## ⚠️ Current Issues (November 23, 2025)

### Property Research Path Error
**Issue**: Research system looks for Materials.yaml at wrong path
- **Expected**: `data/materials/Materials.yaml`
- **Actual**: `domains/materials/data/Materials.yaml`
- **Impact**: Blocks ceramic property research
- **Status**: Requires configuration fix

**Workaround**: Manual YAML editing or fix path configuration first

---

## 🎯 Current Status

### Materials Needing Property Research (3)
1. **Boron Nitride** - 0 properties (needs all 14-16)
2. **Titanium Nitride** - 0 properties (needs all 14-16)
3. **Yttria-Stabilized Zirconia** - 0 properties (needs all 14-16)

### Materials with Complete Properties (13)
- Stainless Steel 316 (14 properties)
- Stainless Steel 304 (14 properties)
- PTFE (16 properties)
- Gallium Nitride (18 properties)
- PEEK (14 properties)
- Polyimide (16 properties)
- Zirconia (22 properties)
- Titanium Carbide (20 properties)
- Tungsten Carbide (18 properties)
- Boron Carbide (16 properties)
- Silicon Carbide (20 properties)
- Aluminum Nitride (19 properties)
- Silicon Nitride (18 properties)

---

## 🔍 Quality Assurance

### Confidence Levels
- **90-100%**: Database or handbook values (highly reliable)
- **70-89%**: Literature values with minor uncertainty
- **50-69%**: Estimated from similar materials
- **Below 50%**: Not saved (triggers re-research or manual review)

### Data Sources
1. **Material Property Databases** (MatWeb, NIST, etc.)
2. **Scientific Literature** (journals, papers)
3. **Industry Standards** (ASTM, ISO)
4. **Technical Handbooks** (ASM, CRC)
5. **Manufacturer Data Sheets**

---

## 📚 Related Documentation

- **Property Research System**: `export/research/property_value_researcher.py`
- **Research Configuration**: `generation/config.yaml`
- **Data Architecture**: `docs/DATA_ARCHITECTURE.md`
- **Zero Null Policy**: `docs/ZERO_NULL_POLICY.md`
- **AI Guide**: `.github/copilot-instructions.md`

---

## 🎓 Key Principles

### Fail-Fast Architecture
- ❌ NO fallback values or defaults
- ❌ NO "N/A" or null for required properties
- ✅ Research OR fail (user must fix)
- ✅ Explicit confidence scoring

### Research-Based Only
- ❌ NO estimates without research
- ❌ NO copy-paste from similar materials
- ✅ Every value has source + confidence
- ✅ AI research with verification

### Quality Gates
- Minimum confidence: 50%
- Unit validation: Required
- Range checking: Physical limits
- Source tracking: Always recorded

---

**Summary**: Non-text data is populated through AI-powered research using DeepSeek, with confidence scoring and source tracking. The system ensures fail-fast behavior with no fallbacks or defaults.
