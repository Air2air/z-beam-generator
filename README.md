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

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd z-beam-generator
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   GOOGLE_API_KEY=your_google_api_key_here
   ```

5. **Verify installation:**
   ```bash
   python run.py --help
   ```

---

## 🚀 Example Usage

### Basic Generation
```bash
# Generate a material article
python run.py --article-type material --subject "Aluminum"

# Generate an application article
python run.py --article-type application --subject "Graffiti Removal"

# Generate a region article
python run.py --article-type region --subject "San Jose"

# Generate a thesaurus article
python run.py --article-type thesaurus --subject "Fluence"

# Generate with specific author
python run.py --article-type material --subject "Aluminum" --author-id "john_doe"
```

### Output Location
Generated articles are saved to the `output/` directory with filenames like:
- `aluminum_laser_cleaning.md`
- `graffiti_removal_laser_cleaning.md`
- `san_jose_laser_cleaning.md`
- `fluence.md`

---

## ⚙️ Configuration

### AI Provider Configuration
Set your preferred AI provider by adding to your `.env` file:

```env
# Required: At least one API key
OPENAI_API_KEY=sk-your-openai-key
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
GOOGLE_API_KEY=your-google-api-key

# Optional: Default provider (defaults to OpenAI)
DEFAULT_AI_PROVIDER=openai
```

### Author Configuration
Edit `authors/authors.json` to add or modify author information:

```json
{
  "john_doe": {
    "name": "John Doe",
    "bio": "Laser cleaning specialist with 15 years experience",
    "email": "john@example.com",
    "expertise": ["industrial cleaning", "surface preparation"]
  }
}
```

---

## 🔧 Troubleshooting

### Common Issues

**1. "No API key found" error**
- Ensure your `.env` file is in the root directory
- Check that environment variable names match exactly
- Verify your API keys are valid

**2. "Schema file not found" error**
- Check that schema files exist in `schemas/definitions/`
- Ensure filenames follow the pattern: `{type}_schema_definition.json`

**3. "Invalid JSON in schema" error**
- Validate your schema JSON files using `python -m json.tool schema_file.json`
- Check for trailing commas or syntax errors

**4. "Generation failed" error**
- Check your internet connection
- Verify API key permissions
- Review logs for specific error messages

**5. Module import errors**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Debug Mode
Enable verbose logging by setting environment variable:
```bash
export LOG_LEVEL=DEBUG
python run.py --article-type material --subject "Steel" --verbose
```

### Validation
Run the validation script to check your setup:
```bash
python scripts/validate_setup.py
```

---

## Extending the System

- To add a new article type, create a new schema file in `schemas/definitions/` (as JSON).
- Update context in `run.py` to use the new type.
- No changes to generator or orchestrator code are required; only context and schema files need updating.
- The system will dynamically adapt to the new schema without code changes.

---

## 🔌 API Client Architecture

### Supported Providers
The system supports these AI providers through a unified interface:

```python
# api_client.py structure
class APIClient:
    def __init__(self, provider):
        self.provider = provider  # No default - set in run.py
        self.client = self._get_client()
    
    def generate(self, prompt, max_tokens=1000):
        # Returns standardized response regardless of provider
        pass
```

### Provider Configuration
- **XAI**: Uses Grok models
- **GEMINI**: Uses Google Gemini Pro
- **DEEPSEEK**: Uses DeepSeek models  
- **OPENAI**: Uses GPT-4 models

### Rate Limiting
- Built-in retry logic with exponential backoff
- Respects provider-specific rate limits
- Logs all API calls for debugging

### Environment Variables
```env
XAI_API_KEY=your-xai-key
GEMINI_API_KEY=your-gemini-key
DEEPSEEK_API_KEY=your-deepseek-key
OPENAI_API_KEY=your-openai-key
```

---

## ✅ Schema Validation Framework

### Validation Requirements
The validator ensures **100% field completion** for:

1. **Metadata Fields**: Every field in the schema's metadata section must be populated
2. **JSON-LD Fields**: Every field in the schema's structured data section must be complete

### Validation Rules
- **No Empty Strings**: All fields must have meaningful content
- **No Null Values**: All fields must be populated
- **No Missing Fields**: Every schema field must be present in output
- **Type Consistency**: Values must match expected data types

### Schema-Agnostic Validation
```python
def validate_schema_completion(output, schema):
    """Validate that ALL schema fields are populated."""
    for section_name, section_schema in schema.items():
        if "metadata" in section_name.lower() or "jsonld" in section_name.lower():
            validate_all_fields_populated(output[section_name], section_schema)
```

### Validation Failure Handling
- **No Partial Output**: If any required field is missing/empty, no file is generated
- **Detailed Logging**: Specific fields that failed validation are logged
- **Schema Flexibility**: Validator adapts to any schema structure automatically

---

## ⚡ Performance & Resource Management

### No Caching Strategy
- **Fresh Generation**: Every request generates new content
- **No Template Caching**: Schemas loaded fresh each time
- **No API Response Caching**: All API calls are live requests

### Resource Management
- **Memory Usage**: Efficient JSON parsing for large schemas
- **API Limits**: Built-in rate limiting and quota management
- **Sequential Processing**: One article at a time for simplicity

### Local Development Focus
- **File System**: Direct local file I/O
- **Simple Logging**: Console and file logging
- **No External Dependencies**: Self-contained operation

---

## 🔄 Development Workflow

### Adding New Article Types
1. Create schema file: `schemas/definitions/newtype_schema_definition.json`
2. Add placeholder mapping to context mapping table
3. Update CLI choices in `run.py`
4. Set your preferred AI provider in `run.py`
5. Test with sample data

### Schema Development Process
**⚠️ Schema Structure Changes Frequently**

1. Design schema structure (completely unique per type)
2. Validate JSON syntax: `python -m json.tool schema_file.json`
3. Test field completion: `python run.py --article-type newtype --subject "Test"`
4. Verify ALL fields are populated in output
5. Update placeholder mappings if needed

### Schema Flexibility
- No standardized field names
- No common structure requirements
- Validator adapts to any schema format
- Complete freedom in schema design

---

## 🏠 Local Development Environment

### Environment Variables
```env
# All four API keys from your .env
XAI_API_KEY
GEMINI_API_KEY
DEEPSEEK_API_KEY
OPENAI_API_KEY

# Optional Configuration
LOG_LEVEL=INFO
OUTPUT_DIR=./output
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

### File Structure
- **Local Only**: No deployment considerations
- **Direct File I/O**: Simple file system operations
- **Console Interface**: Rich console output for development

### Testing Approach
- **Schema Validation**: Test that all fields are populated
- **API Integration**: Test with actual API calls
- **Field Completion**: Verify no empty or missing fields