# Extensible Frontmatter Architecture Specification

**Version**: 2.0.0  
**Date**: October 30, 2025  
**Status**: DESIGN SPECIFICATION

---

## 🎯 Requirements

### Core Requirements
1. ✅ Support multiple frontmatter content types (Materials, Region, Applications, Thesaurus)
2. ✅ Expand data over time (new materials, properties, categories)
3. ✅ **Author voice as mandatory post-processing** for ALL generated content
4. ✅ Maintain backward compatibility with existing material frontmatter

### New Content Types

#### 1. **Region Frontmatter** (Geographic/Location-based)
- Regional regulations and standards
- Local industry practices
- Geographic-specific applications
- Regional supplier information
- Language/localization variants

#### 2. **Applications Frontmatter** (Use Case-based)
- Specific application scenarios
- Industry-specific workflows
- Process parameters per application
- Success metrics and KPIs
- Case studies and examples

#### 3. **Thesaurus Frontmatter** (Terminology/Knowledge)
- Term definitions and relationships
- Synonyms and related terms
- Technical terminology mappings
- Cross-references
- Multi-language support

---

## 🏗️ Architecture Overview

### Current State (Materials-Only)
```
run.py
  └─> StreamlinedFrontmatterGenerator (hardcoded for materials)
        └─> generates material-laser-cleaning.yaml
```

### Future State (Multi-Type)
```
run.py
  └─> FrontmatterOrchestrator (content-type aware)
        ├─> MaterialFrontmatterGenerator → material-*.yaml
        ├─> RegionFrontmatterGenerator → region-*.yaml
        ├─> ApplicationFrontmatterGenerator → application-*.yaml
        └─> ThesaurusFrontmatterGenerator → thesaurus-*.yaml
        
  ALL generators → AuthorVoiceProcessor (mandatory post-processing)
```

---

## 📁 Proposed Directory Structure

```
components/frontmatter/
├── core/
│   ├── base_generator.py              # Abstract base for all types
│   ├── orchestrator.py                # Multi-type coordinator
│   └── author_voice_processor.py      # Mandatory post-processing
│
├── types/                              # NEW: Type-specific generators
│   ├── __init__.py
│   ├── material/
│   │   ├── __init__.py
│   │   ├── generator.py               # MaterialFrontmatterGenerator
│   │   ├── schema.json                # Material-specific schema
│   │   └── templates/                 # Material templates
│   │
│   ├── region/                         # NEW
│   │   ├── __init__.py
│   │   ├── generator.py               # RegionFrontmatterGenerator
│   │   ├── schema.json
│   │   ├── templates/
│   │   └── data/
│   │       ├── regions.yaml           # Region definitions
│   │       └── regulations.yaml       # Regional regulations
│   │
│   ├── application/                    # NEW
│   │   ├── __init__.py
│   │   ├── generator.py               # ApplicationFrontmatterGenerator
│   │   ├── schema.json
│   │   ├── templates/
│   │   └── data/
│   │       ├── applications.yaml      # Application definitions
│   │       └── workflows.yaml         # Application workflows
│   │
│   └── thesaurus/                      # NEW
│       ├── __init__.py
│       ├── generator.py               # ThesaurusFrontmatterGenerator
│       ├── schema.json
│       ├── templates/
│       └── data/
│           ├── terms.yaml             # Term definitions
│           └── relationships.yaml     # Term relationships
│
├── services/                           # Existing services
│   ├── property_manager.py
│   ├── template_service.py
│   └── pipeline_process_service.py
│
└── validation/
    ├── type_validators/                # NEW: Type-specific validation
    │   ├── material_validator.py
    │   ├── region_validator.py
    │   ├── application_validator.py
    │   └── thesaurus_validator.py
    └── completeness_validator.py

data/
├── Materials.yaml                      # Existing
├── categories/                         # Existing (enhanced)
├── regions/                            # NEW
│   ├── regions.yaml                   # Region definitions
│   ├── regulations.yaml               # Regional regulations
│   └── suppliers.yaml                 # Regional suppliers
├── applications/                       # NEW
│   ├── applications.yaml              # Application definitions
│   ├── workflows.yaml                 # Process workflows
│   └── case_studies.yaml              # Examples
└── thesaurus/                          # NEW
    ├── terms.yaml                     # Term definitions
    ├── synonyms.yaml                  # Synonym mappings
    └── translations.yaml              # Multi-language

frontmatter/
├── materials/                          # Existing (organized)
│   └── aluminum-laser-cleaning.yaml
├── regions/                            # NEW
│   ├── north-america-laser-cleaning.yaml
│   └── europe-laser-cleaning.yaml
├── applications/                       # NEW
│   ├── automotive-coating-removal.yaml
│   └── aerospace-surface-prep.yaml
└── thesaurus/                          # NEW
    └── laser-cleaning-terminology.yaml
```

