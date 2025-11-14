# Flexible Architecture Guide

## Overview

The new processing pipeline supports **flexible component types** and **content domains** without creating redundant generators. You can generate different text types (subtitle, caption, description, FAQ, troubleshooter) for different domains (materials, settings) using the same unified system.

## Supported Component Types

1. **subtitle** (15 words) - Concise, punchy summary without ending period
2. **caption** (25 words) - Technical description with measurements
3. **description** (150 words) - Comprehensive overview with details
4. **faq** (100 words) - Question-and-answer format
5. **troubleshooter** (120 words) - Problem diagnosis and solution steps

## Supported Content Domains

1. **materials** - Physical properties, industrial applications, laser cleaning characteristics
2. **settings** - Machine parameters, optimal ranges, adjustment guidelines

## Usage Examples

### Basic Material Subtitle
```python
from processing.orchestrator import Orchestrator
from shared.api.grok_client import GrokClient

orchestrator = Orchestrator(GrokClient())

result = orchestrator.generate(
    topic="Aluminum",
    component_type="subtitle",
    author_id=2,  # Italian author
    length=15,  # Optional - uses component default if omitted
    domain="materials"  # Optional - defaults to "materials"
)

if result['success']:
    print(result['text'])
    # Example output: "Removes oxide layers while preserving aluminum's natural finish"
```

### Material Description
```python
result = orchestrator.generate(
    topic="Stainless Steel",
    component_type="description",
    author_id=1,
    # length omitted - uses component default (150 words)
    domain="materials"
)

# Generates comprehensive 150-word description with:
# - Properties and characteristics
# - Applications and use cases
# - Laser cleaning process details
# - Benefits and advantages
```

### Settings-Based FAQ
```python
result = orchestrator.generate(
    topic="Laser Power",
    component_type="faq",
    author_id=3,  # Indonesian author
    context="Common questions about power settings for different materials",
    domain="settings"
)

# Generates FAQ-style content like:
# Q: What power setting should I use for aluminum?
# A: For aluminum cleaning, typical power settings range from...
```

### Troubleshooting Guide
```python
result = orchestrator.generate(
    topic="Inconsistent Cleaning Results",
    component_type="troubleshooter",
    author_id=4,  # Taiwanese author
    context="Users report uneven cleaning patterns on stainless steel",
    domain="settings"
)

# Generates step-by-step troubleshooting:
# 1. Check power consistency across scan area
# 2. Verify focal distance is maintained
# 3. Adjust pulse overlap for uniform coverage...
```

### Batch Generation
```python
# Generate subtitles for multiple materials
results = orchestrator.batch_generate(
    topics=["Aluminum", "Brass", "Copper"],
    component_type="subtitle",
    author_id=2,
    domain="materials"
)

for topic, result in results.items():
    if result['success']:
        print(f"{topic}: {result['text']}")
        print(f"AI Score: {result['ai_score']}")
```

## Adding New Component Types

You can add custom component types without modifying core code:

```python
from processing.generation.component_specs import ComponentSpec, ComponentRegistry

# Define new component
custom_spec = ComponentSpec(
    name='quick_tip',
    default_length=30,
    min_length=25,
    max_length=35,
    format_rules='Single actionable tip; imperative voice',
    focus_areas='One specific technique or best practice',
    style_notes='Direct and practical; focus on what user should do',
    end_punctuation=True
)

# Register it
ComponentRegistry.register(custom_spec)

# Now you can use it
result = orchestrator.generate(
    topic="Surface Preparation",
    component_type="quick_tip",
    author_id=1
)
```

## Adding New Content Domains

Extend DomainContext for new domains:

```python
from processing.generation.component_specs import DomainContext

# Add method to DomainContext class
@classmethod
def safety(cls) -> 'DomainContext':
    """Context for safety procedures domain"""
    return cls(
        domain='safety',
        focus_template='Safety procedures, protective equipment, hazard warnings, compliance requirements',
        enrichment_strategy='Extract safety data sheets, regulatory standards, PPE requirements',
        example_facts='Eye protection: OD 6+ @ 1064nm; Enclosure: Class 1 laser product',
        terminology_style='Clear and authoritative; emphasize compliance; use imperative voice for procedures'
    )

# Use it
result = orchestrator.generate(
    topic="Laser Eye Safety",
    component_type="troubleshooter",
    author_id=1,
    domain="safety"
)
```

## Backward Compatibility

The system maintains backward compatibility with old code:

