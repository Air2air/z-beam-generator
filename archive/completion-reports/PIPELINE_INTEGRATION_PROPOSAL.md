# Pipeline Integration Proposal: Inline Content Validation

## Overview

Integrate `ContentValidator` into the generation pipeline to catch quality issues **before** content is persisted to `Materials.yaml` or exported to frontmatter.

---

## 1. Integration Points

### Option A: **Fail-Fast Mode** (Recommended for Production)

```python
# In faq_generator.py, after FAQ generation but before saving

from validation.content_validator import ContentValidator, ValidationError

def generate(self, material_name: str, ...):
    # ... existing generation code ...
    
    # Parse generated FAQ
    faq_items = yaml.safe_load(faq_content)
    
    # VALIDATE BEFORE SAVING
    validator = ContentValidator(strict_mode=True)  # Fail-fast
    try:
        report = validator.validate_faq(
            faq_items,
            word_count_range=(20, 50),
            max_repetition_threshold=0.60,
            min_variation_score=0.40
        )
        logger.info(f"✅ FAQ validation passed (score: {report['quality_score']:.0f}/100)")
    except ValidationError as e:
        logger.error(f"❌ FAQ validation failed: {e}")
        return self._create_result("", success=False, error_message=str(e))
    
    # Only save if validation passes
    self._write_to_materials(material_name, faq_items, timestamp)
    return self._create_result(faq_content, success=True)
```

**Benefits:**
- ✅ Zero defective content reaches Materials.yaml
- ✅ Fail-fast aligns with project philosophy (GROK_INSTRUCTIONS.md)
- ✅ Forces AI regeneration on quality failures
- ✅ Clear error messages for debugging

**Drawbacks:**
- ⚠️ May require multiple API calls if content fails validation
- ⚠️ Could increase generation time by 10-20% (worth it for quality)

---

### Option B: **Warning Mode** (Development/Testing)

```python
# In faq_generator.py, after generation

validator = ContentValidator(strict_mode=False)  # Warning only
report = validator.validate_faq(faq_items, ...)

# Log issues but don't block
if not report['valid']:
    logger.warning(f"⚠️ Quality issues detected:")
    for error in report['errors']:
        logger.warning(f"  • {error}")
    for warning in report['warnings']:
        logger.warning(f"  • {warning}")

# Save anyway (for testing)
self._write_to_materials(material_name, faq_items, timestamp)
```

**Benefits:**
- ✅ See quality reports without blocking workflow
- ✅ Good for development and tuning thresholds
- ✅ Collect data on typical quality scores

**Drawbacks:**
- ❌ Allows defective content into system
- ❌ Requires manual review

---

### Option C: **Hybrid Mode** (Recommended for Development → Production)

```python
# Use environment variable to control mode
import os

strict_mode = os.getenv('VALIDATION_STRICT_MODE', 'false').lower() == 'true'
validator = ContentValidator(strict_mode=strict_mode)

# Development: VALIDATION_STRICT_MODE=false (warnings only)
# Production:  VALIDATION_STRICT_MODE=true  (fail-fast)
```

---

## 2. Implementation Steps

### Step 1: Install Validator

```bash
# Validator already created at:
validation/content_validator.py
```

### Step 2: Update FAQ Generator

```python
# File: components/faq/generators/faq_generator.py

from validation.content_validator import ContentValidator, ValidationError, ValidationReporter

class FAQComponentGenerator(APIComponentGenerator):
    
    def __init__(self):
        super().__init__("faq")
        # Initialize validator in strict mode for production
        self.validator = ContentValidator(strict_mode=True)
    
    def generate(self, material_name: str, material_data: dict, ...):
        # ... existing 3-step research process ...
        
        # Apply voice enhancement if author provided
        # ... existing voice enhancement code ...
        
        # VALIDATE GENERATED CONTENT
        try:
            faq_items = yaml.safe_load(faq_content)
            
            # Run validation
            report = self.validator.validate_faq(
                faq_items,
                word_count_range=(20, 50),
                max_repetition_threshold=0.60,
                min_variation_score=0.40
            )
            
            # Log results
            logger.info(f"✅ Validation passed (score: {report['quality_score']:.0f}/100)")
            
            if report['warnings']:
                logger.warning(f"⚠️ Quality warnings:")
                for warning in report['warnings']:
                    logger.warning(f"  • {warning}")
            
        except ValidationError as e:
            # Validation failed - return error
            error_msg = f"Content quality validation failed: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return self._create_result("", success=False, error_message=error_msg)
        
        # Only save if validation passes
        try:
            timestamp = datetime.now().isoformat()
            self._write_to_materials(material_name, faq_items, timestamp)
            logger.info(f"✅ FAQ generation complete: {len(faq_items)} questions generated")
        except Exception as e:
            logger.warning(f"Failed to write FAQ to Materials.yaml: {e}")
        
        return self._create_result(faq_content, success=True)
```

