# Frontmatter Generation: AI API Call Requirements

**Date**: October 17, 2025  
**Component**: Frontmatter Generator  
**System**: Streamlined Generator (`components/frontmatter/core/streamlined_generator.py`)

---

## 🤖 Overview: Which Fields Use AI?

During frontmatter generation, **5 fields** may require AI API calls, depending on data availability:

| Field | AI Required? | Conditions | API Provider |
|-------|-------------|------------|--------------|
| **description** (subtitle) | ✅ YES | Always generated with AI | DeepSeek |
| **materialProperties** | ⚠️ CONDITIONAL | Only for missing/low-confidence properties | DeepSeek |
| **machineSettings** | ⚠️ CONDITIONAL | Only for missing settings | DeepSeek |
| **caption** | ✅ YES | Always generated with AI | Grok (via caption component) |
| **applications** | ❌ NO | Extracted from Materials.yaml | N/A |

---

## 📋 Detailed Field Breakdown

### 1. **description** (Subtitle) - ALWAYS AI

**Location**: Top-level field  
**API Calls**: 1 per material  
**Provider**: DeepSeek  
**Token Usage**: ~150 tokens  
**Purpose**: Generate natural, conversational 2-sentence subtitle

#### Example Output:
```yaml
description: "The micro-porous surface needs controlled thermal penetration—standard cleaning won't reach those deep oxide layers. I've found success with shorter wavelengths here, letting photon absorption target just the contamination without compromising the ceramic's structural integrity."
```

#### Code Reference:
```python
def _generate_subtitle(self, material_name: str, category: str, subcategory: str, material_data: Dict) -> str:
    """Generate AI-powered subtitle highlighting material-specific characteristics"""
    # Located at: streamlined_generator.py:1502-1591
    prompt = f"""Generate a natural, conversational two-sentence subtitle about {material_name}..."""
    response = self.api_client.generate_simple(
        prompt=prompt,
        max_tokens=150,
        temperature=0.75
    )
```

---

### 2. **materialProperties** - CONDITIONAL AI

**Location**: Nested section  
**API Calls**: Variable (0-20+ per material)  
**Provider**: DeepSeek  
**Token Usage**: ~500 tokens per property researched  
**Purpose**: Fill missing or low-confidence material properties

#### When AI is Used:
1. **Property missing** from Materials.yaml
2. **Confidence < 85%** in existing data
3. **Range data incomplete** in Categories.yaml (triggers CategoryRangeResearcher)

#### What Gets Researched:
- Physical properties (density, hardness, etc.)
- Thermal properties (conductivity, expansion, etc.)
- Mechanical properties (tensile strength, modulus, etc.)
- Optical properties (absorption, reflectivity)

#### Code Reference:
```python
def _generate_from_yaml(self, material_name: str, material_data: Dict) -> Dict:
    """Generate from Materials.yaml with AI enhancement for missing properties"""
    # Located at: streamlined_generator.py:617-896
    
    # Phase 1: Load high-confidence YAML properties
    yaml_properties = material_data.get('properties', {})
    for prop_name, yaml_prop in yaml_properties.items():
        confidence = yaml_prop.get('confidence', 0)
        if confidence >= 0.85:  # High confidence threshold
            properties[prop_name] = yaml_prop
    
    # Phase 2: Discover which properties need AI research
    to_research = self.property_discovery_service.discover_properties_to_research(
        material_name=material_name,
        material_category=material_category,
        yaml_properties=yaml_properties
    )
    
    # Phase 3: Research missing properties with AI
    researched_properties = self.property_research_service.research_material_properties(
        material_name=material_name,
        material_category=material_category,
        existing_properties=properties
    )
```

#### Example Scenarios:

**Scenario A**: Aluminum (Well-documented metal)
- YAML has 12 properties with high confidence (≥85%)
- AI researches: 0-2 properties (mostly complete)
- **API Calls**: ~0-2

**Scenario B**: Rare Ceramic (Poorly documented)
- YAML has 3 properties with high confidence
- AI researches: 10+ properties
- **API Calls**: ~10-15

---

### 3. **machineSettings** - CONDITIONAL AI

**Location**: Nested section  
**API Calls**: Variable (0-8 per material)  
**Provider**: DeepSeek  
**Token Usage**: ~300 tokens per setting  
**Purpose**: Generate laser processing parameters when not in Materials.yaml

#### When AI is Used:
- No `machineSettings` data in Materials.yaml
- Falls back to AI generation with ranges from Categories.yaml

#### Settings Generated:
- powerRange
- wavelength
- spotSize
- repetitionRate
- pulseDuration
- fluenceThreshold
- scanningSpeed
- beamProfile

#### Code Reference:
```python
def _generate_machine_settings(self, material_name: str, material_data: Dict, category: str) -> Dict:
    """Generate machine settings with intelligent lookup"""
    # Located at: streamlined_generator.py:1230-1257
    
    # Try YAML first
    if material_data and 'machineSettings' in material_data:
        return self._extract_machine_settings_from_yaml(material_data)
    
    # Fall back to AI generation
    self.logger.info(f"No machineSettings in Materials.yaml - using AI generation")
    return self._generate_machine_settings_from_api(material_name, category)
```

---

### 4. **caption** - ALWAYS AI

**Location**: Nested `componentOutputs.caption` section  
**API Calls**: 1 per material  
**Provider**: Grok (via Caption Component)  
**Token Usage**: ~3000 tokens  
**Purpose**: Generate before/after microscopy analysis

