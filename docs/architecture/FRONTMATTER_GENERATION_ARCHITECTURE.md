# Frontmatter Generation Architecture

**Date**: November 27, 2025  
**Status**: ✅ ACTIVE ARCHITECTURE  
**Purpose**: Document the unified frontmatter generation system for all domains

> **📋 Related**: See [MINIMAL_DOMAIN_ARCHITECTURE_PROPOSAL.md](./MINIMAL_DOMAIN_ARCHITECTURE_PROPOSAL.md) for proposed improvements to reduce code duplication from 853 → 150 lines while keeping prompts as the primary user interface.

---

## 🎯 Executive Summary

The Z-Beam Generator uses a **domain-agnostic frontmatter generation architecture** where:

1. **All domains export similar frontmatter structures** (author, content, metadata, properties)
2. **All domains share mandatory post-processing** (AI detection, author voice enhancement)
3. **Each domain has unique content requirements** requiring domain-specific prompts
4. **Shared infrastructure handles common concerns** (validation, voice, export)
5. **Domain-specific generators customize content strategy** (prompts, properties, structure)

---

## 📐 Architectural Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  FRONTMATTER OUTPUT (All Domains)                               │
│  - author: {name, country, bio}                                 │
│  - content: {caption, description, faq}                         │
│  - metadata: {title, slug, datePublished}                       │
│  - properties: {domain-specific fields}                         │
└─────────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│  MANDATORY POST-PROCESSING (Shared Infrastructure)              │
│  1. AI Detection (shared/voice/ai_detection.py)                 │
│  2. Author Voice Enhancement (shared/voice/post_processor.py)   │
│  3. Schema Validation (shared/validation/)                      │
│  4. Quality Scanning (shared/voice/quality_scanner.py)          │
└─────────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│  CONTENT GENERATION (Domain-Specific)                           │
│  - Domain-specific prompts (domains/[name]/prompts/*.txt)       │
│  - Domain-specific properties (materialProperties, etc.)        │
│  - Domain-specific validation (completeness, ranges)            │
│  - Component generation (caption, description, FAQ)             │
└─────────────────────────────────────────────────────────────────┘
                              ↑
┌─────────────────────────────────────────────────────────────────┐
│  BASE GENERATOR (export/core/base_generator.py)                 │
│  - BaseFrontmatterGenerator: Abstract base class                │
│  - Standard generation pipeline                                 │
│  - Enforces mandatory post-processing                           │
│  - Schema validation                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏛️ Base Generator Architecture

### **BaseFrontmatterGenerator** (`export/core/base_generator.py`)

**Purpose**: Abstract base class enforcing consistent generation workflow across ALL domains.

#### **Standard Pipeline**

Every domain generator follows this pipeline:

```python
def generate(self, identifier: str, **kwargs) -> ComponentResult:
    """
    Standard generation pipeline (enforced for all domains).
    
    1. Validate identifier exists
    2. Load domain data
    3. Build frontmatter structure
    4. Apply author voice (MANDATORY)
    5. Validate schema
    6. Export to file
    """
    # Step 1: Validate
    self._validate_identifier(identifier)
    
    # Step 2: Load data
    data = self._load_domain_data(identifier)
    
    # Step 3: Build frontmatter
    frontmatter = self._build_frontmatter_data(data)
    
    # Step 4: Apply author voice (MANDATORY)
    frontmatter = self._enhance_author_voice(frontmatter)
    
    # Step 5: Validate schema
    self._validate_schema(frontmatter)
    
    # Step 6: Export
    self._export_to_file(frontmatter, identifier)
    
    return ComponentResult(...)
```

#### **Abstract Methods** (Must be implemented by each domain)

```python
@abstractmethod
def _load_type_data(self):
    """Load domain-specific data structures (YAML files, configs)"""
    pass

@abstractmethod
def _validate_identifier(self, identifier: str) -> bool:
    """Validate that identifier exists in domain data"""
    pass

@abstractmethod
def _build_frontmatter_data(self, data: Dict) -> Dict:
    """Construct domain-specific frontmatter structure"""
    pass

@abstractmethod
def _get_schema_name(self) -> str:
    """Return schema name for validation (e.g., 'material_frontmatter')"""
    pass

@abstractmethod
def _get_output_filename(self, identifier: str) -> str:
    """Generate output filename for frontmatter file"""
    pass
```

#### **Provided Methods** (Shared across all domains)

```python
def _enhance_author_voice(self, frontmatter: Dict) -> Dict:
    """
    Apply author voice enhancement to ALL text fields.
    
    Uses: shared/voice/post_processor.py
    Enhances: caption, description, FAQ, subtitle, any text field
    """
    pass

def _validate_schema(self, frontmatter: Dict):
    """
    Validate frontmatter against schema.
    
    Uses: shared/validation/schema_validator.py
    Raises: ValidationError if schema invalid
    """
    pass

def _export_to_file(self, frontmatter: Dict, identifier: str):
    """
    Export frontmatter to YAML file.
    
    Output: content/[domain]/[identifier].md
    Format: YAML frontmatter + Markdown body
    """
    pass
```

---

## 🎭 Domain-Specific Implementations

### **1. Materials Domain** (`domains/materials/`)

#### **Generator**: `UnifiedMaterialsGenerator` (coordinator.py)

**Frontmatter Structure**:
```yaml
---
# Author section (standard)
author:
  name: Todd Dunning
  country: United States
  bio: Materials scientist specializing in laser cleaning

# Content section (materials-specific components)
content:
  caption: "Two paragraphs describing material at 1000x magnification..."
  description: "Technical description focusing on laser cleaning properties..."
  faq: "Q: Why does aluminum respond well to laser cleaning? A: ..."

# Metadata section (standard)
metadata:
  title: "Aluminum"
  slug: "aluminum"
  datePublished: "2025-11-27"
  dateModified: "2025-11-27"

# Properties section (materials-specific)
materialProperties:
  density: 2.70
  meltingPoint: 660.3
  thermalConductivity: 237
  absorptionCoefficient1064nm: 0.08
  laserResponseCharacteristics:
    optimalFluence: "2-5 J/cm²"
    removalMechanism: "Photothermal ablation"
    surfaceQuality: "Excellent"

# Machine settings section (materials-specific)
machineSettings:
  wavelength:
    min: 1064
    max: 1064
    typical: 1064
  pulseWidth:
    min: 10
    max: 150
    typical: 50
---
```

#### **Domain-Specific Prompts**:
- `domains/materials/prompts/caption.txt` - Material caption focusing on contamination removal
- `domains/materials/prompts/material_description.txt` - Technical properties for laser cleaning
- `domains/materials/prompts/faq.txt` - Common material questions

#### **Content Strategy**:
```
caption.txt excerpt:
"You are {author} from {country}, writing a caption about {material}.

TASK: Write two short paragraphs describing {material} at 1000x magnification.
- Paragraph 1: Contaminated surface before laser cleaning  
- Paragraph 2: Clean surface after laser treatment"
```

**Key Focus**: Material properties relevant to laser cleaning (absorption, thermal response, surface quality)

---

### **2. Contaminants Domain** (`domains/contaminants/`)

#### **Generator**: `ContaminantFrontmatterGenerator` (generator.py)

**Frontmatter Structure**:
```yaml
---
# Author section (standard)
author:
  name: Todd Dunning
  country: United States
  bio: Contamination removal specialist

# Content section (contaminant-specific components)
content:
  caption: "Two paragraphs describing contamination before/after removal..."
  description: "Technical description of contaminant removal process..."
  faq: "Q: What laser settings remove rust most effectively? A: ..."

# Metadata section (standard)
metadata:
  title: "Rust (Iron Oxide)"
  slug: "rust-iron-oxide"
  datePublished: "2025-11-27"

# Properties section (contaminant-specific)
contaminantProperties:
  chemicalComposition: "Fe₂O₃, FeOOH"
  thickness: "5-500 micrometers"
  adhesionStrength: "Medium to high"
  laserRemovalCharacteristics:
    removalMechanism: "Selective photothermolysis"
    typicalFluence: "3-8 J/cm²"
    removalEfficiency: "95-99%"
    surfaceQualityPostRemoval: "Excellent"

# Visual appearance section (contaminant-specific)
visualAppearance:
  color: "Orange-brown to dark brown"
  texture: "Rough, flaky, porous"
  morphology: "Layered oxide structure"
---
```

#### **Domain-Specific Prompts**:
- `domains/contaminants/prompts/caption.txt` - Contamination removal focus
- `domains/contaminants/prompts/description.txt` - Contaminant characteristics
- `domains/contaminants/prompts/faq.txt` - Removal process questions

#### **Content Strategy**:
```
(Would be in caption.txt):
"You are {author} from {country}, writing about {contaminant} removal.

TASK: Write two short paragraphs describing contaminated surface treatment.
- Paragraph 1: Surface with {contaminant} contamination
- Paragraph 2: Clean surface after laser removal"
```

**Key Focus**: Contamination characteristics, removal mechanisms, cleaning effectiveness

---

### **3. Applications Domain** (`domains/applications/`)

#### **Generator**: `ApplicationFrontmatterGenerator` (generator.py)

**Frontmatter Structure**:
```yaml
---
# Author section (standard)
author:
  name: Todd Dunning
  country: United States
  bio: Industrial laser cleaning specialist

# Content section (application-specific components)
content:
  caption: "Two paragraphs describing application use case..."
  description: "Industry-specific laser cleaning applications..."
  faq: "Q: What are the benefits for aerospace? A: ..."

# Metadata section (standard)
metadata:
  title: "Aerospace Manufacturing"
  slug: "aerospace-manufacturing"
  datePublished: "2025-11-27"

# Properties section (application-specific)
applicationProperties:
  industry: "Aerospace"
  commonMaterials: ["Aluminum", "Titanium", "Composites"]
  commonContaminants: ["Oxide layers", "Paint", "Sealants"]
  processRequirements:
    cleanlinessStandard: "Class 100 cleanroom"
    traceabilityRequired: true
    nonDestructive: true
  benefits:
    - "Zero chemical waste"
    - "Precision cleaning"
    - "No surface damage"
  challenges:
    - "Composite material sensitivity"
    - "Certification requirements"
---
```

**Key Focus**: Industry use cases, common materials/contaminants, process requirements

---

### **4. Regions Domain** (`domains/regions/`)

#### **Generator**: `RegionFrontmatterGenerator` (generator.py - to be implemented)

**Frontmatter Structure**:
```yaml
---
# Author section (standard)
author:
  name: Todd Dunning
  country: United States

# Content section (region-specific components)
content:
  caption: "Industrial laser cleaning landscape in {region}..."
  description: "Regional regulatory and market overview..."
  faq: "Q: What are the regulations in {region}? A: ..."

# Metadata section (standard)
metadata:
  title: "European Union"
  slug: "european-union"
  datePublished: "2025-11-27"

# Properties section (region-specific)
regionProperties:
  geographicArea: "27 member states"
  regulatoryFramework:
    - "REACH compliance"
    - "CE marking required"
    - "Waste disposal directive"
  marketCharacteristics:
    adoptionRate: "High"
    keyIndustries: ["Automotive", "Aerospace", "Heritage"]
  culturalConsiderations:
    preferredApproach: "Environmental sustainability"
    documentation: "Comprehensive traceability"
---
```

**Key Focus**: Regional regulations, market characteristics, cultural approaches

---

## 🔧 Mandatory Post-Processing (Shared Infrastructure)

All generated content goes through mandatory post-processing, regardless of domain.

### **1. AI Detection** (`shared/voice/ai_detection.py`)

**Purpose**: Detect AI-generated patterns that need enhancement.

**Detection Categories**:
- Grammatical errors (unusual for AI)
- Repetitive patterns (formulaic structure)
- Unnatural phrasing (corporate jargon, academic language)
- AI-specific patterns (theatrical language, generic transitions)

**API**:
```python
from shared.voice.ai_detection import AIDetector

detector = AIDetector()
result = detector.detect_ai_patterns(text)

# Result structure:
{
    'is_ai_like': bool,
    'confidence': float,  # 0-100
    'patterns_found': List[str],
    'recommendations': List[str]
}
```

**Integration Point**: Called before author voice enhancement to determine enhancement strategy.

---

### **2. Author Voice Enhancement** (`shared/voice/post_processor.py`)

**Purpose**: Enhance text with author-specific voice markers for authenticity.

**Process**:
1. **Language Detection**: Verify text is in English (prevent enhancement of translations)
2. **Voice Analysis**: Score current voice authenticity (0-100)
3. **Enhancement Strategy**: Determine adjustments needed based on author profile
4. **API Enhancement**: Apply voice markers via Grok API
5. **Validation**: Verify enhancement improved authenticity without over-adjustment

**API**:
```python
from shared.voice.post_processor import VoicePostProcessor

processor = VoicePostProcessor(api_client, temperature=0.4)

enhanced_text = processor.enhance(
    text="Original technical text here",
    author={
        'name': 'Todd Dunning',
        'country': 'United States'
    },
    component_type='caption',  # Optional: contextual hint
    material_name='Aluminum'   # Optional: domain context
)
```

**Author Profiles** (`shared/voice/profiles/`):
```yaml
todd_dunning:
  country: United States
  writing_style:
    - Direct, practical
    - Active voice
    - Straightforward descriptions
    - Grounded in observation
  avoid:
    - Corporate jargon
    - Theatrical language
    - Academic formality
  sentence_patterns:
    - Varied lengths
    - Different openings
    - Complete sentences
```

**Integration Point**: Called for ALL text fields in frontmatter (caption, description, FAQ, etc.)

---

### **3. Schema Validation** (`shared/validation/schema_validator.py`)

**Purpose**: Validate frontmatter structure matches expected schema.

**Validation Checks**:
- Required fields present
- Field types correct (string, number, dict, list)
- Nested structure valid
- Value ranges within bounds
- Cross-field consistency

**API**:
```python
from shared.validation.schema_validator import SchemaValidator

validator = SchemaValidator()
is_valid, errors = validator.validate(
    data=frontmatter,
    schema_name='material_frontmatter'
)

if not is_valid:
    raise ValidationError(f"Schema validation failed: {errors}")
```

**Schema Definitions** (`shared/schemas/`):
```python
# shared/schemas/base.py
@dataclass
class ContentSchema(ABC):
    """Base schema for all content types"""
    content_type: str
    name: str
    category: str
    
    # Standard sections
    author: Dict[str, Any]
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    
    # Domain-specific properties
    custom_fields: Dict[str, Any]
```

**Integration Point**: Called after frontmatter construction, before export.

---

### **4. Quality Scanning** (`shared/voice/quality_scanner.py`)

**Purpose**: Comprehensive quality checks for generated content.

**Scan Categories**:
- Voice authenticity score
- AI pattern detection
- Language verification
- Structural integrity
- Readability metrics

**API**:
```python
from shared.voice.quality_scanner import VoiceQualityScanner

scanner = VoiceQualityScanner()
quality_report = scanner.scan(
    text=frontmatter['content']['caption'],
    author=frontmatter['author']
)

# Report structure:
{
    'overall_quality': float,  # 0-100
    'voice_authenticity': float,
    'ai_detection': Dict,
    'readability': Dict,
    'issues': List[str],
    'recommendations': List[str]
}
```

**Integration Point**: Called after author voice enhancement, before final export.

---

## 🎨 Domain-Specific Prompt Strategy

### **Why Domain-Specific Prompts?**

Each domain has unique content requirements that cannot be generalized:

| Domain | Content Focus | Unique Requirements |
|--------|--------------|---------------------|
| **Materials** | Laser cleaning properties | Material behavior under laser, absorption characteristics, thermal response |
| **Contaminants** | Removal characteristics | Contamination types, removal mechanisms, cleaning effectiveness |
| **Applications** | Use case scenarios | Industry needs, process requirements, benefits/challenges |
| **Regions** | Regulatory landscape | Local regulations, market characteristics, cultural considerations |
| **Thesaurus** | Terminology | Definitions, usage context, related terms |

### **Prompt Location Strategy**

```
WRONG (violates Domain Independence Policy):
shared/prompts/caption.txt  # ❌ Cannot handle all domains

RIGHT (domain-specific):
domains/materials/prompts/caption.txt      # ✅ Material-specific
domains/contaminants/prompts/caption.txt   # ✅ Contaminant-specific
domains/applications/prompts/caption.txt   # ✅ Application-specific
```

### **Prompt Template Variables**

Each domain defines its own template variables:

**Materials Domain**:
```
{author}      - Author name
{country}     - Author country
{material}    - Material name
{category}    - Material category
{technical_guidance}  - Material-specific technical notes
{sentence_guidance}   - Sentence structure rules
```

**Contaminants Domain**:
```
{author}      - Author name
{country}     - Author country
{contaminant} - Contaminant type
{mechanism}   - Removal mechanism
{surface_guidance}  - Surface quality expectations
```

**Applications Domain**:
```
{author}       - Author name
{country}      - Author country
{application}  - Application name
{industry}     - Industry sector
{use_case_guidance}  - Industry-specific context
```

---

## 🔄 Generation Workflow (Complete Flow)

### **Example: Material Caption Generation**

```
1. User Command:
   python3 run.py --caption "Aluminum"

2. CLI Handler (shared/commands/generation.py):
   - Parse command
   - Load configuration
   - Determine content type (material)
   - Determine component type (caption)

3. Domain Coordinator (domains/materials/coordinator.py):
   - Load Materials.yaml
   - Extract material data for "Aluminum"
   - Validate material exists

4. Component Generator (shared/pipeline/content_pipeline.py):
   - Load domain-specific prompt (domains/materials/prompts/caption.txt)
   - Populate template variables:
     * {author} = "Todd Dunning"
     * {country} = "United States"
     * {material} = "Aluminum"
     * {technical_guidance} = Material-specific notes
   - Send prompt to Grok API

5. Initial Generation:
   Raw AI output: "Aluminum surfaces contaminated with oxide layers..."

6. AI Detection (shared/voice/ai_detection.py):
   - Scan for AI patterns
   - Detect any corporate jargon, theatrical language
   - Generate enhancement recommendations

7. Author Voice Enhancement (shared/voice/post_processor.py):
   - Load author profile (Todd Dunning)
   - Apply voice markers:
     * Direct, practical language
     * Active voice
     * Varied sentence structures
     * Grounded observations
   - Enhanced output: "Oxide layers build up on aluminum..."

8. Quality Scanning (shared/voice/quality_scanner.py):
   - Voice authenticity: 87/100 ✓
   - AI patterns: None detected ✓
   - Readability: Good ✓
   - Pass quality gates

9. Schema Validation (shared/validation/schema_validator.py):
   - Validate caption field structure
   - Verify length requirements
   - Check nested frontmatter structure

10. Save to Materials.yaml:
    materials:
      Aluminum:
        caption: "Enhanced caption text..."
        author: "Todd Dunning"

11. Export Frontmatter (export/core/):
    - Build complete frontmatter structure
    - Add metadata (datePublished, slug, etc.)
    - Add materialProperties (density, melting point, etc.)
    - Add machineSettings (wavelength, pulse width, etc.)
    - Export to: content/materials/aluminum.md

12. Frontmatter Sync (export/):
    - Update frontmatter file with new caption
    - Preserve all other fields (description, FAQ, properties)
    - Write YAML frontmatter + Markdown body
```

---

## 📊 Frontmatter Structure Comparison

### **Common Structure (All Domains)**

```yaml
---
# SECTION 1: Author (identical across all domains)
author:
  name: string
  country: string
  bio: string

# SECTION 2: Content (components vary by domain)
content:
  caption: string        # Present in all domains
  description: string    # Present in all domains
  faq: string           # Present in all domains
  # Domain-specific components may be added

# SECTION 3: Metadata (identical across all domains)
metadata:
  title: string
  slug: string
  datePublished: string (ISO 8601)
  dateModified: string (ISO 8601)
  tags: list[string]

# SECTION 4: Properties (domain-specific)
[domainName]Properties:
  # Completely different for each domain
---
```

### **Domain-Specific Properties**

#### **Materials Domain**:
```yaml
materialProperties:
  # Physical properties
  density: number
  meltingPoint: number
  thermalConductivity: number
  
  # Laser properties
  absorptionCoefficient1064nm: number
  laserResponseCharacteristics:
    optimalFluence: string
    removalMechanism: string
    surfaceQuality: string

machineSettings:
  wavelength: {min, max, typical}
  pulseWidth: {min, max, typical}
  fluence: {min, max, typical}
  scanSpeed: {min, max, typical}
```

#### **Contaminants Domain**:
```yaml
contaminantProperties:
  # Chemical properties
  chemicalComposition: string
  thickness: string
  adhesionStrength: string
  
  # Removal characteristics
  laserRemovalCharacteristics:
    removalMechanism: string
    typicalFluence: string
    removalEfficiency: string
    surfaceQualityPostRemoval: string

visualAppearance:
  color: string
  texture: string
  morphology: string
```

#### **Applications Domain**:
```yaml
applicationProperties:
  industry: string
  commonMaterials: list[string]
  commonContaminants: list[string]
  
  processRequirements:
    cleanlinessStandard: string
    traceabilityRequired: bool
    nonDestructive: bool
  
  benefits: list[string]
  challenges: list[string]
```

---

## 🎯 Adding a New Domain

### **Step-by-Step Process**

#### **1. Create Domain Directory**

```bash
mkdir -p domains/new_domain/{prompts,research,modules}
touch domains/new_domain/__init__.py
touch domains/new_domain/generator.py
touch domains/new_domain/data_loader.py
```

#### **2. Implement Generator** (`domains/new_domain/generator.py`)

```python
from export.core.base_generator import BaseFrontmatterGenerator, GenerationContext

class NewDomainFrontmatterGenerator(BaseFrontmatterGenerator):
    """Frontmatter generator for new domain"""
    
    def __init__(self, api_client=None, config=None, **kwargs):
        super().__init__(
            content_type='new_domain',
            api_client=api_client,
            config=config,
            **kwargs
        )
    
    def _load_type_data(self):
        """Load new_domain-specific data"""
        # Load data/new_domain/NewDomain.yaml
        pass
    
    def _validate_identifier(self, identifier: str) -> bool:
        """Validate identifier exists"""
        # Check identifier in loaded data
        pass
    
    def _build_frontmatter_data(self, data: Dict) -> Dict:
        """Build frontmatter structure"""
        return {
            'author': self._build_author_section(data),
            'content': self._build_content_section(data),
            'metadata': self._build_metadata_section(data),
            'newDomainProperties': self._build_properties_section(data)
        }
    
    def _get_schema_name(self) -> str:
        return 'new_domain_frontmatter'
    
    def _get_output_filename(self, identifier: str) -> str:
        return f"{identifier.lower().replace(' ', '-')}.md"
```

#### **3. Create Domain-Specific Prompts**

**File**: `domains/new_domain/prompts/caption.txt`
```
You are {author} from {country}, writing about {domain_item}.

TASK: Write two short paragraphs describing {domain_item} in context.
- Paragraph 1: Introduction and context
- Paragraph 2: Key characteristics and relevance

VOICE & APPROACH:
Write like you're explaining to a colleague - direct, practical, grounded.

FORMATTING:
- Complete sentences
- Vary sentence lengths
- Separate paragraphs with ONE blank line
- NO labels like "Context:", "Characteristics:"

OUTPUT: Just the two paragraphs.
```

#### **4. Define Schema** (`shared/schemas/new_domain_schema.py`)

```python
from dataclasses import dataclass, field
from shared.schemas.base import ContentSchema

@dataclass
class NewDomainSchema(ContentSchema):
    """Schema for new domain content"""
    
    # Domain-specific properties
    newDomainProperties: Dict[str, Any] = field(default_factory=dict)
    
    def get_required_fields(self) -> List[str]:
        return ['name', 'category', 'newDomainProperties']
    
    def validate(self) -> Tuple[bool, List[str]]:
        # Custom validation logic
        pass
```

#### **5. Create Data File**

**File**: `data/new_domain/NewDomain.yaml`
```yaml
new_domain_items:
  item_one:
    name: "Item One"
    category: "Category A"
    properties:
      property1: "value1"
      property2: "value2"
  
  item_two:
    name: "Item Two"
    category: "Category B"
    properties:
      property1: "value3"
      property2: "value4"
```

#### **6. Register Generator**

**File**: `shared/commands/generation.py` (add to generator factory)
```python
def get_generator(content_type: str):
    generators = {
        'material': UnifiedMaterialsGenerator,
        'contaminant': ContaminantFrontmatterGenerator,
        'application': ApplicationFrontmatterGenerator,
        'new_domain': NewDomainFrontmatterGenerator  # Add here
    }
    return generators.get(content_type)
```

#### **7. Add CLI Command**

**File**: `run.py` (add command-line argument)
```python
parser.add_argument(
    '--new-domain',
    type=str,
    help='Generate frontmatter for new domain item'
)
```

---

## 🔍 Key Architectural Benefits

### **1. Separation of Concerns**

- **Shared Infrastructure**: Handles universal concerns (AI detection, voice, validation)
- **Domain Logic**: Focuses on domain-specific content strategy (prompts, properties)
- **Clear Boundaries**: No cross-domain contamination

### **2. Consistency**

- **Standard Pipeline**: All domains follow same generation flow
- **Mandatory Post-Processing**: AI detection + voice enhancement for all content
- **Uniform Output**: Same frontmatter structure (author, content, metadata, properties)

### **3. Extensibility**

- **Easy to Add Domains**: Implement 5 abstract methods, create prompts, done
- **Easy to Add Components**: Create prompt template, add to component list
- **Easy to Add Properties**: Extend domain-specific properties section

### **4. Maintainability**

- **Single Source of Truth**: Each domain has one generator, one prompt directory
- **Shared Utilities**: Post-processing logic in one place (shared/voice/)
- **Clear Documentation**: This file + domain-specific READMEs

### **5. Testability**

- **Unit Testing**: Test each component independently
- **Integration Testing**: Test complete pipeline with mock data
- **Domain Testing**: Test domain-specific logic in isolation

---

## 🚨 Anti-Patterns to Avoid

### **❌ DO NOT: Put domain-specific logic in shared infrastructure**

```python
# WRONG (shared/voice/post_processor.py)
if content_type == 'material':
    # Material-specific enhancement
elif content_type == 'contaminant':
    # Contaminant-specific enhancement
```

**Why**: Violates separation of concerns, creates tight coupling.

**RIGHT**: Domain-specific logic stays in domain generators, shared infrastructure uses generic parameters.

---

### **❌ DO NOT: Use generic prompts for all domains**

```python
# WRONG (shared/prompts/caption.txt)
You are {author}, writing a caption about {item}.
# Generic prompt cannot handle material vs contaminant vs application nuances
```

**Why**: Each domain has unique content strategy that requires specialized prompts.

**RIGHT**: Each domain has its own prompt directory with domain-specific templates.

---

### **❌ DO NOT: Skip mandatory post-processing**

```python
# WRONG (domains/new_domain/generator.py)
def generate(self, identifier):
    frontmatter = self._build_frontmatter_data(...)
    # Skip AI detection
    # Skip author voice enhancement
    # Export directly
    self._export_to_file(frontmatter)
```

**Why**: Breaks consistency, produces lower quality content, defeats unified architecture.

**RIGHT**: Use `super().generate()` to ensure mandatory post-processing runs.

---

### **❌ DO NOT: Duplicate post-processing logic**

```python
# WRONG (domains/materials/voice_enhancer.py)
# Duplicating shared/voice/post_processor.py functionality
```

**Why**: Creates maintenance burden, divergent behavior, violates DRY principle.

**RIGHT**: Import and use `shared/voice/post_processor.py`.

---

## 📚 Related Documentation

- **Base Generator**: `export/core/base_generator.py` - Abstract base class documentation
- **Domain Independence Policy**: `DOMAIN_INDEPENDENCE_POLICY.md` - Cross-domain rules
- **Post-Processor Guide**: `shared/voice/README.md` - Author voice enhancement details
- **Schema Documentation**: `shared/schemas/base.py` - ContentSchema architecture
- **Materials Domain**: `domains/materials/README.md` - Reference implementation
- **Contaminants Domain**: `domains/contaminants/README.md` - Second implementation
- **🔥 Minimal Domain Proposal**: `MINIMAL_DOMAIN_ARCHITECTURE_PROPOSAL.md` - Reduce duplication by 82% (**RECOMMENDED READING**)

---

## 🔮 Future Architecture Direction

### **Current Duplication Issue**

The current architecture has **4 domain generators** (applications, contaminants, regions, thesaurus) with nearly identical code (~200-230 lines each = 853 lines total duplication).

**The Problem**: Only difference is property section naming (`contaminantProperties` vs `applicationProperties`)

### **Proposed Solution**

See **[MINIMAL_DOMAIN_ARCHITECTURE_PROPOSAL.md](./MINIMAL_DOMAIN_ARCHITECTURE_PROPOSAL.md)** for detailed proposal:

- **Single universal generator** (150 lines) replaces all 4 specialized generators
- **Configuration-driven approach** (config.yaml defines structure)
- **Prompts remain domain-specific** (the main user interface - 12 new prompt files)
- **82% code reduction** (853 → 150 lines)
- **Materials exception** (keeps specialized generator due to complexity)

**Benefits**:
- ✅ Zero code duplication
- ✅ Configuration-driven (YAML not Python)
- ✅ Prompts as primary interface (easier to customize)
- ✅ Add new domain in 1 hour (vs 4+ hours)
- ✅ Easier maintenance (fix once, applies everywhere)

**Migration Time**: ~9.5 hours over 2 business days

**Status**: 🔄 Proposal ready for review

---

## 🎓 Summary

The Z-Beam Generator uses a **domain-agnostic frontmatter generation architecture** where:

1. **BaseFrontmatterGenerator** provides abstract base class enforcing standard pipeline
2. **Domain-specific generators** implement abstract methods for custom content strategy
3. **Domain-specific prompts** handle unique content requirements for each domain
4. **Mandatory post-processing** (AI detection + author voice) applies to ALL domains
5. **Shared infrastructure** handles common concerns (validation, quality, export)
6. **Uniform output structure** (author, content, metadata, properties) across all domains

This architecture enables:
- ✅ **Consistency**: Same quality standards across all domains
- ✅ **Extensibility**: Easy to add new domains (5 methods + prompts)
- ✅ **Maintainability**: Clear separation of concerns
- ✅ **Quality**: Mandatory post-processing ensures human-like voice
- ✅ **Testability**: Independent testing at each layer

**Result**: A scalable content generation system that produces high-quality, domain-specific frontmatter with consistent author voice across materials, contaminants, applications, regions, and future domains.
