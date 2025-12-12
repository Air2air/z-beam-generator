# Z-Beam Generator: Simplified Architecture

**Version**: 2.0 (October 2025)  
**Philosophy**: Streamlined to 6 active components with enhanced prompting

---

## 🎯 Core Design Principles

1. **Consolidated Components** - Reduced from 11 to 6 components for maintainability
2. **Fail-Fast Architecture** - Explicit validation, no fallbacks, no mocks
3. **Materials.yaml Orchestration** - Single source of truth for all data
4. **Enhanced Prompting** - Specialized prompt modules within components (not separate generators)
5. **Separation of Concerns** - Reusable services (Voice, PropertyManager) separate from component logic

---

## 📊 6-Component Architecture

```
components/
├── frontmatter/          # Core orchestrator - generates unified metadata
│   ├── core/
│   │   └── streamlined_generator.py (orchestration)
│   ├── prompts/          # NEW: Specialized prompt builders
│   │   ├── industry_applications.py (2-phase research)
│   │   ├── regulatory_standards.py
│   │   ├── environmental_impact.py
│   │   └── templates/ (markdown prompt files)
│   └── services/ (property management, templates, etc.)
│
├── micro/              # Discrete component - dual voice generation
│   ├── generators/
│   │   └── generator.py (micro-specific logic)
│   ├── config/ (micro settings)
│   └── ARCHITECTURE.md (reference pattern)
│
├── subtitle/             # Discrete component - single voice generation
│   ├── core/
│   │   └── subtitle_generator.py (subtitle-specific logic)
│   ├── prompts/ (subtitle prompt templates)
│   └── config/ (subtitle settings)
│
├── author/               # Static component (depends on frontmatter)
├── badgesymbol/          # Static component (depends on frontmatter)
├── metatags/             # Static component
├── jsonld/               # Static component
└── propertiestable/      # Static component
```

---

## 🔄 Component Patterns

### Pattern 1: Frontmatter Orchestrator (Enhanced Prompting)

**File**: `components/frontmatter/core/streamlined_generator.py`

**Role**: Orchestrate specialized prompt builders without creating separate generators.

```python
class StreamlinedFrontmatterGenerator(APIComponentGenerator):
    """
    Orchestrator for unified frontmatter generation.
    Uses specialized prompt builders for quality enhancement.
    """
    
    def __init__(self):
        super().__init__(component_type="frontmatter")
        
        # Load specialized prompt builders (NOT separate generators)
        from components.frontmatter.prompts.industry_applications import IndustryApplicationsPromptBuilder
        from components.frontmatter.prompts.regulatory_standards import RegulatoryStandardsPromptBuilder
        from components.frontmatter.prompts.environmental_impact import EnvironmentalImpactPromptBuilder
        
        self.industry_prompts = IndustryApplicationsPromptBuilder()
        self.regulatory_prompts = RegulatoryStandardsPromptBuilder()
        self.environmental_prompts = EnvironmentalImpactPromptBuilder()
    
    def _generate_industry_applications(self, material_name, material_data, api_client):
        """
        2-Phase prompting for rigorous industry research.
        
        Phase 1: Research with validation criteria
        Phase 2: Generate detailed 50-80 word descriptions
        """
        # Phase 1: Research
        research_prompt = self.industry_prompts.build_research_prompt(
            material_name=material_name,
            category=material_data.get('category'),
            material_properties=material_data.get('materialProperties', {})
        )
        research_response = api_client.generate_simple(research_prompt)
        
        # Validate quality
        validation = self.industry_prompts.validate_research_quality(research_response)
        if not validation['passed']:
            logger.warning(f"Research quality below threshold: {validation['issues']}")
            return []  # Fail fast
        
        # Phase 2: Generate detailed descriptions
        gen_prompt = self.industry_prompts.build_generation_prompt(
            validated_research=validation,
            material_name=material_name
        )
        final_response = api_client.generate_simple(gen_prompt)
        
        return self._parse_applications(final_response)
```

**Benefits**:
- ✅ No new components (stays at 6)
- ✅ Enhanced prompts for better quality
- ✅ 2-phase validation (research → generation)
- ✅ Materials.yaml orchestration preserved
- ✅ Fail-fast on quality thresholds

---

### Pattern 2: Discrete Components (Caption/Subtitle)

**Characteristics**:
- Self-contained component with specialized logic
- Reusable Voice service integration
- Component-specific prompts in dedicated folder
- Clear separation from shared services

**Example: Micro Component**

```
components/micro/
├── generators/
│   └── generator.py          # Micro-specific dual-voice logic
├── config/
│   └── config.yaml           # Micro settings (word counts, etc.)
└── ARCHITECTURE.md           # Reference pattern documentation
```

