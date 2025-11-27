# Minimal Domain Architecture Proposal

**Date**: November 27, 2025  
**Status**: 🔄 PROPOSAL  
**Purpose**: Minimize domain-specific code while preserving text prompts as the primary user interface

---

## 🎯 Executive Summary

**Current State**: 80 Python files across domains with duplicated generator logic (4 generators: applications, contaminants, regions, thesaurus each ~200-230 lines)

**Proposed State**: **Single universal generator + domain-specific prompts and data files**

**Key Insight**: All domains follow identical patterns except for:
1. **Prompts** (the main user interface - domain-specific content strategy)
2. **Data structure** (properties section naming: materialProperties, contaminantProperties, etc.)
3. **Data files** (domains/[name]/data.yaml)

**Result**: Reduce 800+ lines of duplicated generator code to ~50 lines of configuration per domain.

---

## 📊 Current Architecture Analysis

### **Duplication Identified**

All 4 domain generators (applications, contaminants, regions, thesaurus) implement identical logic:

```python
# REPEATED IN ALL 4 GENERATORS (~200 lines each):
class [Domain]FrontmatterGenerator(BaseFrontmatterGenerator):
    def __init__(self, api_client, config, **kwargs):
        super().__init__(content_type='[domain]', ...)
    
    def _load_type_data(self):
        # Load data.yaml from same directory
        data_file = Path(__file__).parent / 'data.yaml'
        with open(data_file) as f:
            data = yaml.safe_load(f)
            self._[items] = data.get('[items]', {})
    
    def _validate_identifier(self, identifier: str):
        # Normalize and check if exists
        identifier_key = identifier.lower().replace(' ', '_')
        if identifier_key not in self._[items]:
            raise GenerationError(...)
    
    def _build_frontmatter_data(self, identifier, context):
        # Build structure: author + content + metadata + properties
        return {
            'author': {...},
            'content': {...},
            'metadata': {...},
            '[domain]Properties': {...}  # ONLY DIFFERENCE
        }
    
    def _get_schema_name(self):
        return '[domain]_frontmatter'
    
    def _get_output_filename(self, identifier):
        return f"{identifier}-laser-cleaning.yaml"
```

**Total Duplication**: 800+ lines (4 generators × ~200 lines each)

**What's Different**: Only the property section name (`materialProperties`, `contaminantProperties`, etc.)

### **What's Unique Per Domain (Should Stay)**

```
domains/[name]/
├── prompts/                  # ✅ KEEP - Main user interface
│   ├── caption.txt
│   ├── description.txt
│   └── faq.txt
└── data.yaml                 # ✅ KEEP - Domain data
```

**Materials prompts** (3 files):
- Focus on laser cleaning properties, material behavior
- Variables: {material}, {category}, {technical_guidance}

**Contaminants prompts** (0 files currently - TODO):
- Should focus on removal mechanisms, contamination characteristics
- Variables: {contaminant}, {removal_mechanism}, {surface_guidance}

**Applications prompts** (0 files currently - TODO):
- Should focus on industry use cases, process requirements
- Variables: {application}, {industry}, {use_case_guidance}

**Regions prompts** (0 files currently - TODO):
- Should focus on regulations, market characteristics
- Variables: {region}, {regulatory_framework}, {market_notes}

---

## 🏗️ Proposed Architecture

### **1. Single Universal Generator**

Create **one** generator that works for all domains:

