# Architecture Design: Flexibility Without Redundancy

## Design Goals

Create a content generation system that:
1. **Handles multiple text types** (subtitle, caption, description, FAQ, troubleshooter)
2. **Works across domains** (materials, settings, and extensible to more)
3. **Avoids code duplication** (single generator, not one per type)
4. **Maintains quality** (consistent AI detection, readability, voice)
5. **Enables easy extension** (add new types/domains without refactoring)

## How We Achieved It

### Problem: Traditional Approach Creates Redundancy

**Anti-Pattern** (What we AVOIDED):
```python
# ❌ Creates code duplication and maintenance nightmare
class SubtitleGenerator:
    def generate(self, material, author_id, length=15):
        # Subtitle-specific logic
        pass

class CaptionGenerator:
    def generate(self, material, author_id, length=25):
        # Caption-specific logic (90% same as above)
        pass

class DescriptionGenerator:
    def generate(self, material, author_id, length=150):
        # Description-specific logic (90% same as above)
        pass

# Problem: Changes to AI detection need updating in 3+ places
# Problem: Voice consistency must be maintained across 3+ generators
# Problem: Adding new type requires entire new class
```

### Solution: Specification-Driven Single Generator

**Our Approach**:
```python
# ✅ Single generator with dynamic behavior
class Orchestrator:
    def generate(self, topic, component_type, author_id, length=None, domain="materials"):
        # Get component specifications
        spec = ComponentRegistry.get_spec(component_type)
        domain_ctx = DomainContext.get_domain(domain)
        
        # Build prompt using specs (not hardcoded templates)
        prompt = PromptBuilder.build_unified_prompt(
            topic, voice, spec, domain_ctx, ...
        )
        
        # Same workflow for all types
        text = self._call_api(prompt)
        detection = self.detector.detect(text)
        readability = self.validator.validate(text)
        
        # Retry logic works for all types
        if not acceptable:
            adjust_prompt_and_retry()
```

**Benefits**:
- ✅ One codebase for all types
- ✅ Changes propagate automatically
- ✅ Consistent quality across all types
- ✅ Easy to add new types

## Key Architectural Patterns

### 1. Specification Registry Pattern

Instead of hardcoding component behavior, we define specifications:

```python
ComponentSpec(
    name='subtitle',
    default_length=15,
    format_rules='No period at end; concise and punchy',
    focus_areas='Unique characteristics, key benefits',
    style_notes='Professional but natural; vary structure',
    end_punctuation=False
)
```

**Why this works**:
- Behavior is data, not code
- Add new types by adding data, not classes
- Modify behavior by editing specs, not refactoring code
- Specs are self-documenting

### 2. Domain Context Pattern

Content domains provide guidance without hardcoding:

```python
DomainContext.materials() → {
    'focus_template': 'Physical properties, applications, cleaning characteristics',
    'enrichment_strategy': 'Extract from Materials.yaml',
    'terminology_style': 'Technical but accessible'
}

DomainContext.settings() → {
    'focus_template': 'Operating parameters, optimal ranges, effects',
    'enrichment_strategy': 'Extract machineSettings',
    'terminology_style': 'Precise with units; cite ranges'
}
```

**Why this works**:
- Domain-specific guidance without separate generators
- Same orchestrator adapts to domain automatically
- Easy to add new domains (history, safety, recipes)
- Clean separation of concerns

### 3. Template-Free Prompt Building

Instead of hardcoded templates per type, we build dynamically:

```python
def _build_spec_driven_prompt(topic, spec, domain_ctx, voice, facts):
    return f"""You are {author}, writing a {spec.name} about {topic}.

FACTS: {facts}
FOCUS: {spec.focus_areas}
DOMAIN: {domain_ctx.focus_template}

REQUIREMENTS:
- Length: {spec.default_length} words
- Format: {spec.format_rules}
- Style: {spec.style_notes}

VOICE: {voice.esl_traits}

Generate {spec.name}:"""
```

**Why this works**:
- No if/elif chains for each type
- Prompt adapts to any component spec
- Adding new type doesn't require new prompt template
- All types benefit from same anti-AI strategies

## Avoiding Common Pitfalls

### Pitfall 1: Over-Generalization

**Problem**: Making system too generic loses type-specific nuances.

**Our Solution**: ComponentSpec captures type-specific requirements while keeping orchestration generic.

```python
# Specific enough
ComponentSpec(
    name='faq',
    format_rules='Question-and-answer format; direct response',
    style_notes='Conversational yet authoritative; use second person'
)

# But general workflow
orchestrator.generate(topic, "faq", ...)  # Same method for all types
```

### Pitfall 2: Prompt Bloat

**Problem**: Long prompts hit API token limits.

**Our Solution**: 
- Keep specs concise (100-200 chars each)
- Use `context` parameter for optional details
- DataEnricher provides facts separately

```python
# Base prompt ~500 tokens
# + Facts ~200 tokens
# + Optional context ~100 tokens
# Total: ~800 tokens (well under 4K limit)
```

### Pitfall 3: Detection Slippage

**Problem**: Different text types might trigger AI detectors differently.

