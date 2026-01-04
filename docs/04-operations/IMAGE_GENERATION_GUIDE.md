# Image Generation Guide - Complete Workflow

**Purpose**: Comprehensive guide to AI-powered hero image generation for all domains  
**Audience**: AI assistants, developers, content creators  
**Last Updated**: November 28, 2025

---

## 🎯 Quick Start

### Generate a Material Hero Image
```bash
python3 domains/materials/image/generate.py "Steel" --output-dir public/images/materials
```

### Generate a Contaminant Hero Image
```bash
python3 domains/contaminants/image/generate.py "Rust" --output-dir public/images/contaminants
```

### With Custom Contamination Level
```bash
python3 domains/materials/image/generate.py "Aluminum" --contamination-level 7 --output-dir public/images/materials
```

---

## 🏗️ **System Architecture**

### Three-Layer Design

**Layer 1: Domain Adapter** (`domains/{domain}/image/`)
- Translates domain-specific config → generic parameters
- Handles domain-specific learning systems
- Material example: `MaterialImageGenerator`, `MaterialImageConfig`
- Contaminant example: `ContaminantImageGenerator`, `ContaminantImageConfig`

**Layer 2: Orchestrator** (`shared/image/orchestrator.py`)
- Domain-agnostic prompt chaining (5 stages)
- Works for ALL domains (materials, contaminants, regions)
- Interface: `generate_hero_prompt(identifier, category, api)`

**Layer 3: Validation** (`shared/validation/prompt_validator.py`)
- Pre-generation quality gates
- Prevents bad prompts from reaching API
- Universal validation across all domains

### Domain Independence
**Documentation**: `docs/02-architecture/DOMAIN_ARCHITECTURE.md`

```python
# ✅ CORRECT: Domain adapter translates to generic
orchestrator.generate_hero_prompt(
    identifier="Steel",      # Generic
    category="metals",       # Generic
    api=imagen_api          # Generic
)

# ❌ WRONG: Domain-specific parameters leak to shared
orchestrator.build_prompt(
    material_name="Steel",           # Domain-specific
    contamination_level=5,           # Domain-specific
    machine_settings={...}           # Domain-specific
)
```

**Why This Matters**: New domains (regions, applications) can use the same orchestrator without modifying shared code.

---

## 🔄 **Generation Pipeline**

### Stage 1: Research & Data Gathering
**Location**: Domain adapter calls `DomainResearcher`

**For Materials**:
```python
# Load from Materials.yaml
material_data = {
    'name': 'Steel',
    'category': 'metals',
    'visual_appearance': {...},
    'contamination_patterns': {...}
}
```

**For Contaminants**:
```python
# Load from Contaminants.yaml
contaminant_data = {
    'name': 'Rust',
    'category': 'oxidation',
    'visual_characteristics': {...},
    'distribution_patterns': {...}
}
```

### Stage 2: Visual Description Generation
**Location**: `shared/image/orchestrator.py` - Stage 1

**Purpose**: Generate detailed visual description of the subject

**Temperature**: 0.7 (creative)

**Example Output**:
```
Polished stainless steel surface with mirror-like reflective finish.
Subtle grain patterns visible under directional lighting.
Cool metallic gray-blue tone with high specularity.
```

### Stage 3: Contamination Research
**Location**: `shared/image/orchestrator.py` - Stage 2

**Purpose**: Research contamination patterns and visual impact

**Temperature**: 0.3 (precise)

**Example Output**:
```
Contamination Level: 5/10 (Moderate)
- Surface oxidation: 40% coverage
- Rust patches: scattered, 2-5mm diameter
- Discoloration: brownish-red, uneven distribution
```

### Stage 4: Layout Composition
**Location**: `shared/image/orchestrator.py` - Stage 3

**Purpose**: Design before/after split composition

**Temperature**: 0.5 (balanced)

**Example Output**:
```
LEFT (Before): Contaminated surface with visible oxidation
- Position: Left 45% of frame
- Lighting: Angled to emphasize texture
- Focus: Contamination detail

RIGHT (After): Clean restored surface
- Position: Right 45% of frame
- Lighting: Matching angle, brighter
- Focus: Mirror-like finish

DIVIDER: 10% center, subtle gradient
```

### Stage 5: Technical Refinement
**Location**: `shared/image/orchestrator.py` - Stage 4

**Purpose**: Refine technical accuracy and specifications

**Temperature**: 0.4 (precise)

**Example Output**:
```
Technical Requirements:
- Aspect ratio: 16:9 (1920x1080)
- Lighting: Professional studio (5600K daylight)
- Depth of field: f/8 for surface detail
- Macro focus: 0.5m working distance
```

### Stage 6: Pre-Generation Validation
**Location**: `shared/validation/prompt_validator.py`

**Quality Gates** (ALL must pass):
1. **Length Check**: Positive < 4,096 chars, Negative < 4,096 chars
2. **Logical Coherence**: No contradictions in prompt
3. **Quality Standards**: Technical specs meet requirements
4. **Technical Compliance**: Valid parameters for Imagen 4