```python
# export/core/universal_domain_generator.py

class UniversalDomainGenerator(BaseFrontmatterGenerator):
    """
    Universal generator for all domains (applications, contaminants, regions, thesaurus).
    
    Configuration-driven approach:
    - Domain configuration in domains/[name]/config.yaml
    - Prompts in domains/[name]/prompts/*.txt
    - Data in domains/[name]/data.yaml
    
    Zero domain-specific code needed.
    """
    
    def __init__(
        self,
        domain_name: str,  # 'applications', 'contaminants', 'regions', etc.
        api_client=None,
        config=None,
        **kwargs
    ):
        """Initialize universal generator for specified domain"""
        self.domain_name = domain_name
        self.domain_path = Path(__file__).parent.parent.parent / 'domains' / domain_name
        
        # Load domain configuration
        self.domain_config = self._load_domain_config()
        
        super().__init__(
            content_type=domain_name,
            api_client=api_client,
            config=config,
            **kwargs
        )
    
    def _load_domain_config(self) -> Dict[str, Any]:
        """
        Load domain configuration from domains/[name]/config.yaml
        
        Configuration specifies:
        - data_key: Key in data.yaml containing items (e.g., 'contaminants')
        - property_section: Name of properties section (e.g., 'contaminantProperties')
        - identifier_field: Field name for item (e.g., 'contaminant_name')
        - output_pattern: Filename pattern (e.g., '{identifier}-removal.yaml')
        - schema_name: Schema for validation (e.g., 'contaminant_frontmatter')
        """
        config_file = self.domain_path / 'config.yaml'
        with open(config_file) as f:
            return yaml.safe_load(f)
    
    def _load_type_data(self):
        """Load domain data from domains/[name]/data.yaml"""
        data_file = self.domain_path / 'data.yaml'
        with open(data_file) as f:
            data = yaml.safe_load(f)
            data_key = self.domain_config['data_key']
            self._items = data.get(data_key, {})
            self.logger.info(f"Loaded {len(self._items)} {data_key} from {data_file}")
    
    def _validate_identifier(self, identifier: str) -> bool:
        """Universal validation - checks item exists"""
        identifier_key = identifier.lower().replace(' ', '_').replace('-', '_')
        if identifier_key not in self._items:
            raise GenerationError(
                f"{self.domain_name.title()} '{identifier}' not found. "
                f"Available: {', '.join(self._items.keys())}"
            )
        return True
    
    def _build_frontmatter_data(self, identifier: str, context: GenerationContext) -> Dict[str, Any]:
        """Universal frontmatter builder - uses config to determine structure"""
        identifier_key = identifier.lower().replace(' ', '_').replace('-', '_')
        item_data = self._items[identifier_key]
        
        # Property section name from config (e.g., 'contaminantProperties')
        property_section = self.domain_config['property_section']
        
        frontmatter = {
            'author': context.author_data or {},
            'content': {
                'caption': item_data.get('caption', ''),
                'description': item_data.get('description', ''),
                'faq': item_data.get('faq', '')
            },
            'metadata': {
                'title': item_data.get('name', identifier),
                'slug': identifier_key,
                'datePublished': datetime.now().isoformat(),
                'dateModified': datetime.now().isoformat()
            },
            property_section: item_data.get('properties', {})
        }
        
        return frontmatter
    
    def _get_schema_name(self) -> str:
        """Get schema name from config"""
        return self.domain_config['schema_name']
    
    def _get_output_filename(self, identifier: str) -> str:
        """Get output filename from config pattern"""
        pattern = self.domain_config.get('output_pattern', '{identifier}-laser-cleaning.yaml')
        normalized = identifier.lower().replace(' ', '-').replace('_', '-')
        return pattern.format(identifier=normalized)
```

**Lines of Code**: ~150 lines (vs 800+ lines currently)

---

### **2. Domain Configuration Files**

Each domain has a simple config file defining its structure:

#### **domains/contaminants/config.yaml**

```yaml
# Domain configuration for contaminants
domain_name: contaminants
display_name: Contaminant

# Data loading
data_key: contaminants              # Key in data.yaml
identifier_field: contaminant_name  # Optional: field name in data

# Frontmatter structure
property_section: contaminantProperties  # Name of properties section in frontmatter
schema_name: contaminant_frontmatter     # Schema for validation

# Output configuration
output_pattern: "{identifier}-removal.yaml"  # Filename pattern
output_directory: "content/contaminants/"    # Export directory

# Prompt variables (for template population)
prompt_variables:
  - contaminant      # Primary identifier
  - category         # Contamination category
  - removal_mechanism
  - surface_guidance

# Optional: Custom sections
custom_sections:
  - visual_appearance
  - laser_removal_characteristics
```

#### **domains/applications/config.yaml**

```yaml
# Domain configuration for applications
domain_name: applications
display_name: Application

data_key: applications
identifier_field: application_name

property_section: applicationProperties
schema_name: application_frontmatter

output_pattern: "{identifier}-use-case.yaml"
output_directory: "content/applications/"

prompt_variables:
  - application
  - industry
  - use_case_guidance

custom_sections:
  - common_materials
  - common_contaminants
  - process_requirements
```

#### **domains/regions/config.yaml**

```yaml
# Domain configuration for regions
domain_name: regions
display_name: Region

data_key: regions
identifier_field: region_name

property_section: regionProperties
schema_name: region_frontmatter

output_pattern: "{identifier}-market.yaml"
output_directory: "content/regions/"

prompt_variables:
  - region
  - regulatory_framework
  - market_notes

custom_sections:
  - regulatory_framework
  - market_characteristics
  - cultural_considerations
```

