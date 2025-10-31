# Universal Content Pipeline Architecture

**Purpose**: Extensible framework for researching and generating frontmatter for ANY content type  
**Date**: October 29, 2025  
**Status**: Architectural Proposal

---

## 🎯 Vision

Transform the current **material-specific pipeline** into a **universal content generation system** that can research and produce frontmatter for:

- Materials (current)
- Products
- Services
- Technologies
- Processes
- Equipment
- Applications
- Case Studies
- Industry Standards
- Techniques
- *Any future content type*

---

## 📊 Current State (Material-Specific)

### Existing Pipeline
```
Material Name → Research → Materials.yaml → Components → Frontmatter
                    ↓
            - Properties
            - Settings
            - Applications
            - Standards
```

### Limitations
- ❌ **Hardcoded** for materials only
- ❌ **Tight coupling** between research and material properties
- ❌ **No abstraction** for different content types
- ❌ **Duplicated logic** if adding new content types

---

## 🏗️ Proposed Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                  (Frontmatter Assembly)                      │
├─────────────────────────────────────────────────────────────┤
│     Material      Product      Service     Technology        │
│   Frontmatter   Frontmatter  Frontmatter   Frontmatter       │
│   Orchestrator  Orchestrator Orchestrator  Orchestrator      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   GENERATION LAYER                           │
│              (Content Component Generators)                  │
├─────────────────────────────────────────────────────────────┤
│  Text   FAQ   Caption  Subtitle  Metadata  Properties  ...  │
│  (Universal - work with any content type via ContentSchema)  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH LAYER                            │
│           (AI-Powered Content Discovery)                     │
├─────────────────────────────────────────────────────────────┤
│ PropertyResearcher  ApplicationResearcher  StandardsResearcher│
│ SpecificationResearcher  RelationshipResearcher  ...        │
│          (Schema-driven - discover any field type)           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│              (Universal Content Storage)                     │
├─────────────────────────────────────────────────────────────┤
│  content/                                                    │
│    ├── materials.yaml      (Material content)                │
│    ├── products.yaml       (Product content)                 │
│    ├── services.yaml       (Service content)                 │
│    ├── technologies.yaml   (Technology content)              │
│    └── [content_type].yaml (Extensible)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Core Abstractions

### 1. ContentSchema (Base Class)

**Purpose**: Define the structure and research requirements for any content type

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

@dataclass
class ContentSchema(ABC):
    """
    Abstract base class defining content structure and research requirements.
    
    Every content type (Material, Product, Service, etc.) extends this.
    """
    
    # Identity
    content_type: str           # "material", "product", "service", etc.
    name: str                   # Content item name
    category: Optional[str]     # Primary category
    subcategory: Optional[str]  # Subcategory
    
    # Core metadata
    title: str
    subtitle: Optional[str]
    description: str
    
    # Author/attribution
    author: Dict[str, Any]
    
    # Extensible fields
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Schema definition
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Return list of required field names"""
        pass
    
    @abstractmethod
    def get_researchable_fields(self) -> Dict[str, 'FieldResearchSpec']:
        """Return fields that can be AI-researched with specs"""
        pass
    
    @abstractmethod
    def get_component_requirements(self) -> List[str]:
        """Return required component types (faq, caption, etc.)"""
        pass
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate content completeness"""
        pass


@dataclass
class FieldResearchSpec:
    """Specification for researching a single field"""
    field_name: str
    field_type: str           # "property", "specification", "relationship", etc.
    data_type: str            # "string", "number", "list", "dict"
    research_method: str      # "web_search", "database_lookup", "calculation"
    prompt_template: str      # AI prompt template
    validation_rules: Dict    # Validation requirements
    priority: int             # Research priority (1=critical, 3=optional)