**Our Solution**: 
- Same ensemble detector for all types
- Same forbidden patterns for all types
- Type-specific length adjustments handled in readability validation

```python
# FAQ might be more conversational → same detector still works
# Troubleshooter might be more technical → same detector still works
# Detector looks at linguistic patterns, not content type
```

### Pitfall 4: Fact Accuracy Across Domains

**Problem**: Materials domain enricher won't work for settings domain.

**Our Solution**: DataEnricher adapts based on topic/domain.

```python
class DataEnricher:
    def fetch_real_facts(self, topic, domain="materials"):
        material_data = self._load_materials().get(topic, {})
        
        if domain == "materials":
            # Extract properties, applications
            return self._extract_material_facts(material_data)
        elif domain == "settings":
            # Extract machineSettings
            return self._extract_setting_facts(material_data)
```

## Extensibility Examples

### Adding New Component Type

```python
# 1. Define spec (5 lines)
ComponentSpec(
    name='glossary_entry',
    default_length=40,
    format_rules='Term definition with technical precision',
    focus_areas='Precise meaning, context, examples',
    style_notes='Academic but clear; cite related terms'
)

# 2. Register it (1 line)
ComponentRegistry.register(glossary_spec)

# 3. Use it (no code changes)
result = orchestrator.generate(topic="Ablation", component_type="glossary_entry", ...)
```

**Total effort**: ~10 lines of configuration, zero code changes.

### Adding New Domain

```python
# 1. Add domain context method (10 lines)
@classmethod
def safety(cls):
    return cls(
        domain='safety',
        focus_template='Procedures, PPE, hazards, compliance',
        enrichment_strategy='Extract safety data sheets',
        terminology_style='Clear and authoritative; imperative voice'
    )

# 2. Update get_domain() mapping (1 line)
method_map = {'materials': ..., 'settings': ..., 'safety': cls.safety}

# 3. Use it (no other changes)
result = orchestrator.generate(topic="Eye Protection", domain="safety", ...)
```

**Total effort**: ~15 lines of configuration, zero refactoring.

## Performance Characteristics

### Memory
- **Specification registry**: ~5KB for all component specs
- **Domain contexts**: ~2KB for all domains
- **Orchestrator**: Single instance, minimal overhead
- **Total overhead**: < 10KB vs separate generators

### Speed
- **No performance penalty** from abstraction
- Specs looked up once per generation (~0.1ms)
- Same API call overhead for all types
- Retry logic identical across types

### Code Complexity
- **Single orchestrator**: ~200 lines
- **Component specs**: ~150 lines
- **Domain contexts**: ~100 lines
- **Total**: ~450 lines vs. 1000+ lines for separate generators

## Comparison: Traditional vs. Flexible Architecture

| Aspect | Traditional (Separate Generators) | Flexible (This Architecture) |
|--------|-----------------------------------|------------------------------|
| **Code volume** | ~1000+ lines (5 generators × 200 lines) | ~450 lines (shared orchestrator) |
| **Add new type** | Create full new class (~200 lines) | Add ComponentSpec (~10 lines) |
| **Consistency** | Must maintain manually across 5+ files | Automatic (single codebase) |
| **Testing** | Test each generator separately | Test once, applies to all |
| **Maintenance** | Update 5+ places for fixes | Update once, propagates |
| **Voice consistency** | Duplicate voice logic 5+ times | Single voice system |
| **AI detection** | Duplicate detector 5+ times | Single ensemble detector |
| **Extensibility** | Requires subclassing/refactoring | Add data, not code |

## Real-World Example

User wants to generate content for a material:

```python
# Generate complete content set for Aluminum
orchestrator = Orchestrator(api_client)

content = {}
for component_type in ['subtitle', 'caption', 'description', 'faq', 'troubleshooter']:
    result = orchestrator.generate(
        topic="Aluminum",
        component_type=component_type,
        author_id=2,  # Italian author for consistency
        domain="materials"
    )
    content[component_type] = result['text']

# All generated with:
# - Same voice (Italian ESL traits)
# - Same AI detection (ensemble validation)
# - Same readability (Flesch 60-80)
# - Type-appropriate length and format
# - Consistent factual grounding

# No need for:
# SubtitleGenerator, CaptionGenerator, DescriptionGenerator, etc.
```

## Conclusion

This architecture achieves **flexibility without redundancy** by:

1. **Separating specification from implementation**
   - ComponentSpec = what to generate
   - Orchestrator = how to generate
   - No coupling between type and logic

2. **Using composition over inheritance**
   - Single orchestrator + multiple specs
   - Not SubtitleGenerator extends BaseGenerator

3. **Making behavior data-driven**
   - Add types by adding data
   - Not by adding code

4. **Maintaining single source of truth**
   - One detector, one validator, one voice system
   - All types benefit from improvements

5. **Enabling runtime extensibility**
   - Register new types without restart
   - Modify specs without recompilation

**Result**: System handles 5 component types × 2 domains = 10 combinations with ~450 lines of code, and can scale to 20+ types × 5+ domains = 100+ combinations with minimal additional code.
