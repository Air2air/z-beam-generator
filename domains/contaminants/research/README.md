# Contamination Research System

## Overview

The Contamination Research System provides **AI-driven research for laser-specific contamination properties** using the `LaserPropertiesResearcher` class. Research supports laser cleaning process design and contamination pattern analysis.

## Architecture (Simplified Nov 2025)

```
LaserPropertiesResearcher (single class - 875 lines)
├── 8 research types (optical, thermal, removal, safety, etc.)
├── ContaminationResearchSpec input format
├── ContaminationResearchResult output format  
├── Confidence scoring and validation
└── Fail-fast architecture (no mocks/defaults)
```

## Core Components

### LaserPropertiesResearcher (`laser_properties_researcher.py`)

**Purpose**: Research laser-specific scientific data for contamination patterns

**Key Methods**:
- `research(pattern_id, research_spec, context)` → ContaminationResearchResult

**Supported Research Types**:
1. **optical_properties**: Absorption, reflectivity, refractive index at laser wavelengths
2. **thermal_properties**: Ablation thresholds, decomposition temps, thermal conductivity
3. **removal_characteristics**: Mechanisms, byproducts, efficiency ratings
4. **layer_properties**: Thickness ranges, penetration depth, adhesion
5. **laser_parameters**: Recommended wavelength, fluence, scan speed settings
6. **safety_data**: Fumes, ventilation requirements, PPE
7. **selectivity_ratios**: Material-specific selectivity for selective removal
8. **complete_profile**: All laser properties in one call

**Usage Example**:
```python
from domains.contaminants.research import (
    LaserPropertiesResearcher,
    ContaminationResearchSpec
)

# Create researcher directly (no factory needed)
researcher = LaserPropertiesResearcher(api_client)

# Research specific aspect
spec = ContaminationResearchSpec(
    pattern_id="rust_oxidation",
    research_type="optical_properties",
    material_context="Steel"
)
result = researcher.research("rust_oxidation", spec)

# Research complete profile
spec = ContaminationResearchSpec(
    pattern_id="rust_oxidation",
    research_type="complete_profile",
    material_context="Steel"
)
result = researcher.research("rust_oxidation", spec)
```

## Key Principles

1. **Fail-Fast Architecture**: API client required, no mocks or defaults
2. **Schema Validation**: All research validated against Contaminants.yaml structure
3. **Confidence Scoring**: Every result includes confidence (0.0-1.0)
4. **Context-Aware**: Material context for targeted research
5. **Direct Instantiation**: No factory pattern overhead

## Data Flow

1. **Pattern Discovery**: Load existing pattern from Contaminants.yaml
2. **Prompt Construction**: Build AI prompt with context and existing data
3. **AI Research**: Execute AI research with specified parameters
4. **Response Parsing**: Parse YAML response from AI
5. **Validation**: Validate result against schema requirements
6. **Confidence Scoring**: Calculate confidence based on completeness
7. **Result Return**: ContaminationResearchResult with data and metadata

## Research Result Structure

```python
@dataclass
class ContaminationResearchSpec:
    pattern_id: str
    research_type: str
    material_context: Optional[str] = None
    context: Optional[Dict] = None

@dataclass
class ContaminationResearchResult:
    pattern_id: str           # Pattern identifier
    data: Dict                # Researched data
    confidence: float         # 0.0 to 1.0
    source: str              # "ai_research"
    error: Optional[str]     # Error if research failed
    metadata: Dict           # Research context and details
    
    @property
    def success(self) -> bool:
        return self.error is None and bool(self.data)
```

## Confidence Thresholds

- **HIGH_CONFIDENCE**: 0.85 (85%)
- **ACCEPTABLE_CONFIDENCE**: 0.70 (70%)

Results below acceptable confidence are flagged for review.

## CLI Tools

### Research Laser Properties
```bash
# Research single property type
python3 scripts/research_laser_properties.py --pattern rust_oxidation --type optical_properties

# Research complete profile
python3 scripts/research_laser_properties.py --pattern rust_oxidation --type complete_profile --save

# Research all patterns
python3 scripts/research_laser_properties.py --all-patterns --type optical_properties
```

### Batch Research
```bash
# Research all contamination patterns
python3 tools/research_contaminants.py --all

# Research specific pattern
python3 tools/research_contaminants.py --pattern rust_oxidation
```

## Testing

Run tests with:
```bash
pytest tests/test_contamination_research.py -v
```

## Architecture Notes (Nov 2025 Cleanup)

**Removed**:
- `PatternResearcher` (417 lines) - unused, overlapped with VisualAppearanceResearcher
- `base.py` (235 lines) - abstract base class moved inline
- `factory.py` (136 lines) - unnecessary for single researcher

**Kept**:
- `LaserPropertiesResearcher` (875 lines) - actively used for laser property research
- `VisualAppearanceResearcher` (487 lines, separate file) - actively used for image generation

**Rationale**: Java-style factory pattern is overkill for 2 researchers. Direct instantiation is simpler and equally type-safe.