**Result**:
```python
ValidationResult(
    passed=True,
    score=85/100,
    feedback={
        'length': 'PASS: 2,847/4,096 chars',
        'coherence': 'PASS: No contradictions',
        'quality': 'PASS: Technical specs valid',
        'compliance': 'PASS: All parameters valid'
    }
)
```

**If validation fails**: Prompt rejected, no API call, feedback logged to learning system.

### Stage 7: Final Assembly & Generation
**Location**: `shared/image/generator.py`

**Prompt Optimization**:
- Condense verbose sections (research data)
- Apply learned feedback patterns
- Target: 2,800 chars positive (was 3,500)
- Preserve full negative prompt (1,450 chars)

**API Call**:
```python
imagen_api.generate_image(
    positive_prompt="[2,800 char optimized prompt]",
    negative_prompt="[1,450 char forbidden patterns]",
    aspect_ratio="16:9",
    safety_tolerance="block_only_high"
)
```

### Stage 8: Learning & Logging
**Location**: `domains/{domain}/image/learning/image_generation_logger.py`

**Captured Data**:
- Prompts (positive, negative, full research)
- Validation results (score, pass/fail, feedback)
- Generation parameters (temperature, contamination level)
- Outcome (success/failure, file size, path)
- Timestamp

**Storage**: `domains/{domain}/image/learning/learned_data.db` (SQLite)

**Analytics**: `python3 domains/{domain}/image/learning/analytics.py`

---

## 📊 **Prompt Optimization**

### Size Reduction Strategy
**Documentation**: `docs/06-ai-systems/PROMPT_OPTIMIZATION.md`

**Original Problem**: 10,100 chars total (exceeded Imagen 4 limit)

**Solution**:
1. **Template Consolidation**: 5 generation templates → 1,703 chars
2. **Dynamic Content**: Research data → ~1,200 chars (condensed)
3. **Learned Feedback**: ~500 chars (top patterns only)
4. **Optimizer**: Condense verbose sections → target 2,800 chars

**Result**: 3,250 chars total (68% reduction), well within limits

### Negative Prompt Architecture
**Storage**: `shared/image/prompts/generation/negative.txt`

**Categories**:
- Base forbidden patterns (~50 items): text, logos, watermarks, etc.
- Anti-text terms (18 items): typography, lettering, micros, etc.

**Total**: ~1,450 chars (35% of Imagen 4 limit)

**Separation**: Negative prompt in separate API field (not counted against positive limit)

---

## 🧠 **Learning System**

### Database Schema
**Location**: `domains/{domain}/image/learning/learned_data.db`

**Tables**:

**generation_attempts**:
- id, timestamp
- identifier (material/contaminant name)
- category
- contamination_level
- positive_prompt, negative_prompt, research_text
- validation_score, validation_passed
- outcome (success/failure)
- output_path, file_size_kb

**feedback_patterns**:
- id, timestamp
- pattern_type (rejection_reason, success_factor)
- pattern_text
- frequency (how often this pattern appears)

**sweet_spots**:
- id, timestamp
- identifier, category
- optimal_contamination_level
- optimal_temperature
- success_rate

### Analytics CLI
```bash
# View all attempts
python3 domains/materials/image/learning/analytics.py attempts

# Analyze patterns
python3 domains/materials/image/learning/analytics.py patterns

# Find sweet spots
python3 domains/materials/image/learning/analytics.py sweet-spots

# Category statistics
python3 domains/materials/image/learning/analytics.py categories
```

### Continuous Improvement
**Automatic**:
1. Every generation attempt logged (pass or fail)
2. Validation feedback captured
3. Sweet spot patterns updated
4. Feedback fed back into prompt building (closed loop)

**Manual**:
1. Review analytics to identify patterns
2. Update templates based on high-frequency rejections
3. Adjust default parameters based on sweet spots
4. Add new forbidden patterns to negative prompt

---

## 🛠️ **Configuration**

### Domain-Specific Config
**Location**: `domains/{domain}/image/config.yaml`

**Materials Example**:
```yaml
contamination:
  levels:
    min: 1
    max: 10
    default: 5
    
generation:
  aspect_ratio: "16:9"
  safety_tolerance: "block_only_high"
  
validation:
  length_limit: 4096
  min_score: 70
```

### Shared Config
**Location**: `shared/image/config.yaml`

```yaml
orchestrator:
  stages:
    - name: "visual_description"
      temperature: 0.7
    - name: "contamination_research"
      temperature: 0.3
    - name: "layout_composition"
      temperature: 0.5
    - name: "technical_refinement"
      temperature: 0.4
      
validation:
  quality_gates:
    - "length_check"
    - "logical_coherence"
    - "quality_standards"
    - "technical_compliance"
```

---

## 🔧 **Troubleshooting**

### Validation Failures

**Problem**: "Prompt exceeds length limit"
```
Validation Failed: FAIL - Prompt length 4,523 chars exceeds limit 4,096
```