#### **domains/thesaurus/config.yaml**

```yaml
# Domain configuration for thesaurus
domain_name: thesaurus
display_name: Term

data_key: terms
identifier_field: term_name

property_section: termProperties
schema_name: term_frontmatter

output_pattern: "{identifier}-definition.yaml"
output_directory: "content/thesaurus/"

prompt_variables:
  - term
  - category
  - usage_context

custom_sections:
  - definitions
  - related_terms
  - usage_examples
```

**Lines Per Domain**: ~25-35 lines (vs ~200-230 lines of Python code)

---

### **3. Prompt Files (Main User Interface)**

**Prompts remain domain-specific** - this is the primary user interface where content strategy is defined.

#### **Create Missing Prompt Files**

Currently only **materials** domain has prompts (3 files). Need to create for other domains:

##### **domains/contaminants/prompts/caption.txt**

```
You are {author} from {country}, writing about {contaminant} removal.

TASK: Write two short paragraphs describing contaminated surface treatment.
- Paragraph 1: Surface with {contaminant} contamination characteristics
- Paragraph 2: Clean surface after laser removal process

VOICE & APPROACH:
Write like you're explaining removal results to a colleague - direct, practical, focused on the transformation.

REMOVAL CONTEXT:
{removal_mechanism}

SURFACE QUALITY:
{surface_guidance}

FORMATTING:
- Complete sentences (no fragments)
- Vary sentence lengths (mix short, medium, longer)
- Start each sentence differently
- Separate the two paragraphs with ONE blank line
- NO labels like "Before:", "After:", "Contaminated:", "Clean:"

AVOID:
- Corporate jargon: "facilitates", "leverages", "demonstrates"
- Theatrical: "magically removed", "disappears", "transforms instantly"
- Academic: "results suggest", "testament to"
- Repetitive openings

OUTPUT: Just the two paragraphs.

Generate caption for {contaminant} removal:
```

##### **domains/contaminants/prompts/description.txt**

```
You are {author} from {country}, writing a technical description of {contaminant}.

TASK: Describe the contamination type, its characteristics, and laser removal approach.

CONTENT FOCUS:
- What is {contaminant}? (composition, formation)
- Where does it occur? (common surfaces, conditions)
- How does laser removal work? (mechanism: {removal_mechanism})
- What are the results? (removal efficiency, surface quality)

VOICE & APPROACH:
Technical but accessible. Explain the science without jargon overload.

STRUCTURE:
3-4 paragraphs:
1. Contamination characteristics
2. Removal mechanism
3. Process parameters and results
4. (Optional) Special considerations or limitations

AVOID:
- Marketing language
- Overly academic tone
- Repetitive sentence structures
- Lists (write in paragraph form)

OUTPUT: Complete description (150-250 words).
```

##### **domains/applications/prompts/caption.txt**

```
You are {author} from {country}, writing about {application} in the {industry} industry.

TASK: Write two short paragraphs about laser cleaning application.
- Paragraph 1: The challenge or need in this industry
- Paragraph 2: How laser cleaning addresses it

VOICE & APPROACH:
Write like you're explaining a use case to a colleague - practical, focused on real-world benefits.

INDUSTRY CONTEXT:
{use_case_guidance}

FORMATTING:
- Complete sentences
- Vary sentence lengths
- Start each sentence differently
- Separate paragraphs with ONE blank line
- NO labels

AVOID:
- Sales language: "revolutionary", "game-changing"
- Generic claims: "improves efficiency", "reduces costs" (be specific)
- Repetitive patterns

OUTPUT: Just the two paragraphs.
```

##### **domains/regions/prompts/caption.txt**

```
You are {author} from {country}, writing about laser cleaning in {region}.

TASK: Write two short paragraphs about the regional context.
- Paragraph 1: Market characteristics and adoption in {region}
- Paragraph 2: Regulatory environment and key considerations

VOICE & APPROACH:
Informative, balanced, grounded in regional realities.

REGULATORY CONTEXT:
{regulatory_framework}

MARKET NOTES:
{market_notes}

FORMATTING:
- Complete sentences
- Vary sentence lengths
- Separate paragraphs with ONE blank line
- NO labels

AVOID:
- Stereotypes or generalizations
- Marketing language
- Political commentary
- Oversimplification

OUTPUT: Just the two paragraphs.
```

