# Prompt Management System Documentation

## Overview

The Z-Beam content generation system uses a sophisticated three-layer prompt architecture that requires careful management and versioning. This document provides comprehensive procedures for managing, updating, and versioning prompts across the system.

## Current Prompt Architecture

### Three-Layer System Structure

```
components/content/prompts/
├── base_content_prompt.yaml          # Core guidance and author configurations
├── personas/                         # Author-specific writing styles
│   ├── taiwan_persona.yaml          # Author ID: 1 (380 words max)
│   ├── italy_persona.yaml           # Author ID: 2 (450 words max)
│   ├── indonesia_persona.yaml       # Author ID: 3 (250 words max)
│   └── usa_persona.yaml             # Author ID: 4 (320 words max)
├── formatting/                       # Author-specific formatting rules
│   ├── taiwan_formatting.yaml       # Systematic, methodical style
│   ├── italy_formatting.yaml        # Technical elegance
│   ├── indonesia_formatting.yaml    # Direct, practical style
│   └── usa_formatting.yaml          # Conversational, innovative style
└── README.md                         # This documentation
```

### Layer Responsibilities

1. **Base Layer** (`base_content_prompt.yaml`)
   - Core content guidance questions
   - Author expertise areas and word limits
   - Required content sections
   - Randomization guidelines

2. **Persona Layer** (`personas/{country}_persona.yaml`)
   - Author-specific writing styles
   - Linguistic patterns and cultural elements
   - Signature phrases and personality traits
   - Technical focus areas

3. **Formatting Layer** (`formatting/{country}_formatting.yaml`)
   - Markdown formatting preferences
   - Header and emphasis styles
   - List formatting rules
   - Presentation guidelines

## Prompt Update Procedures

### Pre-Update Checklist

**BEFORE making ANY changes to prompt files:**

1. **Read Documentation First**
   ```bash
   # Review the comprehensive prompt system documentation
   cat components/content/docs/PROMPT_SYSTEM.md
   cat components/content/docs/CONTENT_GENERATION_ARCHITECTURE.md
   ```

2. **Understand Dependencies**
   - Check how prompts are loaded in `fail_fast_generator.py`
   - Review prompt construction process (12-step layered building)
   - Understand caching strategy (`@lru_cache` usage)

3. **Backup Current State**
   ```bash
   # Create timestamped backup before any changes
   TIMESTAMP=$(date +%Y%m%d_%H%M%S)
   cp -r components/content/prompts components/content/prompts_backup_$TIMESTAMP
   ```

4. **Test Current Functionality**
   ```bash
   # Run existing tests to establish baseline
   python -m pytest tests/test_content_generation.py -v
   ```

### Update Process by Layer

#### 1. Base Layer Updates (`base_content_prompt.yaml`)

**When to Update:**
- Adding new core guidance questions
- Modifying author expertise areas
- Changing word count limits
- Updating content structure requirements

**Procedure:**
```yaml
# Example: Adding new guidance question
overall_subject:
  - "What is special about the material?"
  - "How does it differ from others in the category?"
  - "What is it often used for?"
  - "What is it like to laser clean?"
  - "What special challenges or advantages does it present?"
  - "What should the results look like?"
  - "NEW: How does this material behave under different environmental conditions?"
```

**Validation Steps:**
1. Check YAML syntax: `python -c "import yaml; yaml.safe_load(open('base_content_prompt.yaml'))"`
2. Test prompt construction: Generate sample content
3. Verify all authors still work with new guidance

#### 2. Persona Layer Updates (`personas/{country}_persona.yaml`)

**When to Update:**
- Refining linguistic patterns
- Adding/removing signature phrases
- Adjusting personality traits
- Modifying technical focus areas

**Procedure:**
```yaml
# Example: Adding new signature phrase to Taiwan persona
signature_phrases:
  - "This is important, very important"
  - "In practice, it show"
  - "It works good, really good"
  - "Must consider carefully, very carefully"
  - "Together, it help"
  - "Maybe, I think"
  - "Already finish, done"
  - "NEW: Systematic approach enables"
```

**Cultural Authenticity Guidelines:**
- Maintain linguistic patterns (20-40% of sentences)
- Preserve cultural elements and personality traits
- Ensure signature phrases enhance rather than dominate
- Test for natural flow and readability

#### 3. Formatting Layer Updates (`formatting/{country}_formatting.yaml`)

**When to Update:**
- Changing markdown preferences
- Modifying header styles
- Updating list formatting rules
- Adjusting emphasis patterns

