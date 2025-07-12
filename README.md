# Z-Beam Generator

A sophisticated AI-powered content generation system for laser cleaning articles. Generates comprehensive articles using discrete schema-driven templates.

---

## 🚨 CRITICAL REQUIREMENT: SCHEMA-DRIVEN GENERATION

**⚠️ ABSOLUTE RULE: ALL FIELDS MUST BE SCHEMA-DRIVEN**

- **NO DEFAULT VALUES** – Every field must come from the schema
- **NO FALLBACKS** – If a field isn't in the schema, it should not exist
- **NO HARDCODED METADATA** – All metadata, tags, and JSON-LD must be schema-defined
- **DYNAMIC ONLY** – All content must be dynamically generated from schema templates
- **SCHEMA IS THE SOURCE OF TRUTH** – No code should add, modify, or override schema content

**❌ ABSOLUTELY FORBIDDEN:**
- Default titles, descriptions, or metadata
- Hardcoded tag lists
- Generic JSON-LD structures
- Fallback values of any kind
- Code-generated metadata
- Additional processing of schema output

**✅ REQUIRED:**
- All fields sourced from schema definition.json files (see below)
- Dynamic placeholder replacement (e.g., `{{materialName}}`, `{{term}}`)
- Schema-defined metadata structures
- Template-driven content generation
- Pure schema passthrough

---

## 🎯 Schema-First Architecture

- **Schemas define EVERYTHING** – structure, content, metadata, tags, JSON-LD
- **Code only replaces placeholders** – no content generation in code
- **Output = Schema output** – no additional processing

---

## 📋 Article Types & Schema Files

All schema definitions are stored in the `schemas/definitions/` directory as `*definition.json` files.  
**Format:** Each file contains a valid JSON object.

| Article Type | Schema File                                 | Placeholder        | Example Filename |
|--------------|---------------------------------------------|--------------------|------------------|
| application  | application_schema_definition.json          | `{{applicationName}}` | `graffiti_removal_laser_cleaning.md` |
| material     | material_schema_definition.json             | `{{materialName}}`    | `aluminum_laser_cleaning.md` |
| region       | region_schema_definition.json               | `{{regionName}}`      | `san_jose_laser_cleaning.md` |
| thesaurus    | thesaurus_schema_definition.json            | `{{term}}`            | `fluence.md` |

**The system is fully dynamic and driven only by these schema definitions.**  
No content, field, or logic is hardcoded—every output and validation step is determined by the active schema file.

To add or change article types, simply add or update schema files in `schemas/definitions/`.  
**Only the context in `run.py` needs updating to use a new type. No changes to generator or orchestrator code are required.**

---

## 🔧 Placeholder Mapping Logic

The context key `"subject"` is generic and must be mapped to the correct schema placeholder for each article type:

| article_type | Placeholder        |
|--------------|-------------------|
| material     | materialName      |
| application  | applicationName   |
| region       | regionName        |
| thesaurus    | term              |

All generators and prompt builders must replace schema placeholders with the value of `"subject"` from context, mapped according to `article_type`.

Prompt builders are responsible for mapping context keys to schema placeholders and inserting system placeholders.

System placeholders such as `{{generation_timestamp}}`, `{{model_used}}`, `{{lastUpdated}}`, and `{{publishedAt}}` are replaced by code in the orchestrator before sending the prompt to the LLM.

---

## 🚨 **TROUBLESHOOTING & COMMON ISSUES**

### **🔥 Virtual Environment Corruption (Most Common Issue)**
**Symptoms:**
- `pip install` fails with Rich/text module errors
- Dependencies show as installed but imports fail
- `ModuleNotFoundError` for basic packages like `click`

**Solution:**
````bash
# Remove corrupted environment
deactivate
rm -rf .venv

# Create fresh environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies individually
pip install python-dotenv
pip install requests
pip install PyYAML
pip install jsonschema
pip install pytest
pip install "pydantic>=2.0.0"
pip install "click>=8.0.0"
pip install "rich>=13.0.0"
`````

# At the top of any script
import os
from pathlib import Path

def load_env_file():
    """Load .env file manually."""
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load before any other imports
load_env_file()
``````

# Debug AI responses
def debug_ai_response(response):
    print("📝 Raw Response:")
    print(repr(response))  # Shows exact characters
    
    print("📝 Response Length:", len(response))
    
    # Check for common issues
    if response.startswith('{'):
        print("❌ AI returned JSON instead of YAML")
    if len(response) > 1000 and not response.strip().endswith(('}', ']')):
        print("❌ Response appears truncated")
    if '"type": "string"' in response:
        print("❌ AI returned schema instead of data")
    if not ':' in response:
        print("❌ Response doesn't appear to be YAML")
```````

## 🚨 **CURRENT LIMITATIONS & KNOWN ISSUES**