### Step 3: Update Caption Generator

```python
# File: components/caption/generators/generator.py

from validation.content_validator import ContentValidator, ValidationError

class CaptionComponentGenerator(APIComponentGenerator):
    
    def __init__(self):
        super().__init__("caption")
        self.validator = ContentValidator(strict_mode=True)
    
    def generate(self, material_name: str, ...):
        # ... existing generation ...
        
        # Validate caption sections
        caption_data = {
            'before': before_caption,
            'after': after_caption
        }
        
        # Basic validation (captions are short, just check word counts)
        for section, text in caption_data.items():
            words = len(text.split())
            if words < 20 or words > 60:
                error_msg = f"{section} caption word count out of range: {words}w"
                logger.error(f"❌ {error_msg}")
                return self._create_result("", success=False, error_message=error_msg)
        
        # ... save to materials ...
```

### Step 4: Update Subtitle Generator

```python
# File: components/subtitle/core/subtitle_generator.py

from validation.content_validator import ContentValidator, ValidationError

class SubtitleGenerator(APIComponentGenerator):
    
    def __init__(self):
        super().__init__("subtitle")
        self.validator = ContentValidator(strict_mode=True)
    
    def generate(self, material_name: str, ...):
        # ... existing generation ...
        
        # Validate subtitle
        try:
            report = self.validator.validate_subtitle(
                subtitle_text,
                word_count_range=(6, 10),
                required_elements=[material_name, 'laser', 'cleaning']
            )
            
            if not report['valid']:
                error_msg = f"Subtitle validation failed: {'; '.join(report['errors'])}"
                logger.error(f"❌ {error_msg}")
                return self._create_result("", success=False, error_message=error_msg)
                
        except ValidationError as e:
            return self._create_result("", success=False, error_message=str(e))
        
        # ... save to materials ...
```

---

## 3. Configuration Management

### Create validation config file:

```yaml
# File: config/validation_config.yaml

faq:
  word_count:
    min: 20
    max: 50
  repetition:
    max_threshold: 0.60  # 60% maximum for any single word
    critical_threshold: 0.80  # 80%+ triggers automatic fail
  variation:
    min_score: 0.40  # 40% minimum unique sentence structures
  quality:
    min_score: 60  # Minimum quality score to pass

caption:
  word_count:
    min: 25
    max: 59
  quality:
    min_score: 70

subtitle:
  word_count:
    min: 6
    max: 10
  required_elements:
    - material_name
    - laser
    - cleaning

general:
  strict_mode: true  # Fail-fast validation
  log_warnings: true
  save_reports: true
  reports_dir: "validation/reports"
```

---

## 4. Serious Work: Auto-Regeneration

### Enhanced validation with automatic retry:

```python
class FAQComponentGenerator(APIComponentGenerator):
    
    MAX_REGENERATION_ATTEMPTS = 3
    
    def generate(self, material_name: str, material_data: dict, ...):
        """Generate FAQ with automatic quality-based regeneration."""
        
        for attempt in range(1, self.MAX_REGENERATION_ATTEMPTS + 1):
            logger.info(f"📝 Generation attempt {attempt}/{self.MAX_REGENERATION_ATTEMPTS}")
            
            # Generate FAQ (3-step process)
            faq_content = self._generate_faq_content(material_name, ...)
            
            # Validate
            try:
                faq_items = yaml.safe_load(faq_content)
                report = self.validator.validate_faq(faq_items, ...)
                
                # Success!
                logger.info(f"✅ Quality score: {report['quality_score']:.0f}/100")
                
                # Save and return
                self._write_to_materials(material_name, faq_items, timestamp)
                return self._create_result(faq_content, success=True)
                
            except ValidationError as e:
                logger.warning(f"⚠️ Attempt {attempt} failed validation: {e}")
                
                if attempt < self.MAX_REGENERATION_ATTEMPTS:
                    logger.info(f"🔄 Regenerating with adjusted parameters...")
                    # Optionally adjust temperature or other params
                else:
                    # Final attempt failed
                    error_msg = f"Failed quality validation after {attempt} attempts"
                    logger.error(f"❌ {error_msg}")
                    return self._create_result("", success=False, error_message=error_msg)
```