```

### 2. ContentType Implementations

**MaterialContent** (extends ContentSchema):
```python
@dataclass
class MaterialContent(ContentSchema):
    """Material-specific content schema"""
    
    # Material-specific fields
    materialProperties: Dict[str, Dict]
    machineSettings: Dict[str, Dict]
    applications: List[str]
    regulatoryStandards: List[Dict]
    environmentalImpact: List[str]
    outcomeMetrics: List[str]
    materialCharacteristics: List[str]
    
    def get_required_fields(self) -> List[str]:
        return [
            'name', 'category', 'materialProperties', 
            'machineSettings', 'applications'
        ]
    
    def get_researchable_fields(self) -> Dict[str, FieldResearchSpec]:
        return {
            'materialProperties': FieldResearchSpec(
                field_name='materialProperties',
                field_type='property',
                data_type='dict',
                research_method='web_search',
                prompt_template='research_material_properties.txt',
                validation_rules={'min_properties': 3},
                priority=1
            ),
            'applications': FieldResearchSpec(
                field_name='applications',
                field_type='relationship',
                data_type='list',
                research_method='web_search',
                prompt_template='research_material_applications.txt',
                validation_rules={'min_items': 3},
                priority=2
            ),
            # ... more fields
        }
    
    def get_component_requirements(self) -> List[str]:
        return ['text', 'faq', 'caption', 'subtitle']
```

**ProductContent** (extends ContentSchema):
```python
@dataclass
class ProductContent(ContentSchema):
    """Product-specific content schema"""
    
    # Product-specific fields
    manufacturer: str
    model: str
    specifications: Dict[str, Any]
    features: List[str]
    pricing: Dict[str, float]
    availability: Dict[str, Any]
    compatibility: List[str]
    
    def get_required_fields(self) -> List[str]:
        return ['name', 'manufacturer', 'model', 'specifications']
    
    def get_researchable_fields(self) -> Dict[str, FieldResearchSpec]:
        return {
            'specifications': FieldResearchSpec(
                field_name='specifications',
                field_type='specification',
                data_type='dict',
                research_method='web_search',
                prompt_template='research_product_specifications.txt',
                validation_rules={'min_specs': 5},
                priority=1
            ),
            'features': FieldResearchSpec(
                field_name='features',
                field_type='attribute',
                data_type='list',
                research_method='web_search',
                prompt_template='research_product_features.txt',
                validation_rules={'min_items': 5},
                priority=2
            ),
        }
```

---

## 🔬 Research Layer Architecture

### Universal Researcher Pattern

```python
from abc import ABC, abstractmethod
from typing import Any, Optional

class ContentResearcher(ABC):
    """
    Base class for all content researchers.
    
    Researchers are field-type specialists that know how to discover data.
    """
    
    def __init__(self, api_client: Any):
        self.api_client = api_client
    
    @abstractmethod
    def research(
        self, 
        content_name: str,
        field_spec: FieldResearchSpec,
        context: Optional[Dict] = None
    ) -> ResearchResult:
        """Research a specific field for content item"""
        pass
    
    @abstractmethod
    def validate_result(self, result: Any, field_spec: FieldResearchSpec) -> bool:
        """Validate research result meets requirements"""
        pass


class PropertyResearcher(ContentResearcher):
    """Researches property fields (numerical/technical)"""
    
    def research(self, content_name: str, field_spec: FieldResearchSpec, 
                 context: Optional[Dict] = None) -> ResearchResult:
        # Build prompt from template
        prompt = self._build_prompt(content_name, field_spec, context)
        
        # Call AI
        response = self.api_client.generate(prompt)
        
        # Parse and validate
        parsed_data = self._parse_response(response, field_spec.data_type)
        valid = self.validate_result(parsed_data, field_spec)
        
        return ResearchResult(
            field_name=field_spec.field_name,
            data=parsed_data,
            success=valid,
            confidence=self._calculate_confidence(parsed_data),
            source='ai_research'
        )


class ApplicationResearcher(ContentResearcher):
    """Researches application/use-case fields"""
    # Similar structure, different research logic