### **🔍 Response Length Issues (High Priority)**
**Problem**: Generated responses are too short and lack comprehensive content depth
**Current Status**: 
- Metadata: Basic fields only, missing detailed technical specifications
- Tags: Limited scope, missing industry-specific and technical depth
- JSON-LD: Minimal structure, lacks comprehensive schema utilization
- Overall: Content feels abbreviated rather than comprehensive

**Impact**: 
- Reduces SEO value due to insufficient content depth
- Limits technical usefulness for professional applications
- Doesn't fully utilize the rich schema definitions available

**Next Steps**: 
- Increase content depth and technical detail
- Expand prompt instructions for comprehensive responses
- Add more technical specifications and industry context
- Enhance schema utilization for richer content generation

### **📊 Current vs. Target Output Analysis**

**Current Output Characteristics:**
- Metadata: ~25 fields with basic values
- Tags: ~20 tags, mostly generic
- JSON-LD: Standard Schema.org structure
- Total Content: Abbreviated professional level

**Target Output Characteristics:**
- Metadata: ~40+ fields with detailed technical specifications
- Tags: ~30+ tags covering all technical aspects
- JSON-LD: Rich Schema.org structure with comprehensive mentions
- Total Content: In-depth technical documentation quality

### **🎯 Content Enhancement Roadmap**

**Phase 1: Immediate Improvements**
1. **Expand Prompt Instructions**: Add requirements for comprehensive, detailed responses
2. **Increase Token Limits**: Raise to 3000+ tokens for complex content generation
3. **Add Technical Depth Requirements**: Specify industry-standard technical detail levels
4. **Schema Utilization**: Ensure all available schema fields are fully utilized

**Phase 2: Advanced Features**
1. **Content Body Generation**: Add actual article content (not just metadata)
2. **Technical Specifications**: Detailed laser parameters, safety protocols, standards
3. **Industry Case Studies**: Real-world application examples
4. **Comparative Analysis**: Performance vs. traditional cleaning methods

**Phase 3: Production Enhancement**
1. **Multi-Section Articles**: Introduction, technical details, applications, conclusion
2. **Visual Content Integration**: Placeholder for diagrams, charts, tables
3. **Related Content**: Cross-references and further reading
4. **Quality Scoring**: Automated content depth assessment

### **🔧 Immediate Action Items**

**For Next Development Session:**
1. **Analyze Schema Depth**: Review all schema definitions for unused rich content
2. **Prompt Enhancement**: Rewrite prompts to demand comprehensive responses
3. **Token Optimization**: Increase limits and test response quality
4. **Content Validation**: Add checks for minimum content depth and technical detail

**Success Metrics to Track:**
- Average response length (current: short → target: comprehensive)
- Technical detail density (current: basic → target: professional)
- Schema field utilization (current: partial → target: complete)
- Professional readiness (current: abbreviated → target: publication-ready)

### **⚠️ Current System Status**

**✅ What's Working:**
- Schema-driven architecture
- Multi-provider AI integration
- Error handling and validation
- Professional formatting structure

**🔄 What Needs Enhancement:**
- **Content depth and comprehensiveness**
- **Technical detail richness**
- **Full schema utilization**
- **Professional-grade content length**

**🎯 Priority Focus:**
Making the generated content comprehensive enough for professional technical documentation and industry publication standards.

---

## 🚀 **DEVELOPMENT PRIORITY: CONTENT DEPTH**

**Current Challenge**: Responses are too short and lack the comprehensive technical depth needed for professional documentation.

**Next Session Goals:**
1. Analyze why responses are abbreviated
2. Enhance prompts for comprehensive content generation
3. Increase token limits and optimize for detailed responses
4. Ensure full utilization of rich schema definitions
5. Add content quality validation and depth scoring

**Success Criteria**: Generated articles should be comprehensive enough for professional technical publication, with rich technical detail, comprehensive coverage of all relevant aspects, and industry-standard depth.

**📝 Note**: This is a high-priority enhancement that will significantly improve the professional value and usability of the generated content.

---

# Z-Beam Generator Documentation

## Core Principles

### 1. Schema-Driven Only Approach
- **NO fallbacks or defaults** - All generators must fail fast when schema incomplete
- **NO manual field extraction** - Only use schema-defined `example` fields
- **NO hardcoded values** - Everything must come from schema definitions
- **Fail fast philosophy** - Return `None` immediately when required schema fields missing

### 2. Schema Structure Requirements
All schemas must follow this pattern:
```json
{
  "name": "article-type",
  "version": "1.0",
  "schemaType": "LaserCleaning[Type]Profile",
  
  "[articleType]Profile": {
    "fieldName": {
      "type": "string",
      "required": true,
      "description": "Field description",
      "example": "{{placeholder}}"
    }
  }
}
```

### 3. Required Schema Profiles
- **Material Schema**: `materialProfile` with `{{materialName}}` placeholders
- **Application Schema**: `applicationProfile` with `{{applicationName}}` placeholders  
- **Thesaurus Schema**: `termProfile` with `{{term}}` placeholders
- **Region Schema**: `regionProfile` with `{{regionName}}` placeholders