```python
# Old signature (still works)
result = orchestrator.generate(
    material="Aluminum",  # Uses 'material' param
    component_type="subtitle",
    author_id=2,
    length=15
)

# New signature (preferred)
result = orchestrator.generate(
    topic="Aluminum",  # Uses 'topic' param
    component_type="subtitle",
    author_id=2,
    length=15,
    domain="materials"
)
```

## Benefits of This Architecture

### 1. No Code Duplication
- Single `Orchestrator` handles all component types and domains
- No need for separate generators (SubtitleGenerator, CaptionGenerator, etc.)
- Changes propagate automatically to all components

### 2. Easy Extension
- Add new component types via `ComponentRegistry`
- Add new domains via `DomainContext`
- No core code changes required

### 3. Consistent Quality
- Same AI detection ensemble for all content
- Same readability validation for all content
- Same voice profiles and ESL traits

### 4. Flexible Prompting
- Component specs define requirements
- Domain contexts provide guidance
- Additional `context` parameter for specific needs

### 5. Type Safety
- Component specs validated at runtime
- Clear error messages for unknown types
- IDE autocomplete support

## Architecture Flow

```
Input (topic, component_type, domain)
    ↓
ComponentRegistry.get_spec(component_type)
    ↓
DomainContext.get_domain(domain)
    ↓
DataEnricher.fetch_real_facts(topic)
    ↓
PromptBuilder.build_unified_prompt(
    topic + voice + facts + spec + domain_ctx
)
    ↓
API Call (Single Pass)
    ↓
AIDetectorEnsemble.detect(text)
    ↓
ReadabilityValidator.validate(text)
    ↓
Pass? → Return Success
Fail? → Adjust Prompt → Retry (max 5)
```

## Configuration

All component types and their specifications are in:
- `processing/generation/component_specs.py`

Default settings in:
- `processing/config.yaml`

To modify a component's behavior:
1. Edit its `ComponentSpec` in `component_specs.py`
2. Changes apply immediately to all future generations
3. No need to restart or redeploy

## Testing Different Components

```python
# Test all component types for a material
material = "Aluminum"
component_types = ["subtitle", "caption", "description", "faq", "troubleshooter"]

for comp_type in component_types:
    print(f"\n{'='*60}")
    print(f"Testing {comp_type} for {material}")
    print(f"{'='*60}")
    
    result = orchestrator.generate(
        topic=material,
        component_type=comp_type,
        author_id=2
    )
    
    if result['success']:
        print(f"✅ Text: {result['text'][:100]}...")
        print(f"Length: {len(result['text'].split())} words")
        print(f"AI Score: {result['ai_score']:.3f}")
    else:
        print(f"❌ Failed: {result['reason']}")
```

## Best Practices

### 1. Use Component Defaults
```python
# Good - uses component's default length
result = orchestrator.generate(topic="Steel", component_type="description", author_id=1)

# Also fine - override if needed
result = orchestrator.generate(topic="Steel", component_type="description", author_id=1, length=200)
```

### 2. Provide Context for Complex Topics
```python
# Good - provides specific context
result = orchestrator.generate(
    topic="Laser Power Settings",
    component_type="faq",
    author_id=2,
    context="Focus on common mistakes beginners make with power adjustments",
    domain="settings"
)
```

### 3. Match Domain to Topic
```python
# Good - materials domain for material topics
result = orchestrator.generate(topic="Brass", domain="materials", ...)

# Good - settings domain for parameter topics
result = orchestrator.generate(topic="Pulse Duration", domain="settings", ...)
```

### 4. Let AI Detection Work
```python
# System automatically retries on high AI scores
# Max 5 attempts with dynamic prompt adjustment
# No need to manually handle retries
result = orchestrator.generate(...)

if result['success']:
    # Content passed AI detection and readability checks
    save_to_database(result['text'])
```

## Troubleshooting

### "Unknown component type" Error
- Check spelling: must match exactly (lowercase)
- Available types: subtitle, caption, description, faq, troubleshooter
- Add custom types via `ComponentRegistry.register()`

### "Unknown domain" Error
- Check spelling: must be 'materials' or 'settings'
- Add custom domains by extending `DomainContext`

### High AI Scores
- System automatically retries with adjusted prompts
- If all attempts fail, check `processing/config.yaml` forbidden_patterns
- Consider lowering `ai_threshold` (default: 0.3)

### Wrong Text Length
- Specify `length` parameter explicitly
- Check component's default in `ComponentSpec`
- System allows ±2 words variance by default

---

**Summary**: This flexible architecture lets you generate any component type for any domain without duplicating code. Add new types and domains easily. Maintain consistency across all content.