class SpecificationResearcher(ContentResearcher):
    """Researches technical specification fields"""
    # Similar structure, different research logic
```

### Researcher Factory

```python
class ResearcherFactory:
    """Creates appropriate researcher for field type"""
    
    _researchers = {
        'property': PropertyResearcher,
        'specification': SpecificationResearcher,
        'application': ApplicationResearcher,
        'relationship': RelationshipResearcher,
        'standard': StandardsResearcher,
        'attribute': AttributeResearcher,
    }
    
    @classmethod
    def create_researcher(
        cls, 
        field_type: str, 
        api_client: Any
    ) -> ContentResearcher:
        """Create researcher for specific field type"""
        researcher_class = cls._researchers.get(field_type)
        
        if not researcher_class:
            raise ValueError(f"No researcher for field type: {field_type}")
        
        return researcher_class(api_client)
    
    @classmethod
    def register_researcher(cls, field_type: str, researcher_class: type):
        """Register new researcher type (extensibility)"""
        cls._researchers[field_type] = researcher_class
```

---

## 🎨 Generation Layer Architecture

### Universal Component Generators

Component generators become **content-type agnostic** through ContentSchema:

```python
class UniversalTextGenerator:
    """
    Generates text components for ANY content type.
    
    Uses ContentSchema to understand what to generate.
    """
    
    def generate(
        self, 
        content_schema: ContentSchema,
        component_type: str = 'description'
    ) -> ComponentResult:
        # Extract relevant data from schema
        context = self._build_context(content_schema)
        
        # Load appropriate prompt template
        prompt_template = self._load_template(
            content_schema.content_type,
            component_type
        )
        
        # Generate content
        result = self.api_client.generate(
            prompt_template.format(**context)
        )
        
        return ComponentResult(
            content=result,
            success=True,
            component_type=component_type
        )
    
    def _build_context(self, schema: ContentSchema) -> Dict:
        """Extract generation context from schema"""
        return {
            'name': schema.name,
            'category': schema.category,
            'description': schema.description,
            'custom_fields': schema.custom_fields,
            # Add any schema-specific fields
        }
```

---

## 🔄 End-to-End Pipeline

### ContentPipeline (Universal Orchestrator)

```python
class ContentPipeline:
    """
    Universal pipeline for content research → generation → export.
    
    Works with ANY ContentSchema implementation.
    """
    
    def __init__(self, api_client: Any):
        self.api_client = api_client
        self.researcher_factory = ResearcherFactory()
    
    def process(
        self, 
        content_name: str,
        content_schema_class: type,  # MaterialContent, ProductContent, etc.
        existing_data: Optional[Dict] = None
    ) -> ContentResult:
        """
        Complete pipeline from name to frontmatter.
        
        Steps:
        1. Initialize content schema
        2. Research missing fields
        3. Generate components
        4. Assemble frontmatter
        5. Export to YAML
        """
        
        # 1. Initialize schema
        print(f"🚀 Processing {content_name} ({content_schema_class.__name__})")
        
        if existing_data:
            content = content_schema_class(**existing_data)
        else:
            content = content_schema_class(
                content_type=content_schema_class.__name__.replace('Content', '').lower(),
                name=content_name,
                title=f"{content_name}",
                description="",
                author=self._get_default_author()
            )
        
        # 2. Research missing fields
        print("🔬 Researching missing data...")
        research_results = self._research_missing_fields(content)
        
        # 3. Update content with research
        content = self._apply_research(content, research_results)
        
        # 4. Generate components
        print("🎨 Generating components...")
        components = self._generate_components(content)
        
        # 5. Assemble frontmatter
        print("📦 Assembling frontmatter...")
        frontmatter = self._assemble_frontmatter(content, components)
        
        # 6. Export
        print("💾 Exporting...")
        export_path = self._export(content_name, content.content_type, frontmatter)
        
        return ContentResult(
            content_name=content_name,
            content_type=content.content_type,
            frontmatter=frontmatter,
            export_path=export_path,
            success=True
        )
    
    def _research_missing_fields(
        self, 
        content: ContentSchema
    ) -> Dict[str, ResearchResult]:
        """Research all missing researchable fields"""
        results = {}
        
        researchable_fields = content.get_researchable_fields()
        
        for field_name, field_spec in researchable_fields.items():
            # Check if field needs research
            if self._field_needs_research(content, field_name):
                print(f"  🔍 Researching {field_name}...")
                
                # Create appropriate researcher
                researcher = self.researcher_factory.create_researcher(
                    field_spec.field_type,
                    self.api_client
                )
                
                # Research the field
                result = researcher.research(
                    content.name,
                    field_spec,
                    context={'category': content.category}
                )
                
                results[field_name] = result
        
        return results
    
    def _generate_components(
        self, 
        content: ContentSchema
    ) -> Dict[str, ComponentResult]:
        """Generate all required components"""
        components = {}
        
        required_components = content.get_component_requirements()
        
        for component_type in required_components:
            generator = self._get_component_generator(component_type)
            result = generator.generate(content, component_type)
            components[component_type] = result
        
        return components
