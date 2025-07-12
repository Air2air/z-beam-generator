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