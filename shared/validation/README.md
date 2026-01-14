# Validation Module

Consolidated validation system organized by concern.

## Structure

```
shared/validation/
├── core/
│   ├── base_validator.py       # Base validation class
│   └── schema_validator.py     # JSON schema validation
├── content/
│   ├── content_validator.py    # Content quality checks
│   ├── quality_validator.py    # Quality scoring
│   ├── prompt_validator.py     # Prompt validation
│   └── prompt_coherence_validator.py
├── domain/
│   ├── research_validator.py   # Research validation
│   ├── contamination_validator.py
│   └── micro_integration_validator.py
├── helpers/
│   ├── property_validators.py  # Property validation helpers
│   └── relationship_validators.py
├── frontmatter_validator.py    # Frontmatter validation
├── layer_validator.py          # Layer validation
├── score_validator.py          # Score validation
├── validator.py                # Main validator entry
└── errors.py                   # Validation errors
```

## Consolidation (Jan 13, 2026)

Organized 25 validators into logical groups:
- **Core**: Base classes and schema validation
- **Content**: Content quality, prompts, coherence
- **Domain**: Domain-specific validation (research, contamination)
- **Helpers**: Reusable validation utilities
- **Root**: Cross-cutting validators (frontmatter, layers, scores)

## Usage

```python
# Import from organized structure
from shared.validation.content import ContentValidator, QualityValidator
from shared.validation.domain import ResearchValidator
from shared.validation.core import SchemaValidator
```

## Related

- Core validation: `shared/validation/core/`
- Domain validation: `domains/*/validator.py`
- Service validation: `shared/services/validation/`