**Prompt Strategy**: Each domain's prompts focus on what's unique about that domain's content needs.

---

## 📋 Migration Plan

### **Phase 1: Create Universal Generator** (2 hours)

1. Create `export/core/universal_domain_generator.py`
2. Implement configuration-driven logic
3. Add tests for universal generator

### **Phase 2: Add Domain Configurations** (1 hour)

1. Create `config.yaml` for each domain:
   - `domains/contaminants/config.yaml`
   - `domains/applications/config.yaml`
   - `domains/regions/config.yaml`
   - `domains/thesaurus/config.yaml`

### **Phase 3: Create Missing Prompts** (3 hours)

1. **Contaminants prompts** (3 files):
   - `caption.txt` - Removal before/after
   - `description.txt` - Contamination characteristics
   - `faq.txt` - Common removal questions

2. **Applications prompts** (3 files):
   - `caption.txt` - Industry use case
   - `description.txt` - Application details
   - `faq.txt` - Industry-specific questions

3. **Regions prompts** (3 files):
   - `caption.txt` - Market/regulatory overview
   - `description.txt` - Regional characteristics
   - `faq.txt` - Regional questions

4. **Thesaurus prompts** (3 files):
   - `caption.txt` - Term introduction
   - `description.txt` - Detailed definition
   - `faq.txt` - Usage questions

### **Phase 4: Update Generator Factory** (30 minutes)

Update `shared/commands/generation.py`:

```python
def get_generator(content_type: str):
    """Get appropriate generator for content type"""
    
    # Materials uses existing specialized generator
    if content_type == 'material':
        from domains.materials.coordinator import UnifiedMaterialsGenerator
        return UnifiedMaterialsGenerator
    
    # All other domains use universal generator
    from export.core.universal_domain_generator import UniversalDomainGenerator
    
    def create_generator(*args, **kwargs):
        return UniversalDomainGenerator(
            domain_name=content_type,
            *args,
            **kwargs
        )
    
    return create_generator
```

### **Phase 5: Deprecate Old Generators** (30 minutes)

1. Mark old generators as deprecated:
   - `domains/applications/generator.py` → Add deprecation notice
   - `domains/contaminants/generator.py` → Add deprecation notice
   - `domains/regions/generator.py` → Add deprecation notice
   - `domains/thesaurus/generator.py` → Add deprecation notice

2. Add compatibility shim (temporary):
```python
# domains/contaminants/generator.py (deprecated)
from export.core.universal_domain_generator import UniversalDomainGenerator

class ContaminantFrontmatterGenerator(UniversalDomainGenerator):
    """DEPRECATED: Use UniversalDomainGenerator instead"""
    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn(
            "ContaminantFrontmatterGenerator is deprecated. "
            "Use UniversalDomainGenerator(domain_name='contaminants') instead.",
            DeprecationWarning
        )
        super().__init__(domain_name='contaminants', *args, **kwargs)
```

### **Phase 6: Test & Validate** (2 hours)

1. Test each domain with universal generator:
   ```bash
   python3 run.py --contaminant "rust" --caption
   python3 run.py --application "aerospace" --description
   python3 run.py --region "european_union" --faq
   python3 run.py --term "fluence" --caption
   ```

2. Validate output structure matches expected schema
3. Verify prompts load correctly
4. Test author voice processing
5. Validate exported frontmatter files

### **Phase 7: Remove Deprecated Code** (30 minutes)

After validation period (1 week):

1. Delete deprecated generators:
   ```bash
   rm domains/applications/generator.py
   rm domains/contaminants/generator.py
   rm domains/regions/generator.py
   rm domains/thesaurus/generator.py
   ```

2. Update documentation

**Total Migration Time**: ~9.5 hours

---

## 📊 Before & After Comparison

### **Current Architecture**

```
domains/
├── applications/
│   └── generator.py                 # 211 lines
├── contaminants/
│   └── generator.py                 # 229 lines
├── regions/
│   └── generator.py                 # 215 lines
├── thesaurus/
│   └── generator.py                 # 198 lines
└── materials/
    └── coordinator.py               # (kept - specialized)

Total: 853 lines of duplicated code
Prompts: 3 files (materials only)
```

### **Proposed Architecture**