**Procedure:**
```yaml
# Example: Updating Italy formatting for technical elegance
markdown_formatting:
  headers:
    main_title: "# for main title with elegant spacing"
    section_headers: "## for sections with clear hierarchy"
    subsection_headers: "### for technical subsections"
  emphasis:
    critical_info: "**bold** for key technical information"
    formulas: "simple notation without excessive markup"
    parameters: "**bold** for laser parameters and specifications"
```

### Post-Update Validation

#### 1. Syntax Validation
```bash
# Validate all YAML files
find components/content/prompts -name "*.yaml" -exec python -c "
import yaml, sys
try:
    with open('{}') as f:
        yaml.safe_load(f)
    print('✓ {}: Valid YAML')
except Exception as e:
    print('✗ {}: {}'.format(sys.argv[1], e))
" {} \;
```

#### 2. Functional Testing
```python
# Test prompt construction for each author
from components.content.generators.fail_fast_generator import FailFastContentGenerator

generator = FailFastContentGenerator()
for author_id in [1, 2, 3, 4]:  # Taiwan, Italy, Indonesia, USA
    try:
        # Test prompt building
        prompt = generator._build_prompt(material_data, author_id)
        print(f"✓ Author {author_id}: Prompt built successfully ({len(prompt)} chars)")
    except Exception as e:
        print(f"✗ Author {author_id}: {e}")
```

#### 3. Content Generation Testing
```python
# Generate test content for each author
test_material = {
    "name": "Aluminum",
    "chemical_formula": "Al",
    "properties": {"density": "2.7 g/cm³", "melting_point": "660°C"}
}

for author_id in [1, 2, 3, 4]:
    try:
        result = generator.generate("Aluminum", test_material, api_client, author_id=author_id)
        word_count = len(result.content.split())
        print(f"✓ Author {author_id}: Generated {word_count} words")
    except Exception as e:
        print(f"✗ Author {author_id}: {e}")
```

#### 4. Quality Scoring (Optional)
```python
# If quality scoring is enabled
from components.content.validation.content_scorer import ContentScorer

scorer = ContentScorer()
for author_id in [1, 2, 3, 4]:
    result = generator.generate("Aluminum", test_material, api_client, author_id=author_id)
    scores = scorer.score_content(result.content, author_id)
    print(f"Author {author_id} Quality: {scores['overall_score']:.1f}")
```

## Version Control Strategy

### Git Workflow for Prompt Updates

#### 1. Branch Strategy
```bash
# Create feature branch for prompt updates
git checkout -b feature/prompt-update-taiwan-persona-2024q1

# Make changes to prompt files
# ... edit files ...

# Commit with descriptive message
git add components/content/prompts/personas/taiwan_persona.yaml
git commit -m "feat: enhance Taiwan persona linguistic patterns

- Add systematic approach signature phrases
- Refine Mandarin-influenced language patterns
- Improve cultural authenticity for semiconductor focus
- Tested with Aluminum material generation"
```

#### 2. Version Tagging
```bash
# Tag prompt system versions
git tag -a v2.1.0-prompts -m "Prompt System v2.1.0
- Enhanced Taiwan persona linguistic patterns
- Improved Italy formatting for technical elegance
- Updated base guidance questions
- All authors validated with quality scores >80"
```

### Change Documentation

#### 1. Change Log Format
```markdown
# Prompt System Change Log

## v2.1.0 (2024-01-XX)
### Enhancements
- **Taiwan Persona**: Added systematic approach signature phrases
- **Italy Formatting**: Improved technical elegance presentation
- **Base Guidance**: Added environmental conditions question

### Validation Results
- All authors generate within word limits
- Quality scores maintained >80 for all personas
- YAML syntax validated across all files

### Testing
- Generated test content for Aluminum, Steel, Plastic
- Verified prompt construction for all 4 authors
- Confirmed backward compatibility
```

#### 2. Impact Assessment
**Before committing prompt changes:**
- [ ] Document which authors are affected
- [ ] Note any word count limit changes
- [ ] Record quality score impacts
- [ ] List any breaking changes to prompt structure

## Monitoring and Maintenance

### Regular Health Checks