---

## 🎨 Base Generator Architecture

### Abstract Base Class

```python
# components/frontmatter/core/base_generator.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class FrontmatterGenerationContext:
    """Context for frontmatter generation"""
    content_type: str  # 'material', 'region', 'application', 'thesaurus'
    identifier: str    # e.g., "Aluminum", "North America", "Automotive"
    api_client: Any
    config: Dict[str, Any]
    author: Optional[str] = None
    skip_components: list = None


class BaseFrontmatterGenerator(ABC):
    """
    Abstract base class for all frontmatter generators.
    
    ALL generators must:
    1. Inherit from this base
    2. Implement generate_content()
    3. Support author voice post-processing
    4. Follow schema validation
    """
    
    def __init__(self, api_client=None, config=None, **kwargs):
        self.api_client = api_client
        self.config = config or {}
        self.content_type = self._get_content_type()
        self.author_voice_processor = None  # Injected by orchestrator
    
    @abstractmethod
    def _get_content_type(self) -> str:
        """Return content type identifier"""
        pass
    
    @abstractmethod
    def generate_content(self, context: FrontmatterGenerationContext) -> Dict[str, Any]:
        """
        Generate raw frontmatter content (before author voice processing).
        
        Args:
            context: Generation context with type, identifier, config
            
        Returns:
            Dict with frontmatter structure
        """
        pass
    
    @abstractmethod
    def validate_schema(self, content: Dict[str, Any]) -> bool:
        """Validate content against type-specific schema"""
        pass
    
    @abstractmethod
    def get_output_filename(self, identifier: str) -> str:
        """Generate output filename for this type"""
        pass
    
    def generate(self, identifier: str, **kwargs) -> 'ComponentResult':
        """
        Main generation entry point with mandatory author voice processing.
        
        PIPELINE:
        1. Generate raw content
        2. Validate schema
        3. Apply author voice (MANDATORY)
        4. Final validation
        5. Format as YAML
        """
        # Create context
        context = FrontmatterGenerationContext(
            content_type=self.content_type,
            identifier=identifier,
            api_client=self.api_client,
            config=self.config,
            **kwargs
        )
        
        # 1. Generate raw content
        raw_content = self.generate_content(context)
        
        # 2. Schema validation
        if not self.validate_schema(raw_content):
            return ComponentResult(
                component_type=self.content_type,
                content="",
                success=False,
                error_message=f"Schema validation failed for {self.content_type}"
            )
        
        # 3. MANDATORY: Apply author voice processing
        if self.author_voice_processor:
            processed_content = self.author_voice_processor.process(
                content=raw_content,
                content_type=self.content_type,
                identifier=identifier
            )
        else:
            # FAIL-FAST: Author voice processor MUST be configured
            raise ConfigurationError(
                "Author voice processor not configured - this is mandatory for all frontmatter generation"
            )
        
        # 4. Convert to YAML
        yaml_content = yaml.dump(
            processed_content,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False
        )
        
        return ComponentResult(
            component_type=self.content_type,
            content=yaml_content,
            success=True
        )
```

---

## 🎭 Mandatory Author Voice Integration

### Author Voice Processor

