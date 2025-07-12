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

| Article Type | Schema File                                 | Placeholder        |
|--------------|---------------------------------------------|--------------------|
| application  | application_schema_definition.json          | `{{applicationName}}` |
| material     | material_schema_definition.json             | `{{materialName}}`    |
| region       | region_schema_definition.json               | `{{regionName}}`      |
| thesaurus    | thesaurus_schema_definition.json            | `{{term}}`            |

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

## 🏗️ End-to-End System Flow

1. **Load Context & Schema:**  
   - `run.py` sets the context (`ARTICLE_CONTEXT`) and loads the appropriate schema from `schemas/definitions/`.
2. **Orchestration:**  
   - `orchestrator.py` creates dedicated generator instances for metadata, tags, and JSON-LD.
3. **Generation:**  
   - Each generator (`metadata/generator.py`, `tags/generator.py`, `jsonld/generator.py`) uses its own prompt builder and submits its own LLM API call, strictly following the schema and context mapping logic.
4. **Formatting & Output:**  
   - Tags are normalized with `utils/tag_formatter.py`.
   - Output is assembled into Markdown using `utils/output_formatter.py`.
   - The final file is saved to the `output/` directory.
5. **Validation:**  
   - Output is validated against the schema using `utils/schema_validator.py`.
   - If validation fails, no output is written and an error is logged.

**At no point does code generate content; it only replaces placeholders and assembles schema-driven output.**

---

## Error Handling & Logging

- All major steps and errors are logged using Python's logging module.
- If required context fields or API keys are missing, generation fails with a clear error.
- Output validation failures halt the process and log the issue.

---

## Directory Structure

```
z-beam-generator/
├── run.py
├── orchestrator.py
├── api_client.py
├── metadata/
│   ├── generator.py
│   └── prompt.py
├── tags/
│   ├── generator.py
│   └── prompt.py
├── jsonld/
│   ├── generator.py
│   └── prompt.py
├── utils/
│   ├── setup_logging.py
│   ├── schema_validator.py
│   ├── tag_formatter.py
│   └── output_formatter.py
├── authors/
│   ├── author_utils.py
│   └── authors.json
├── schemas/
│   └── definitions/
│       ├── application_schema_definition.json
│       ├── material_schema_definition.json
│       ├── region_schema_definition.json
│       └── thesaurus_schema_definition.json
├── output/
└── tests/
    └── test_generator.py
```

---

## Extending the System

- To add a new article type, create a new schema file in `schemas/definitions/` (as JSON).
- Update context in `run.py` to use the new type.
- No changes to generator or orchestrator code are required; only context and schema files need updating.
- The system will dynamically adapt to the new schema without code changes.

---

**⚠️ REMEMBER:**  
Schemas in `schemas/definitions/` are the ONLY source of truth.  
Code must never add, modify, or override schema content.  
The system is fully dynamic and adapts to any valid schema definition, using context mapping as described