#### 1. Weekly Validation
```bash
# Automated prompt validation script
#!/bin/bash
echo "=== Weekly Prompt System Health Check ==="

# Check file existence
for file in base_content_prompt.yaml personas/*.yaml formatting/*.yaml; do
    if [ ! -f "components/content/prompts/$file" ]; then
        echo "✗ Missing: $file"
    else
        echo "✓ Found: $file"
    fi
done

# Validate YAML syntax
echo -e "\n=== YAML Validation ==="
find components/content/prompts -name "*.yaml" -exec python -c "
import yaml, sys
try:
    yaml.safe_load(open('{}'))
    print('✓ {}')
except Exception as e:
    print('✗ {}: {}'.format(sys.argv[1], e))
" {} \;

# Test prompt construction
echo -e "\n=== Prompt Construction Test ==="
python -c "
from components.content.generators.fail_fast_generator import FailFastContentGenerator
generator = FailFastContentGenerator()
# Test basic prompt building
print('✓ Prompt construction functional')
"
```

#### 2. Performance Monitoring
```python
# Monitor prompt building performance
import time
from components.content.generators.fail_fast_generator import FailFastContentGenerator

generator = FailFastContentGenerator()

start_time = time.time()
for i in range(100):
    prompt = generator._build_prompt(test_material, author_id=1)
build_time = time.time() - start_time

print(f"Average prompt build time: {build_time/100:.3f} seconds")
print(f"Cache hit ratio: {generator._cache_info().hit_rate:.2%}")
```

### Quality Metrics Tracking

#### 1. Generation Quality Dashboard
```python
# Track quality metrics over time
quality_history = {
    'taiwan': [],
    'italy': [],
    'indonesia': [],
    'usa': []
}

# After each generation
scores = scorer.score_content(content, author_id)
quality_history[author_country].append({
    'timestamp': datetime.now(),
    'overall_score': scores['overall_score'],
    'human_believability': scores['human_believability'],
    'word_count': len(content.split())
})
```

#### 2. Author Performance Analysis
```python
# Analyze author-specific performance
for author, history in quality_history.items():
    if history:
        avg_score = sum(h['overall_score'] for h in history) / len(history)
        avg_words = sum(h['word_count'] for h in history) / len(history)
        print(f"{author}: {avg_score:.1f} quality, {avg_words:.0f} avg words")
```

## Troubleshooting Common Issues

### Configuration Errors

#### Missing Required Sections
```yaml
# Error: Missing 'language_patterns' in persona
# Fix: Add required section
language_patterns:
  signature_phrases:
    - "required phrase"
  vocabulary: "style description"
```

#### Invalid YAML Syntax
```bash
# Use YAML validator
python -c "import yaml; yaml.safe_load(open('file.yaml'))"
```

#### Author Mapping Issues
```python
# Check author ID mapping
author_mapping = {
    1: 'taiwan',
    2: 'italy', 
    3: 'indonesia',
    4: 'usa'
}
```

### Generation Issues

#### Word Count Violations
```python
# Check word count limits
word_limits = {
    1: 380,  # Taiwan
    2: 450,  # Italy
    3: 250,  # Indonesia
    4: 320   # USA
}

content_words = len(generated_content.split())
if content_words > word_limits[author_id] * 1.2:  # 20% tolerance
    print(f"Word count violation: {content_words} > {word_limits[author_id]}")
```

#### Quality Score Degradation
```python
# Monitor quality score trends
if scores['overall_score'] < 75.0:
    print("Quality score below threshold - prompt refinement needed")
    # Log for analysis
    logging.warning(f"Low quality score for author {author_id}: {scores['overall_score']}")
```

## Best Practices

### 1. Incremental Changes
- Make small, targeted changes rather than large rewrites
- Test each change individually before combining
- Maintain backward compatibility where possible

### 2. Documentation Updates
- Update this document when changing procedures
- Document all prompt changes in commit messages
- Maintain change log for version tracking

### 3. Testing Strategy
- Test all authors after any prompt changes
- Validate with multiple material types
- Monitor quality metrics for regressions

### 4. Backup Strategy
- Always backup before changes
- Keep multiple versions for rollback
- Document rollback procedures

### 5. Collaboration Guidelines
- Communicate prompt changes to team
- Review changes before committing
- Share validation results

## Emergency Rollback Procedures

### Immediate Rollback
```bash
# If prompt changes break generation
git checkout HEAD~1 -- components/content/prompts/
git checkout HEAD~1 -- components/content/generators/fail_fast_generator.py

# Or rollback to specific backup
cp -r components/content/prompts_backup_20240101_143000 components/content/prompts
```

### Validation After Rollback
```bash
# Test that rollback restored functionality
python -m pytest tests/test_content_generation.py
python test_content_generation.py  # Generate test content
```

This comprehensive prompt management system ensures consistent, high-quality content generation while maintaining the sophisticated multi-layered architecture that makes the Z-Beam system effective.