```python
# components/frontmatter/core/author_voice_processor.py

class AuthorVoiceProcessor:
    """
    Mandatory post-processor for ALL frontmatter content.
    
    Applies author voice patterns to:
    - Descriptions
    - Captions
    - Technical explanations
    - Any human-readable text
    
    REQUIREMENTS:
    - MUST be applied to all generated content
    - MUST preserve technical accuracy
    - MUST maintain schema compliance
    - MUST support all content types
    """
    
    def __init__(self, voice_engine=None):
        if voice_engine is None:
            from voice.engine import get_voice_engine
            self.voice_engine = get_voice_engine()
        else:
            self.voice_engine = voice_engine
    
    def process(
        self,
        content: Dict[str, Any],
        content_type: str,
        identifier: str,
        author: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Apply author voice to all text fields in content.
        
        Args:
            content: Raw frontmatter content
            content_type: Type of content (material, region, etc.)
            identifier: Content identifier
            author: Optional author override
            
        Returns:
            Content with author voice applied
        """
        # Select author based on content type and identifier
        if not author:
            author = self._select_author(content_type, identifier)
        
        # Apply voice to all text fields
        processed = self._apply_voice_recursive(
            content=content,
            author=author,
            content_type=content_type
        )
        
        # Add metadata
        processed['_voice_metadata'] = {
            'author': author,
            'processed_date': datetime.now().isoformat(),
            'content_type': content_type
        }
        
        return processed
    
    def _select_author(self, content_type: str, identifier: str) -> str:
        """
        Select appropriate author based on content and context.
        
        Rules:
        - Materials: Rotate through technical authors
        - Regions: Use local/regional author when possible
        - Applications: Use industry-specific author
        - Thesaurus: Use authoritative/academic author
        """
        # Author selection logic
        return self.voice_engine.select_author(content_type, identifier)
    
    def _apply_voice_recursive(
        self,
        content: Any,
        author: str,
        content_type: str
    ) -> Any:
        """
        Recursively apply author voice to all text fields.
        
        Preserves:
        - Numerical values
        - Units
        - Enums/constants
        - Technical identifiers
        
        Transforms:
        - Descriptions
        - Explanations
        - Captions
        - Notes
        """
        if isinstance(content, dict):
            result = {}
            for key, value in content.items():
                # Apply voice to text fields
                if key in ['description', 'micro', 'explanation', 'notes', 'summary']:
                    if isinstance(value, str):
                        result[key] = self.voice_engine.transform_text(
                            text=value,
                            author=author,
                            context=content_type
                        )
                    else:
                        result[key] = value
                else:
                    # Recurse for nested structures
                    result[key] = self._apply_voice_recursive(value, author, content_type)
            return result
        
        elif isinstance(content, list):
            return [self._apply_voice_recursive(item, author, content_type) for item in content]
        
        else:
            return content
```

---

## 📦 Content Type Implementations

### 1. Material Frontmatter (Existing - Refactored)

```python
# components/frontmatter/types/material/generator.py

class MaterialFrontmatterGenerator(BaseFrontmatterGenerator):
    """Material-specific frontmatter generator (existing functionality)"""
    
    def _get_content_type(self) -> str:
        return "material"
    
    def generate_content(self, context: FrontmatterGenerationContext) -> Dict:
        # Existing StreamlinedFrontmatterGenerator logic here
        # Extract from _generate_from_yaml method
        return material_content
    
    def get_output_filename(self, identifier: str) -> str:
        safe_name = identifier.lower().replace(' ', '-')
        return f"{safe_name}-laser-cleaning.yaml"
```

### 2. Region Frontmatter (NEW)