```

---

## 📁 File Structure

```
z-beam-generator/
├── content/                        # Universal content storage
│   ├── schemas/                    # ContentSchema definitions
│   │   ├── __init__.py
│   │   ├── base.py                 # ContentSchema base class
│   │   ├── material.py             # MaterialContent
│   │   ├── product.py              # ProductContent
│   │   ├── service.py              # ServiceContent
│   │   └── technology.py           # TechnologyContent
│   │
│   ├── data/                       # Content YAML files
│   │   ├── materials.yaml
│   │   ├── products.yaml
│   │   ├── services.yaml
│   │   └── technologies.yaml
│   │
│   └── frontmatter/                # Generated frontmatter
│       ├── materials/
│       ├── products/
│       ├── services/
│       └── technologies/
│
├── research/                       # Research layer
│   ├── __init__.py
│   ├── base.py                     # ContentResearcher base
│   ├── factory.py                  # ResearcherFactory
│   ├── property_researcher.py
│   ├── application_researcher.py
│   ├── specification_researcher.py
│   └── standards_researcher.py
│
├── components/                     # Generation layer
│   ├── universal/                  # Universal generators
│   │   ├── text_generator.py      # Works with any ContentSchema
│   │   ├── faq_generator.py
│   │   ├── caption_generator.py
│   │   └── subtitle_generator.py
│   │
│   └── specialized/                # Content-type specific (if needed)
│       ├── material/
│       └── product/
│
├── pipeline/                       # Orchestration layer
│   ├── __init__.py
│   ├── content_pipeline.py         # Universal pipeline
│   ├── material_pipeline.py        # Material-specific (convenience)
│   └── product_pipeline.py         # Product-specific (convenience)
│
└── cli/                            # Command-line interface
    └── generate_content.py         # Universal CLI
```

---

## 🎯 Usage Examples

### Example 1: Generate Material (Current Use Case)

```python
from shared.pipeline.content_pipeline import ContentPipeline
from content.schemas.material import MaterialContent
from api.client_factory import create_api_client

# Initialize pipeline
client = create_api_client('grok')
pipeline = ContentPipeline(client)

# Process new material
result = pipeline.process(
    content_name="Titanium Alloy Ti-6Al-4V",
    content_schema_class=MaterialContent
)

print(f"✅ Generated frontmatter: {result.export_path}")
```

### Example 2: Generate Product

```python
from content.schemas.product import ProductContent

# Process new product
result = pipeline.process(
    content_name="Trumpf TruLaser 3030",
    content_schema_class=ProductContent
)
```

### Example 3: Generate with Existing Data

```python
# Process material with partial data
existing_data = {
    'name': 'Steel',
    'category': 'metal',
    'subcategory': 'ferrous',
    'materialProperties': {...},  # Partial data
    # Missing: applications, standards, etc.
}