```
export/core/
└── universal_domain_generator.py    # 150 lines (shared)

domains/
├── applications/
│   ├── config.yaml                  # 30 lines
│   ├── data.yaml                    # (existing)
│   └── prompts/                     # 3 files (NEW)
│       ├── caption.txt
│       ├── description.txt
│       └── faq.txt
├── contaminants/
│   ├── config.yaml                  # 35 lines (NEW)
│   ├── data.yaml                    # (existing)
│   └── prompts/                     # 3 files (NEW)
│       ├── caption.txt
│       ├── description.txt
│       └── faq.txt
├── regions/
│   ├── config.yaml                  # 30 lines (NEW)
│   ├── data.yaml                    # (existing)
│   └── prompts/                     # 3 files (NEW)
│       ├── caption.txt
│       ├── description.txt
│       └── faq.txt
├── thesaurus/
│   ├── config.yaml                  # 28 lines (NEW)
│   ├── data.yaml                    # (existing)
│   └── prompts/                     # 3 files (NEW)
│       ├── caption.txt
│       ├── description.txt
│       └── faq.txt
└── materials/
    ├── coordinator.py               # (kept - specialized)
    └── prompts/                     # 3 files (existing)
        ├── caption.txt
        ├── description.txt
        └── faq.txt

Total Python: 150 lines (shared generator)
Config: 123 lines (4 × ~30 lines)
Prompts: 15 files (5 domains × 3 files)
```

### **Code Reduction**

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Python LOC (generators) | 853 | 150 | **-82%** |
| Files per domain | 1 Python | 1 config + 3 prompts | More maintainable |
| Prompt files | 3 (materials only) | 15 (all domains) | +400% coverage |
| Duplicated code | High | Zero | Eliminated |
| Configuration complexity | Embedded in code | Declarative YAML | Simpler |

---

## 🎯 Benefits

### **1. Dramatic Code Reduction**

- **Before**: 853 lines of duplicated generator code
- **After**: 150 lines of shared universal generator
- **Savings**: 82% reduction in code

### **2. Prompts as Primary Interface**

- **12 new prompt files** created (contaminants, applications, regions, thesaurus)
- **Prompts define content strategy** - no code changes needed for content variations
- **Easy to customize**: Edit text file vs modifying Python code
- **Version control friendly**: Text diffs are clear and reviewable

### **3. Configuration-Driven**

- **Add new domain**: Create config.yaml + prompts directory (no Python code)
- **Modify structure**: Edit config.yaml (no code changes)
- **Test variations**: Change config and re-run (instant)

### **4. Maintainability**

- **Single source of truth**: One generator for all domains
- **Bug fixes**: Fix once, applies to all domains
- **Feature additions**: Add to universal generator, all domains benefit
- **Clear separation**: Logic (Python) vs content strategy (prompts) vs configuration (YAML)

### **5. Consistency**

- **Identical pipeline**: All domains follow same flow
- **Uniform quality**: Same post-processing for all
- **Predictable behavior**: No domain-specific quirks

### **6. Extensibility**

Adding a new domain requires:
1. Create `domains/new_domain/config.yaml` (30 lines)
2. Create `domains/new_domain/prompts/*.txt` (3 files)
3. Create `domains/new_domain/data.yaml` (data structure)

**Total time**: ~1 hour (vs 4+ hours to write custom generator)

---

## 🚨 Considerations & Edge Cases

### **Materials Domain Exception**

**Materials domain keeps specialized generator** (`domains/materials/coordinator.py`) because:

1. **Complex property research**: Multi-field AI research for physical properties
2. **Machine settings integration**: Merges Materials.yaml + MachineSettings.yaml
3. **Category taxonomy**: Complex category-level data loading
4. **Completeness validation**: Strict 100% data coverage enforcement
5. **Historical complexity**: 2,500+ lines with specialized modules

**Decision**: Materials is complex enough to warrant specialized code. Universal generator is for simpler domains.

### **Backward Compatibility**

**Compatibility shims** provided during transition:
- Old generator classes redirect to universal generator
- Deprecation warnings for 1 week
- Remove after validation period

### **Schema Validation**

Each domain needs:
- Schema definition in `shared/schemas/`
- Schema name specified in `config.yaml`
- Validation rules for domain-specific properties

### **Prompt Variable Population**

Universal generator must:
1. Load domain config to get `prompt_variables` list
2. Extract values from data.yaml based on config
3. Populate prompt template with correct variables