```python
# components/frontmatter/types/region/generator.py

class RegionFrontmatterGenerator(BaseFrontmatterGenerator):
    """Region-specific frontmatter generator"""
    
    def _get_content_type(self) -> str:
        return "region"
    
    def generate_content(self, context: FrontmatterGenerationContext) -> Dict:
        """
        Generate region frontmatter content.
        
        Structure:
        - region_name
        - geographic_coverage
        - regulatory_standards (region-specific)
        - industry_practices
        - supplier_information
        - language_variants
        - market_characteristics
        """
        region_data = self._load_region_data(context.identifier)
        
        content = {
            'region_name': context.identifier,
            'geographic_coverage': region_data['coverage'],
            'regulatory_standards': self._get_regional_regulations(context.identifier),
            'industry_practices': self._get_industry_practices(context.identifier),
            'supplier_directory': self._get_suppliers(context.identifier),
            'language_variants': region_data.get('languages', []),
            'market_size': region_data.get('market_data', {}),
            'applications': self._get_regional_applications(context.identifier)
        }
        
        return content
    
    def get_output_filename(self, identifier: str) -> str:
        safe_name = identifier.lower().replace(' ', '-')
        return f"{safe_name}-laser-cleaning-region.yaml"
```

### 3. Application Frontmatter (NEW)

```python
# components/frontmatter/types/application/generator.py

class ApplicationFrontmatterGenerator(BaseFrontmatterGenerator):
    """Application-specific frontmatter generator"""
    
    def _get_content_type(self) -> str:
        return "application"
    
    def generate_content(self, context: FrontmatterGenerationContext) -> Dict:
        """
        Generate application frontmatter content.
        
        Structure:
        - application_name
        - industry_sector
        - process_parameters
        - material_compatibility
        - success_metrics
        - workflow_steps
        - case_studies
        """
        app_data = self._load_application_data(context.identifier)
        
        content = {
            'application_name': context.identifier,
            'industry': app_data['industry'],
            'process_parameters': self._get_optimal_parameters(context.identifier),
            'compatible_materials': self._get_compatible_materials(context.identifier),
            'success_metrics': app_data['kpis'],
            'workflow': self._generate_workflow(context.identifier),
            'case_studies': self._get_case_studies(context.identifier),
            'challenges': app_data.get('common_challenges', []),
            'best_practices': self._generate_best_practices(context.identifier)
        }
        
        return content
    
    def get_output_filename(self, identifier: str) -> str:
        safe_name = identifier.lower().replace(' ', '-')
        return f"{safe_name}-laser-cleaning-application.yaml"
```

### 4. Thesaurus Frontmatter (NEW)

```python
# components/frontmatter/types/thesaurus/generator.py

class ThesaurusFrontmatterGenerator(BaseFrontmatterGenerator):
    """Thesaurus/terminology frontmatter generator"""
    
    def _get_content_type(self) -> str:
        return "thesaurus"
    
    def generate_content(self, context: FrontmatterGenerationContext) -> Dict:
        """
        Generate thesaurus frontmatter content.
        
        Structure:
        - term
        - definition
        - synonyms
        - related_terms
        - category
        - usage_examples
        - translations
        - references
        """
        term_data = self._load_term_data(context.identifier)
        
        content = {
            'term': context.identifier,
            'definition': self._generate_definition(context.identifier),
            'synonyms': term_data.get('synonyms', []),
            'related_terms': self._get_related_terms(context.identifier),
            'category': term_data['category'],
            'usage_context': self._generate_usage_examples(context.identifier),
            'translations': self._get_translations(context.identifier),
            'technical_notes': term_data.get('notes', ''),
            'references': self._get_references(context.identifier)
        }
        
        return content
    
    def get_output_filename(self, identifier: str) -> str:
        safe_name = identifier.lower().replace(' ', '-')
        return f"{safe_name}-terminology.yaml"
```

---

## 🎯 Orchestrator Implementation

