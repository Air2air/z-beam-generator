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