**Key Pattern**: Micro calls Voice service **twice** (before/after sections) but keeps micro-specific logic separate.

**Example: Subtitle Component**

```
components/subtitle/
├── core/
│   └── subtitle_generator.py    # Subtitle-specific logic
├── prompts/
│   └── templates/                # Subtitle prompt templates
└── config/
    └── config.yaml               # Subtitle settings
```

**Key Pattern**: Subtitle has single voice call with 8-12 word target, subtitle-specific validation.

---

## 🔧 Specialized Prompt Builders

### IndustryApplicationsPromptBuilder

**Location**: `components/frontmatter/prompts/industry_applications.py`

**Purpose**: 2-phase rigorous research for industry applications

**Methods**:
- `build_research_prompt()` - Phase 1: Validation criteria prompts
- `validate_research_quality()` - Quality gate (5-8 industries, confidence scoring)
- `build_generation_prompt()` - Phase 2: Detailed 50-80 word descriptions

**Quality Targets**:
- 5-8 evidence-based industries (vs 10+ generic)
- 50-80 word descriptions with specific products
- Standards citations (FAA, AWS, ISO, etc.)
- High/medium confidence threshold (70%+)

---

### RegulatoryStandardsPromptBuilder

**Location**: `components/frontmatter/prompts/regulatory_standards.py`

**Purpose**: Research applicable regulatory standards (FDA, ANSI, ISO, OSHA, IEC, EPA)

**Methods**:
- `build_research_prompt()` - Standards discovery with applicability verification
- `validate_research_quality()` - Ensure direct applicability

**Quality Targets**:
- 3-5 highly relevant standards
- Full longName for each standard
- Specific compliance requirements
- Industry-specific relevance

---

### EnvironmentalImpactPromptBuilder

**Location**: `components/frontmatter/prompts/environmental_impact.py`

**Purpose**: Quantified environmental benefits vs traditional cleaning

**Methods**:
- `build_research_prompt()` - Comparative analysis (chemical, water, VOC, energy, waste)
- `validate_research_quality()` - Ensure quantifiable metrics

**Quality Targets**:
- Quantified reductions (%, liters/m², kWh/m²)
- Specific chemical/waste types
- EPA/OSHA standard citations
- Cost savings analysis

---

## 📈 Data Flow: Materials.yaml Orchestration