```python
# components/frontmatter/core/orchestrator.py

class FrontmatterOrchestrator:
    """
    Central coordinator for multi-type frontmatter generation.
    
    Responsibilities:
    - Route requests to appropriate generator
    - Inject author voice processor (mandatory)
    - Manage generator lifecycle
    - Handle cross-type dependencies
    """
    
    def __init__(self, api_client=None, config=None):
        self.api_client = api_client
        self.config = config or {}
        
        # Initialize author voice processor (MANDATORY)
        self.author_voice_processor = AuthorVoiceProcessor()
        
        # Initialize generators
        self.generators = {
            'material': MaterialFrontmatterGenerator(api_client, config),
            'region': RegionFrontmatterGenerator(api_client, config),
            'application': ApplicationFrontmatterGenerator(api_client, config),
            'thesaurus': ThesaurusFrontmatterGenerator(api_client, config)
        }
        
        # Inject author voice processor into all generators
        for generator in self.generators.values():
            generator.author_voice_processor = self.author_voice_processor
    
    def generate(
        self,
        content_type: str,
        identifier: str,
        **kwargs
    ) -> 'ComponentResult':
        """
        Generate frontmatter for any content type.
        
        Args:
            content_type: Type of content ('material', 'region', 'application', 'thesaurus')
            identifier: Content identifier
            **kwargs: Additional generation parameters
            
        Returns:
            ComponentResult with generated content
        """
        if content_type not in self.generators:
            raise ValueError(f"Unknown content type: {content_type}")
        
        generator = self.generators[content_type]
        return generator.generate(identifier, **kwargs)
    
    def generate_batch(
        self,
        requests: List[Tuple[str, str]]
    ) -> Dict[str, 'ComponentResult']:
        """
        Generate multiple frontmatter files in batch.
        
        Args:
            requests: List of (content_type, identifier) tuples
            
        Returns:
            Dict mapping identifiers to results
        """
        results = {}
        for content_type, identifier in requests:
            result = self.generate(content_type, identifier)
            results[f"{content_type}:{identifier}"] = result
        return results
```

---

## 🔄 Data Expansion Strategy

### Adding New Materials
```yaml
# data/Materials.yaml
materials:
  NewMaterial:  # Just add new entry
    category: metal
    properties:
      density:
        value: 8.9
        unit: g/cm³
        confidence: 95
```

### Adding New Properties
```yaml
# data/property_definitions.yaml (auto-classification)
properties:
  newProperty:
    type: quantitative
    category: thermal
    unit_required: true
    range_required: true
    typical_units: ['unit']
```

### Adding New Categories
```yaml
# data/categories/material_types.yaml
categories:
  new_category:
    name: New Category Name
    description: Description
    subcategories: {}
    common_applications: []
```

### Adding New Regions
```yaml
# data/regions/regions.yaml (NEW)
regions:
  Asia-Pacific:
    countries: [China, Japan, Korea, ...]
    regulations: [...]
    market_size: {...}
```

### Adding New Applications
```yaml
# data/applications/applications.yaml (NEW)
applications:
  AutomotiveCoatingRemoval:
    industry: Automotive
    parameters: {...}
    materials: [...]
```

---

## 🚀 Migration Path

### Phase 1: Refactor Existing (Week 1)
1. Extract MaterialFrontmatterGenerator from StreamlinedFrontmatterGenerator
2. Create BaseFrontmatterGenerator abstract class
3. Implement AuthorVoiceProcessor integration
4. Update run.py to use orchestrator

### Phase 2: Add Region Support (Week 2)
1. Create data/regions/ structure
2. Implement RegionFrontmatterGenerator
3. Add region-specific schemas
4. Test with 3-5 regions

### Phase 3: Add Application Support (Week 3)
1. Create data/applications/ structure
2. Implement ApplicationFrontmatterGenerator
3. Add application workflows
4. Test with 5-10 applications

### Phase 4: Add Thesaurus Support (Week 4)
1. Create data/thesaurus/ structure
2. Implement ThesaurusFrontmatterGenerator
3. Add term relationships
4. Test with 20-30 terms

---

## ✅ Success Criteria

- [ ] All frontmatter types support author voice (MANDATORY)
- [ ] New materials can be added by editing Materials.yaml only
- [ ] New properties auto-classified via property_definitions.yaml
- [ ] Each content type has independent schema validation
- [ ] Backward compatibility with existing material frontmatter
- [ ] Performance: <5s per frontmatter file
- [ ] All content types follow same pipeline (generate → voice → validate)

---

**Next Steps**: Implement Phase 1 refactoring