result = pipeline.process(
    content_name="Steel",
    content_schema_class=MaterialContent,
    existing_data=existing_data
)
# Pipeline will research and fill missing fields
```

### Example 4: CLI Usage

```bash
# Generate material
python3 cli/generate_content.py --type material --name "Carbon Fiber"

# Generate product
python3 cli/generate_content.py --type product --name "Coherent Monaco Laser"

# Generate service
python3 cli/generate_content.py --type service --name "Laser Cleaning Service"

# Batch generate
python3 cli/generate_content.py --type material --batch materials_list.txt
```

---

## 🚀 Migration Strategy

### Phase 1: Foundation (Week 1)
1. Create `shared/schemas/base.py` with ContentSchema
2. Refactor MaterialContent to extend ContentSchema
3. Create ResearcherFactory and base ContentResearcher
4. Update existing researchers to use new pattern

### Phase 2: Universal Pipeline (Week 2)
1. Create ContentPipeline
2. Migrate material pipeline to use ContentPipeline
3. Test with existing 132 materials
4. Validate backward compatibility

### Phase 3: New Content Types (Week 3)
1. Implement ProductContent schema
2. Implement product-specific researchers
3. Test product pipeline end-to-end
4. Document extension process

### Phase 4: Component Generalization (Week 4)
1. Refactor component generators to be content-agnostic
2. Create universal prompt templates
3. Test components across content types
4. Performance optimization

---

## ✅ Benefits

### For Developers
- ✅ **DRY Principle**: Write research logic once, use everywhere
- ✅ **Type Safety**: Strong typing through ContentSchema
- ✅ **Testability**: Each layer independently testable
- ✅ **Extensibility**: Add new content types without modifying core

### For Users
- ✅ **Consistency**: Same quality across all content types
- ✅ **Speed**: Parallel research and generation
- ✅ **Flexibility**: Support any content domain
- ✅ **Reliability**: Fail-fast validation at every step

### For Business
- ✅ **Scalability**: Generate thousands of content items
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Reusability**: Leverage existing infrastructure
- ✅ **Future-Proof**: Easy to add new domains

---

## 🎓 Key Principles

1. **Schema-Driven**: ContentSchema defines structure and behavior
2. **Factory Pattern**: Create researchers dynamically based on field type
3. **Strategy Pattern**: Different research strategies for different field types
4. **Composition**: Assemble complex content from simple components
5. **Fail-Fast**: Validate at every step, never produce incomplete content
6. **Zero Coupling**: Components don't know about specific content types

---

## 🔮 Future Extensions

### Additional Content Types
- **Equipment**: Laser systems, cleaning machines, robotics
- **Techniques**: Laser cleaning methods, surface preparation
- **Applications**: Industry-specific use cases
- **Case Studies**: Customer success stories
- **Standards**: Regulatory and industry standards
- **Training**: Educational content and courses

### Advanced Features
- **Relationship Mapping**: Link related content automatically
- **Version Control**: Track content evolution over time
- **Multi-Language**: Generate content in multiple languages
- **Batch Operations**: Process hundreds of items in parallel
- **Quality Scoring**: AI-driven content quality assessment
- **A/B Testing**: Generate multiple variations for testing

---

## 📊 Success Metrics

- ✅ **100% backward compatibility** with existing material pipeline
- ✅ **3+ new content types** implemented in first month
- ✅ **<2 hours** to add new content type (including tests)
- ✅ **90%+ code reuse** across content types
- ✅ **<10 seconds** to generate complete frontmatter for any content
- ✅ **Zero regression** in existing material generation

---

**Status**: Ready for implementation  
**Next Step**: Create `shared/schemas/base.py` with ContentSchema base class