### 4. Generator Architecture
Each generator follows this pattern:
```python
class Generator:
    def __init__(self, context, schema, ai_provider):
        # NO DEFAULT VALUES - Must come from context
        self.subject = context["subject"]  # Will fail if not provided
        self.article_type = context["article_type"]  # Will fail if not provided
    
    def generate(self):
        prompt = self._build_prompt()
        if not prompt:
            return None  # FAIL FAST - NO FALLBACK
    
    def _build_schema_template(self):
        profile_key = f"{self.article_type}Profile"
        if profile_key in self.schema:
            return self._build_from_profile(profile)
        else:
            return None  # NO FALLBACK - FAIL FAST
```

## System Components

### 1. Metadata Generator
- **Purpose**: Generate YAML metadata from schema examples
- **Input**: Schema with `example` fields
- **Output**: Comprehensive YAML metadata
- **Compliance**: ✅ Schema-driven only, no fallbacks

### 2. Tags Generator  
- **Purpose**: Generate tags from schema examples
- **Input**: Schema with `example` fields
- **Output**: List of kebab-case tags
- **Compliance**: ✅ Schema-driven only, no fallbacks

### 3. JSON-LD Generator
- **Purpose**: Generate Schema.org JSON-LD from schema examples
- **Input**: Schema with `example` fields  
- **Output**: Valid JSON-LD structure
- **Compliance**: ✅ Schema-driven only, no fallbacks

## Schema Normalization Lessons

### Problem Identified
- **Material schema** had `example` fields, worked correctly
- **Application, Thesaurus, Region schemas** lacked `example` fields, failed

### Solution Applied
Added `example` fields to all schema profiles:
```json
"fieldName": {
  "type": "string",
  "required": true,
  "description": "Field description",
  "example": "{{placeholder}}"
}
```

### Generator Logic Fix
Updated all generators to look in correct profile section:
```python
def _build_schema_template(self):
    profile_key = f"{self.article_type}Profile"  # applicationProfile, etc.
    if profile_key in self.schema:
        return self._build_from_profile(self.schema[profile_key])
    else:
        return None  # NO FALLBACK
```

## Key Debugging Insights

### 1. Schema Field Detection
Generators must look in `[articleType]Profile` section, not root schema:
- ✅ `schema["applicationProfile"]["name"]["example"]`
- ❌ `schema["name"]["example"]`

### 2. Null Content Error Pattern
When generators send `"content": null` to AI providers:
- **Root Cause**: Generator couldn't find schema fields
- **Symptom**: 422/400 errors from AI providers
- **Solution**: Fix schema template building logic

### 3. Validation Field Mapping
Ensure validation configs match schema field names:
- Schema uses `name` field
- Validation should require `name`, not `title`

## AI Provider Integration

### DeepSeek Specifics
- **Model**: `deepseek-chat`
- **Error Pattern**: 422 errors when content is null
- **Solution**: Ensure generators build valid prompts before API calls

### OpenAI Specifics  
- **Model**: `gpt-4o-mini`
- **Error Pattern**: 400 "Invalid value for content" when null
- **Solution**: Same as DeepSeek - fix generator logic

## File Structure Requirements

### Schema Organization
```
schemas/definitions/
├── material_schema_definition.json     # materialProfile only
├── application_schema_definition.json  # applicationProfile only  
├── thesaurus_schema_definition.json    # termProfile only
└── region_schema_definition.json       # regionProfile only
```

### Generator Organization
```
generators/
├── metadata/
│   ├── generator.py      # Schema-driven metadata generation
│   └── prompt.yaml       # Metadata prompt template
├── tags/
│   ├── generator.py      # Schema-driven tags generation  
│   └── prompt.yaml       # Tags prompt template
└── jsonld/
    ├── generator.py      # Schema-driven JSON-LD generation
    └── prompt.yaml       # JSON-LD prompt template
```

## Testing Approach

### Validation Commands
```bash
# Test each article type
python run.py --article-type material --subject "Aluminum"
python run.py --article-type application --subject "Rust Removal"  
python run.py --article-type thesaurus --subject "Ablation"
python run.py --article-type region --subject "North America"
```

### Expected Success Pattern
```
✅ Found applicationProfile with X fields
✅ Found example in [field names]
✅ Generated X template parts
✅ Successfully generated content with [ai_provider]
✅ Successfully generated schema-driven [component]
```

## Compliance Checklist

For each generator:
- [ ] ✅ No fallback methods or logic
- [ ] ✅ No default values or hardcoded content
- [ ] ✅ Only uses schema `example` fields
- [ ] ✅ Fails fast when schema incomplete
- [ ] ✅ Returns `None` instead of fallback content
- [ ] ✅ Looks in correct `[articleType]Profile` section
- [ ] ✅ Proper placeholder replacement logic