**Example**:
```python
# domains/contaminants/config.yaml
prompt_variables:
  - contaminant      # Maps to item name
  - category         # Maps to item.category
  - removal_mechanism  # Maps to item.properties.removal_mechanism
```

---

## 📚 Documentation Updates Required

### **1. Update Architecture Docs**

**File**: `docs/architecture/FRONTMATTER_GENERATION_ARCHITECTURE.md`

Add section:
```markdown
## 🔧 Universal Domain Generator

### When to Use Specialized vs Universal

**Use Specialized Generator** when:
- Complex multi-step data processing required
- Multiple data sources must be merged
- Specialized research modules needed
- Domain has >5 specialized Python modules

**Use Universal Generator** when:
- Simple data.yaml → frontmatter transformation
- Standard property structure
- No specialized research needed
- Prompts define all content strategy

### Current Usage

- **Materials**: Specialized (UnifiedMaterialsGenerator)
- **Contaminants**: Universal ✅
- **Applications**: Universal ✅
- **Regions**: Universal ✅
- **Thesaurus**: Universal ✅
```

### **2. Create Prompt Writing Guide**

**File**: `docs/prompts/PROMPT_WRITING_GUIDE.md`

Content:
- How to write effective domain prompts
- Variable naming conventions
- Voice and tone guidelines
- Testing prompt effectiveness
- Examples from each domain

### **3. Create Domain Configuration Guide**

**File**: `docs/domains/DOMAIN_CONFIGURATION_GUIDE.md`

Content:
- config.yaml structure and fields
- How to add a new domain
- Property section naming conventions
- Custom sections and their usage
- Schema requirements

### **4. Update Domain READMEs**

Each domain needs:
- `domains/contaminants/README.md`
- `domains/applications/README.md`
- `domains/regions/README.md`
- `domains/thesaurus/README.md`

Content:
```markdown
# [Domain] Domain

## Overview
Brief description of domain

## Configuration
Location: `config.yaml`
- Property section: [domainProperties]
- Schema: [domain_frontmatter]
- Output pattern: [pattern]

## Prompts
Location: `prompts/*.txt`
- caption.txt - [Description]
- description.txt - [Description]
- faq.txt - [Description]

## Data Structure
Location: `data.yaml`
[Example structure]

## Generation
```bash
python3 run.py --[domain] "[item]" --caption
python3 run.py --[domain] "[item]" --description
python3 run.py --[domain] "[item]" --faq
```

## Customization
Edit prompts in `prompts/` directory to adjust content strategy.
Edit config in `config.yaml` to modify structure.
```

---

## 🎓 Summary

### **Proposal: Minimal Domain Architecture**

**Core Principle**: Reduce domain-specific code to absolute minimum while keeping prompts as the primary user interface.

**Implementation**:
1. **Single universal generator** (150 lines) replaces 4 specialized generators (853 lines)
2. **Configuration files** (config.yaml) define domain structure
3. **Prompt files** remain domain-specific (12 new files created)
4. **Materials exception** keeps specialized generator due to complexity

**Benefits**:
- ✅ **82% code reduction** (853 → 150 lines)
- ✅ **Prompts as main interface** (15 files total across 5 domains)
- ✅ **Configuration-driven** (add domains via YAML, not Python)
- ✅ **Zero duplication** (shared generator logic)
- ✅ **Easier maintenance** (fix once, applies everywhere)
- ✅ **Better extensibility** (new domain = 1 hour vs 4+ hours)

**Migration**: ~9.5 hours total
- Phase 1: Create universal generator (2h)
- Phase 2: Domain configs (1h)
- Phase 3: Create prompts (3h)
- Phase 4: Update factory (0.5h)
- Phase 5: Deprecate old (0.5h)
- Phase 6: Test (2h)
- Phase 7: Remove old (0.5h)

**Result**: Clean, maintainable architecture with prompts as the primary interface for content strategy definition.

---

## 🚀 Next Steps

1. **Review this proposal** - Discuss approach and edge cases
2. **Approve migration plan** - Confirm phases and timeline
3. **Create universal generator** - Implement Phase 1
4. **Write domain configs** - Implement Phase 2
5. **Create missing prompts** - Implement Phase 3 (critical for user interface)
6. **Test thoroughly** - Validate all domains work
7. **Deploy and monitor** - Roll out with monitoring
8. **Remove deprecated code** - Clean up after validation

**Estimated Completion**: 2 business days with testing

**Risk**: Low - backward compatibility maintained during transition