---

## 5. Reporting & Analytics

### Save validation reports for analysis:

```python
import json
from pathlib import Path
from datetime import datetime

class FAQComponentGenerator(APIComponentGenerator):
    
    def _save_validation_report(self, material_name: str, report: Dict):
        """Save validation report for analytics."""
        reports_dir = Path("validation/reports/faq")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{material_name}_{timestamp}.json"
        
        report_data = {
            'material': material_name,
            'timestamp': timestamp,
            'validation_report': report
        }
        
        with open(reports_dir / filename, 'w') as f:
            json.dump(report_data, f, indent=2)
```

### Analyze trends:

```bash
# Count failures by material
find validation/reports/faq -name "*.json" | xargs grep '"valid": false' | wc -l

# Average quality scores
python3 -c "
import json
from pathlib import Path

scores = []
for f in Path('validation/reports/faq').glob('*.json'):
    data = json.load(open(f))
    scores.append(data['validation_report']['quality_score'])

print(f'Average quality: {sum(scores)/len(scores):.1f}/100')
print(f'Min: {min(scores):.0f}, Max: {max(scores):.0f}')
"
```

---

## 6. Testing Strategy

```python
# File: tests/test_validation_integration.py

import pytest
from components.faq.generators.faq_generator import FAQComponentGenerator
from validation.content_validator import ValidationError

def test_faq_fails_on_repetition():
    """Test that FAQ with 100% repetition fails validation."""
    
    # Create FAQ with systematic in every answer
    bad_faq = [
        {'question': 'Q1?', 'answer': 'systematic systematic systematic' * 7},
        {'question': 'Q2?', 'answer': 'systematic systematic systematic' * 7},
        {'question': 'Q3?', 'answer': 'systematic systematic systematic' * 7},
    ]
    
    validator = ContentValidator(strict_mode=True)
    
    with pytest.raises(ValidationError):
        validator.validate_faq(bad_faq, word_count_range=(20, 50))

def test_faq_passes_with_variation():
    """Test that diverse FAQ passes validation."""
    
    good_faq = [
        {'question': 'Q1?', 'answer': 'Laser cleaning removes contaminants precisely through thermal ablation processes' + ' word' * 15},
        {'question': 'Q2?', 'answer': 'Advanced optics ensure consistent beam delivery across surface geometries' + ' word' * 15},
        {'question': 'Q3?', 'answer': 'Material-specific parameters optimize cleaning efficiency without damage' + ' word' * 15},
    ]
    
    validator = ContentValidator(strict_mode=True)
    report = validator.validate_faq(good_faq, word_count_range=(20, 50))
    
    assert report['valid']
    assert report['quality_score'] >= 80
```

---

## 7. Rollout Plan

### Phase 1: Development (Week 1)
- ✅ Implement validator in warning mode
- ✅ Collect baseline quality metrics
- ✅ Tune thresholds based on data

### Phase 2: Testing (Week 2)
- ✅ Enable strict mode on test materials
- ✅ Verify auto-regeneration works
- ✅ Measure performance impact

### Phase 3: Production (Week 3)
- ✅ Enable strict mode for all materials
- ✅ Monitor failure rates
- ✅ Adjust thresholds if needed

---

## 8. Success Metrics

| Metric | Target | Current (Granite) |
|--------|--------|-------------------|
| Quality Score | >80/100 | 45/100 ❌ |
| Max Repetition | <60% | 100% ❌ |
| Variation Score | >40% | 14% ❌ |
| Word Count Compliance | 100% | 100% ✅ |

---

## Conclusion

Inline validation with **fail-fast mode** ensures zero defective content reaches production, aligns with project philosophy, and provides actionable quality metrics for continuous improvement.