**Solution**: Run prompt optimizer, reduce research data verbosity
```python
# Check optimizer settings
optimizer.target_length = 2800  # More aggressive
optimizer.condense_research_data = True
```

**Problem**: "Logical coherence check failed"
```
Validation Failed: Contradictions found - "clean surface" AND "heavy oxidation"
```

**Solution**: Review stage outputs, ensure contamination level consistent
```python
# Check contamination level
config.contamination_level = 5  # Moderate (not 1 or 10)
```

### Generation Failures

**Problem**: "API error: Invalid aspect ratio"
```
Error: aspect_ratio='wide' not supported by Imagen 4
```

**Solution**: Use valid aspect ratios
```python
# Valid options
aspect_ratio="16:9"    # ✅ Landscape
aspect_ratio="9:16"    # ✅ Portrait
aspect_ratio="1:1"     # ✅ Square
aspect_ratio="wide"    # ❌ Invalid
```

**Problem**: "Insufficient contamination detail"
```
Generated image shows minimal contamination despite level 8/10
```

**Solution**: Verify contamination_patterns in YAML data, increase pattern specificity
```yaml
# Materials.yaml
contamination_patterns:
  rust:
    severity_8:
      description: "Heavy oxidation with 70% surface coverage"
      visual_cues: "Deep rust pitting, flaking, structural impact"
```

### Learning System Issues

**Problem**: "Database locked"
```
SQLite Error: database is locked
```

**Solution**: Close analytics tool before generating, use read-only mode
```bash
# Use read-only
python3 domains/materials/image/learning/analytics.py attempts --readonly
```

**Problem**: "No learning data available"
```
Analytics: No attempts found in database
```

**Solution**: Generate at least one image to populate learning data
```bash
python3 domains/materials/image/generate.py "Steel"
```

---

## 📚 **Related Documentation**

### Architecture
- **Architecture Overview**: `docs/02-architecture/ARCHITECTURE_OVERVIEW.md` - System architecture
- **Domain Independence**: `docs/02-architecture/DOMAIN_ARCHITECTURE.md`
- **Image Architecture**: `docs/02-architecture/IMAGE_ARCHITECTURE.md`

### Policies
- **Prompt Chaining**: `docs/08-development/PROMPT_CHAINING_POLICY.md`
- **Hardcoded Values**: `docs/08-development/HARDCODED_VALUE_POLICY.md`

### Implementation
- **Orchestrator Integration**: `docs/archive/2025-11/ORCHESTRATOR_VALIDATION_INTEGRATION_NOV27_2025.md`
- **Validation System**: `docs/06-ai-systems/VALIDATION_SYSTEM.md`
- **Learning System**: `docs/06-ai-systems/LEARNING_SYSTEM.md`

### Quick References
- **AI Assistant Guide**: `docs/08-development/AI_ASSISTANT_GUIDE.md`
- **Quick Reference**: `docs/QUICK_REFERENCE.md`
- **Troubleshooting**: `TROUBLESHOOTING.md`

---

## 🎯 **Best Practices**

### For AI Assistants
1. **Always use domain adapter pattern** - Don't pass domain-specific params to orchestrator
2. **Validate before generation** - Use PromptValidator before API calls
3. **Log ALL attempts** - Success and failure both valuable for learning
4. **Respect contamination levels** - 1=minimal, 5=moderate, 10=severe
5. **Check YAML data completeness** - Verify visual_appearance and contamination_patterns exist

### For Developers
1. **Start with research** - Ensure YAML data is complete before generation
2. **Test validation separately** - Use validator independently before full pipeline
3. **Monitor learning database** - Review patterns to improve prompts
4. **Respect prompt limits** - Keep positive < 2,800 chars (target), < 4,096 (hard limit)
5. **Use analytics** - Identify successful patterns and replicate them

### For Content Creators
1. **Choose appropriate contamination level** - Match real-world severity
2. **Verify output quality** - Check before/after split is clear
3. **Review contamination accuracy** - Ensure patterns match real oxidation/dirt/coatings
4. **Test multiple materials** - Different materials may need different contamination levels
5. **Provide feedback** - Log issues for learning system improvement

---

## 📊 **Metrics & Success Criteria**

### Quality Metrics
- **Validation Pass Rate**: Target 90%+ (currently varies by domain)
- **Generation Success Rate**: Target 95%+ (after validation)
- **Prompt Optimization**: Target < 3,000 chars positive (currently ~2,800)
- **Learning Data Growth**: Target 100+ attempts/month per domain

### Performance Metrics
- **Validation Time**: < 1 second
- **Generation Time**: 5-15 seconds (Imagen 4 API)
- **Total Pipeline**: < 20 seconds end-to-end
- **Database Query Time**: < 100ms

### Content Quality
- **Contamination Accuracy**: Visual match to specified level (1-10)
- **Before/After Clarity**: Clear split, consistent lighting
- **Technical Accuracy**: Realistic material appearance
- **Composition Quality**: Professional layout, proper framing

---

**Last Major Update**: November 28, 2025 - Orchestrator validation integration, learning system restoration, documentation consolidation