#### Generated Fields:
- `beforeText`: Pre-cleaning surface description (~800 chars)
- `afterText`: Post-cleaning results (~800 chars)
- `technicalAnalysis`: Material-specific characteristics
- `microscopy`: Parameters and quality metrics
- `seo`: Title and description

#### Example Output:
```yaml
componentOutputs:
  caption:
    beforeText: "At 500x magnification, the contaminated aluminum surface reveals..."
    afterText: "Following laser treatment, the cleaned surface demonstrates..."
    technicalAnalysis:
      focus: "surface_analysis"
      uniqueCharacteristics:
        - "Native oxide layer formation"
        - "Thermal conductivity effects"
    microscopy:
      parameters: "500x magnification, brightfield illumination"
      qualityMetrics: "Ra < 0.5 μm, oxide layer removed"
```

#### Code Reference:
```python
def _add_caption_section(self, frontmatter: Dict, material_data: Dict, material_name: str) -> Dict:
    """Add caption section with before/after text using AI generation"""
    # Located at: streamlined_generator.py:1648-1738
    
    prompt = f"""You are writing technical documentation for laser surface cleaning...
    
    Generate exactly two text blocks:
    **BEFORE_TEXT:**
    [microscopic analysis of contaminated surface]
    
    **AFTER_TEXT:**
    [analysis of cleaned surface with results]
    """
    
    response = self.api_client.generate_simple(
        prompt=prompt,
        max_tokens=3000,
        temperature=0.2
    )
```

---

### 5. **applications** - NO AI (Data Extraction Only)

**Location**: Top-level array  
**API Calls**: 0  
**Source**: Materials.yaml extraction  
**Purpose**: List industry applications

#### Example:
```yaml
applications:
  - Aerospace
  - Automotive
  - Electronics Manufacturing
  - Medical Devices
```

---

## 📊 Total API Calls Per Material

### Best Case (Well-Documented Material):
- **description**: 1 call
- **materialProperties**: 0-2 calls
- **machineSettings**: 0 calls
- **caption**: 1 call
- **TOTAL**: ~2-4 API calls

### Average Case (Typical Material):
- **description**: 1 call
- **materialProperties**: 5-8 calls
- **machineSettings**: 0-3 calls
- **caption**: 1 call
- **TOTAL**: ~7-13 API calls

### Worst Case (Rare/Undocumented Material):
- **description**: 1 call
- **materialProperties**: 15-20 calls
- **machineSettings**: 8 calls
- **caption**: 1 call
- **TOTAL**: ~25-30 API calls

---

## 🔧 Configuration

All AI generation is configured in `run.py`:

```python
# Component-specific generation settings
"component_generation": {
    "frontmatter": {
        "max_tokens": 4000,
        "temperature": 0.3,
    },
}

# API Provider Configuration
API_PROVIDERS = {
    "deepseek": {
        "model": "deepseek-chat",
        "max_tokens": 4000,
        "temperature": 0.1,
        "enabled": True,
    },
    "grok": {
        "model": "grok-3",
        "max_tokens": 550,
        "temperature": 0.2,
        "enabled": True,
    },
}
```

---

## 🚫 Fields That NEVER Use AI

These fields are **always** generated from existing data:

1. **name** - From Materials.yaml
2. **category** - From Materials.yaml
3. **subcategory** - From Materials.yaml
4. **title** - Template: "{Material Name} Laser Cleaning"
5. **author** - From Materials.yaml `author.id` lookup
6. **images** - Static URL templates
7. **regulatoryStandards** - Universal standards list
8. **environmentalImpact** - Static template based on category
9. **outcomeMetrics** - Static template
10. **prompt_chain_verification** - System metadata

---

## 💡 Cost & Performance Implications

### Token Usage Estimates:
- **description**: 150 tokens/call
- **materialProperties**: 500 tokens/property
- **machineSettings**: 300 tokens/setting
- **caption**: 3000 tokens/call

### Example: Aluminum (Well-documented)
- Calls: 2-4
- Tokens: ~3,500-4,000
- Cost: ~$0.01-0.02 (DeepSeek rates)
- Time: ~5-10 seconds

### Example: Rare Ceramic (Undocumented)
- Calls: 25-30
- Tokens: ~15,000-20,000
- Cost: ~$0.08-0.10
- Time: ~45-60 seconds

---

## 🎯 Optimization Strategies

### To Minimize AI Calls:
1. **Improve Materials.yaml coverage** - Add more high-confidence (≥85%) properties
2. **Complete Categories.yaml ranges** - Prevent range research API calls
3. **Pre-populate machineSettings** - Add to Materials.yaml for common materials
4. **Cache AI responses** - Reuse for similar materials (already implemented)

### Currently Implemented:
- ✅ Response caching (saves 90%+ on regeneration)
- ✅ High-confidence threshold (85%) to prefer existing data
- ✅ Batch processing to amortize overhead
- ✅ Fail-fast validation before API calls

---

## 📝 Summary

**Always AI**: `description` (subtitle), `caption`  
**Conditional AI**: `materialProperties`, `machineSettings`  
**Never AI**: `name`, `category`, `title`, `author`, `images`, etc.

**Total API Calls**: Typically 7-13 per material, range 2-30 depending on data completeness.

**Primary AI Provider**: DeepSeek (structured data generation)  
**Secondary AI Provider**: Grok (caption narrative generation)
