# Contamination Research System

## Overview

The Contamination Research System provides **AI-driven research for contamination patterns** using a dedicated `PatternResearcher` class. Research supports both image generation validation and dedicated contamination pages.

## Architecture

```
PatternResearcher
├── Multi-type research (detailed_description, formation_conditions, visual_characteristics, etc.)
├── ContaminationResearchResult output format  
├── Confidence scoring and validation
└── Fail-fast architecture (no mocks/defaults)
```

## Core Components

### PatternResearcher (`pattern_researcher.py`)

**Purpose**: Research contamination pattern details for dedicated pages and enhanced validation

**Key Methods**:
- `research(pattern_id, research_spec, context)` → ContaminationResearchResult
- `research_pattern_details(pattern_id, material_context)` → Dict of all research types
- Validation against Contaminants.yaml schema

**Supported Research Types**:
1. **detailed_description**: Comprehensive technical description (200-400 words)
2. **formation_conditions**: Environmental conditions for formation (temp, humidity, duration)
3. **visual_characteristics**: Observable characteristics (color, texture, pattern)
4. **material_compatibility**: Valid/invalid material lists with chemical basis
5. **environmental_factors**: Contextual factors affecting formation
6. **chemical_composition**: Detailed chemical analysis
7. **removal_methods**: Laser cleaning strategies and parameters

**Usage Example**:
```python
from domains.contaminants.research.factory import ContaminationResearcherFactory
from domains.contaminants.research.base import ContaminationResearchSpec

# Create researcher
factory = ContaminationResearcherFactory()
researcher = factory.create_pattern_researcher(api_client)

# Research specific aspect
spec = ContaminationResearchSpec(
    pattern_id="rust_oxidation",
    research_type="detailed_description",
    material_context="Steel"
)
result = researcher.research("rust_oxidation", spec)

# Or research all details at once
all_details = researcher.research_pattern_details(
    pattern_id="rust_oxidation",
    material_context="Steel"
)
```

## Factory Pattern

### ContaminationResearcherFactory (`factory.py`)

**Purpose**: Create appropriate researcher for contamination research tasks

**Available Researchers**:
- `pattern` / `detail` / `information`: PatternResearcher (all aliases)

**Future Extensibility**:
- `compatibility`: Specialized material-contamination compatibility research
- `removal`: Research removal methods and laser parameters
- `formation`: Research formation processes and chemistry

**Usage**:
```python
factory = ContaminationResearcherFactory()
researcher = factory.create_researcher('pattern', api_client)
```

## Key Principles

1. **Fail-Fast Architecture**: API client required, no mocks or defaults in production
2. **Schema Validation**: All research validated against Contaminants.yaml structure
3. **Confidence Scoring**: Every result includes confidence (0.0-1.0)
4. **Context-Aware**: Material and environment context for targeted research
5. **Multi-Type Support**: Different research types for different page needs

## Data Flow

1. **Pattern Discovery**: Load existing pattern from Contaminants.yaml
2. **Prompt Construction**: Build AI prompt with context and existing data
3. **AI Research**: Execute AI research with specified parameters
4. **Response Parsing**: Parse response (JSON or text based on type)
5. **Validation**: Validate result against schema requirements
6. **Confidence Scoring**: Calculate confidence based on completeness
7. **Result Return**: ContaminationResearchResult with data and metadata

## Integration Points

### Image Generation (Existing)
- ContaminationValidator uses Contaminants.yaml for compatibility
- Filters incompatible patterns during image generation
- Research system enhances with detailed pattern information

### Dedicated Pages (Future)
- PatternResearcher provides content for contamination pattern pages
- Detailed descriptions, formation conditions, visual characteristics
- Material compatibility matrices and chemistry explanations
- Similar architecture to Material property pages

## Research Result Structure

```python
@dataclass
class ContaminationResearchResult:
    pattern_id: str           # Pattern identifier
    data: Any                 # Researched data (varies by type)
    confidence: float         # 0.0 to 1.0
    source: str              # "ai_research", "database", etc.
    metadata: Dict           # Research context and details
    error: Optional[str]     # Error if research failed
```

## Confidence Thresholds

- **HIGH_CONFIDENCE**: 0.85 (85%)
- **ACCEPTABLE_CONFIDENCE**: 0.75 (75%)

Results below acceptable confidence are flagged for review.

## Example Research Types

### Detailed Description
```python
spec = ContaminationResearchSpec(
    pattern_id="rust_oxidation",
    research_type="detailed_description"
)
# Returns: 200-400 word technical description
```

### Formation Conditions
```python
spec = ContaminationResearchSpec(
    pattern_id="rust_oxidation",
    research_type="formation_conditions"
)
# Returns: {temperature, humidity, duration, environmental_factors, ...}
```

### Visual Characteristics
```python
spec = ContaminationResearchSpec(
    pattern_id="copper_patina",
    research_type="visual_characteristics"
)
# Returns: {color, texture, thickness, pattern, identification_markers}
```

### Material Compatibility
```python
spec = ContaminationResearchSpec(
    pattern_id="uv_chalking",
    research_type="material_compatibility",
    material_context="Acrylic"
)
# Returns: {valid_materials, invalid_materials, compatibility_notes, chemical_basis}
```

## Testing

Run tests with:
```bash
pytest tests/test_contamination_research.py -v
```

Test coverage includes:
- ✅ Factory creation and researcher types
- ✅ All research types with validation
- ✅ Confidence scoring and thresholds
- ✅ Error handling and fail-fast behavior
- ✅ Schema validation against Contaminants.yaml
- ✅ Context-aware research with materials

## Comparison to Materials Research

| Aspect | Materials Research | Contamination Research |
|--------|-------------------|----------------------|
| **Base Class** | ContentResearcher | ContaminationResearcher |
| **Factory** | ResearcherFactory | ContaminationResearcherFactory |
| **Researcher** | PropertyResearcher | PatternResearcher |
| **Data Source** | Materials.yaml | Contaminants.yaml |
| **Research Focus** | Material properties | Contamination patterns |
| **Use Cases** | Material pages, specifications | Contamination pages, validation |

## Future Enhancements

1. **Compatibility Researcher**: Specialized material-contamination compatibility analysis
2. **Removal Researcher**: Laser cleaning parameters and strategies per pattern
3. **Formation Researcher**: Detailed chemistry and formation process research
4. **Multi-Pattern Analysis**: Research multiple patterns simultaneously
5. **Historical Research**: Archive and learn from previous research results

## Architecture Notes

- **Mirrors Materials**: Same patterns and conventions as Materials research
- **Extensible**: Easy to add new researcher types via factory registration
- **Fail-Fast**: No degraded operation, explicit errors
- **Schema-Driven**: All validation against Contaminants.yaml structure
- **Context-Aware**: Material and environment context throughout

This research system enables both current validation needs (image generation) and future content needs (dedicated contamination pages) using a consistent, extensible architecture.
