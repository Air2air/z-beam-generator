# Z-Beam Generator

A sophisticated AI-powered content generation system for laser cleaning articles. Generates comprehensive articles using discrete schema-driven templates.

## 🚨 CRITICAL REQUIREMENT: SCHEMA-DRIVEN GENERATION

**⚠️ ABSOLUTE RULE: ALL FIELDS MUST BE SCHEMA-DRIVEN**

- **NO DEFAULT VALUES** - Every field must come from the schema
- **NO FALLBACKS** - If a field isn't in the schema, it should not exist
- **NO HARDCODED METADATA** - All metadata, tags, and JSON-LD must be schema-defined
- **DYNAMIC ONLY** - All content must be dynamically generated from schema templates
- **SCHEMA IS THE SOURCE OF TRUTH** - No code should add, modify, or override schema content

**❌ ABSOLUTELY FORBIDDEN:**
- Default titles, descriptions, or metadata
- Hardcoded tag lists
- Generic JSON-LD structures
- Fallback values of any kind
- Code-generated metadata
- Additional processing of schema output

**✅ REQUIRED:**
- All fields sourced from schema YAML definitions
- Dynamic placeholder replacement (e.g., `{{materialName}}`, `{{term}}`)
- Schema-defined metadata structures
- Template-driven content generation
- Pure schema passthrough

## 🎯 Schema-First Architecture

### **Complete Schema Control**
- **Schemas define EVERYTHING** - structure, content, metadata, tags, JSON-LD
- **Code only replaces placeholders** - no content generation in code
- **Output = Schema output** - no additional processing

### **Zero Code Intervention**
- Generator only processes schema templates
- Orchestrator only returns schema output
- No metadata generation in code
- No hardcoded values anywhere

## 🚀 Quick Start

1. **Edit Configuration** (top of `run.py`):
```python
# Article Context
context = {
    "subject": "hafnium",         # Subject to write about
    "author_id": 2,              # Author style (1-4)
    "article_type": "material"   # application, material, region, thesaurus
}
```

2. **Run Generation**:
```bash
python3 run.py
```

3. **Check Output**: Article generated in `output/` directory

## 📋 Article Types & Schema Files

### **Application Articles** (`application`)
- **Schema**: `schemas/application_schema_prompt.md`
- **Purpose**: Industry-specific use cases and applications
- **Placeholder**: `{{applicationName}}`

### **Material Articles** (`material`)
- **Schema**: `schemas/material_schema_prompt.md`
- **Purpose**: Material-specific laser cleaning guides
- **Placeholder**: `{{materialName}}`

### **Region Articles** (`region`)
- **Schema**: `schemas/region_schema_prompt.md`
- **Purpose**: Geographic and regional applications
- **Placeholder**: `{{regionName}}`

### **Thesaurus Articles** (`thesaurus`)
- **Schema**: `schemas/thesaurus_schema_prompt.md`
- **Purpose**: Comprehensive terminology and definitions
- **Placeholder**: `{{term}}`

## 🔧 Schema Placeholder System

### **Dynamic Replacements**
```
{{materialName}} → "hafnium"
{{applicationName}} → "automotive_restoration"
{{regionName}} → "southeast_asia"
{{term}} → "fluence"
{{authorName}} → "Mario Jordan"
{{authorTitle}} → "Senior Laser Applications Engineer"
{{authorCountry}} → "Italy"
```

### **System Placeholders**
```
{{generation_timestamp}} → Current ISO timestamp
{{model_used}} → API provider/model
{{lastUpdated}} → Current date
{{publishedAt}} → Current date
```

## 🚨 Validation Rules

### **Schema Compliance**
- Every field in output must exist in schema
- No fields should be added by code
- All content must be schema-generated
- Placeholders must be completely replaced

### **Forbidden Patterns**
```python
# ❌ NEVER DO THIS
title = f"Guide to {subject}"
metadata = {"default": "value"}
tags = ["#Default", "#Tags"]
```

### **Required Patterns**
```python
# ✅ ONLY DO THIS
content = api_client.call(schema_with_placeholders)
return content  # No modifications
```

## 🏗️ System Flow

```
1. Load Schema → 2. Replace Placeholders → 3. Send to LLM → 4. Return Output
```

**NO additional steps, processing, or modifications**

## 📊 Schema Validation

### **Output Verification**
- Compare generated output with schema template
- Verify all placeholders are replaced
- Ensure no code-generated content exists
- Check all metadata comes from schema

### **Common Violations**
- Adding metadata not in schema
- Generating tags outside schema
- Creating JSON-LD not defined in schema
- Any code-based content generation

---

**⚠️ REMEMBER: Schemas are the ONLY source of truth. Code must never add, modify, or override schema content.**