```
┌─────────────────────────────────────────────────────────────┐
│                   Materials.yaml                             │
│              (Single Source of Truth)                        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│         StreamlinedFrontmatterGenerator                      │
│         (Orchestrator - 6 active components)                 │
├─────────────────────────────────────────────────────────────┤
│  1. Load material data from Materials.yaml                   │
│  2. Call specialized prompt builders:                        │
│     • IndustryApplicationsPromptBuilder (2-phase)            │
│     • RegulatoryStandardsPromptBuilder                       │
│     • EnvironmentalImpactPromptBuilder                       │
│  3. Validate quality thresholds (fail-fast)                  │
│  4. Merge results into unified frontmatter                   │
│  5. Save back to Materials.yaml                              │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Trivial Exporter                                │
│  (Export to frontmatter/*.yaml for Next.js)          │
└─────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│         Discrete Components (Caption/Subtitle)               │
│  • Caption: Dual voice calls (before/after)                  │
│  • Subtitle: Single voice call (8-12 words)                  │
│  • Both use VoiceOrchestrator (reusable service)             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Benefits of Simplified Architecture

### 1. Consolidation (6 Components)
- ✅ Reduced from 11 to 6 active components
- ✅ Clear component boundaries
- ✅ Easier maintenance and testing
- ✅ Simplified dependency graph

### 2. Enhanced Prompting (Without New Components)
- ✅ Specialized prompt builders in `frontmatter/prompts/`
- ✅ 2-phase validation (research → generation)
- ✅ Quality gates with scoring
- ✅ Template-based prompts (markdown files)

### 3. Separation of Concerns
- ✅ Voice service: Reusable across micro/subtitle
- ✅ Property services: Shared across frontmatter
- ✅ Component logic: Self-contained in discrete components
- ✅ No circular dependencies

### 4. Fail-Fast Design
- ✅ Quality thresholds enforced before generation
- ✅ No mocks or fallbacks in production
- ✅ Explicit validation at each phase
- ✅ Clear error messages with context

### 5. Materials.yaml Orchestration
- ✅ Single source of truth preserved
- ✅ All generation flows through Materials.yaml
- ✅ Trivial export to frontmatter files
- ✅ Data consistency guaranteed

---

## 🎯 Component Responsibilities

| Component | Type | Purpose | Dependencies |
|-----------|------|---------|--------------|
| **frontmatter** | Orchestrator | Unified metadata generation with enhanced prompting | Materials.yaml, prompt builders, services |
| **caption** | Discrete | Dual-section microscopy descriptions (before/after) | VoiceOrchestrator, frontmatter data |
| **subtitle** | Discrete | 8-12 word engaging subtitles | VoiceOrchestrator, frontmatter data |
| **author** | Static | Author information | frontmatter data |
| **badgesymbol** | Static | Material symbol badges | frontmatter data |
| **metatags** | Static | HTML meta tags | frontmatter data |
| **jsonld** | Static | JSON-LD structured data | frontmatter data |
| **propertiestable** | Static | Technical properties table | frontmatter data |

---

## 🚀 Migration from Previous Architecture

### What Changed:

**Before**:
- 11 components with complex dependencies
- Industry applications: 10+ generic entries, brief descriptions
- No validation phase for research
- Scattered prompt logic in monolithic files

**After**:
- 6 consolidated components
- Industry applications: 5-8 evidence-based, 50-80 word descriptions
- 2-phase validation (research → generation)
- Organized prompt builders in `frontmatter/prompts/`

### What Stayed the Same:

- ✅ ComponentGeneratorFactory pattern
- ✅ Materials.yaml single source of truth
- ✅ Fail-fast architecture principles
- ✅ ComponentResult standard output
- ✅ Trivial export to frontmatter files

---

## 📚 Reference Implementations

### Micro Component (Discrete Pattern)
**File**: `components/micro/ARCHITECTURE.md`

**Key Features**:
- Dual voice call architecture (before/after)
- Separation from Voice service
- Component-specific configuration
- Clear documentation of pattern

**Use as reference for**: Any component needing multiple AI generations with different contexts.

### Subtitle Component (Discrete Pattern)
**File**: `materials/subtitle/core/subtitle_generator.py`

**Key Features**:
- Single voice call with specific constraints (8-12 words)
- VoiceOrchestrator integration
- Subtitle-specific validation
- Clean separation from shared services

**Use as reference for**: Any component needing single AI generation with strict formatting.

---

## 🧪 Testing Strategy

### Frontmatter with Prompt Builders
```python
def test_industry_applications_2phase():
    """Test 2-phase prompting for industry applications"""
    builder = IndustryApplicationsPromptBuilder()
    
    # Phase 1: Research
    research_prompt = builder.build_research_prompt(
        material_name="Aluminum",
        category="metal",
        material_properties={"density": 2.7, "hardness": 95}
    )
    
    # Simulate API response
    research_response = api_client.generate_simple(research_prompt)
    
    # Validate
    validation = builder.validate_research_quality(research_response)
    assert validation['passed'] == True
    assert 5 <= len(validation['industries']) <= 8
    assert validation['quality_score'] >= 70.0
```

### Discrete Components (Caption/Subtitle)
```python
def test_micro_dual_voice():
    """Test micro's dual voice call pattern"""
    generator = CaptionComponentGenerator()
    
    result = generator.generate(
        material_name="Aluminum",
        material_data={"category": "metal"},
        api_client=api_client
    )
    
    assert 'beforeText' in result.content
    assert 'afterText' in result.content
    assert result.success == True
```

---

## 🔮 Future Enhancements

### Potential Additions (Maintain 6-Component Philosophy):
1. **Property prompts** - Add `property_generation.py` to `frontmatter/prompts/`
2. **Machine settings prompts** - Add `machine_settings.py` to `frontmatter/prompts/`
3. **Quality scoring** - Enhance validation with confidence scoring
4. **Caching** - Add LRU cache for prompt builders

### Anti-Patterns to Avoid:
- ❌ Creating new components for prompt variations
- ❌ Splitting frontmatter into multiple components
- ❌ Adding mocks or fallbacks in production code
- ❌ Bypassing Materials.yaml orchestration

---

## 📖 Quick Reference

**For Enhanced Prompting**: Add prompt builder to `components/frontmatter/prompts/`  
**For Discrete Components**: Follow micro/subtitle pattern with `core/`, `prompts/`, `config/`  
**For Shared Services**: Use `voice/`, `services/`, `utils/` - never duplicate  
**For Testing**: Write component tests + prompt builder tests  
**For Documentation**: Update this file when adding new patterns

---

**Last Updated**: October 26, 2025  
**Maintainer**: Z-Beam Generator Architecture Team  
**Related Docs**: `components/micro/ARCHITECTURE.md`, `README.md`, `GROK fail-fast principles`
