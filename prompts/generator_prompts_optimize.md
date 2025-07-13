component="JSON-LD only"

I have a prompt that I need you to optimize.  The prompt is used to generate {component} for a given article type related to Laser Cleaning (ex: "application", "material", "region", "thesaurus term") and subject (ex: "Cleaning for weld surface preparation", "Masonry", "Palo Alto", "fluence").

1. Schema Loading: Loads extensive schema from application_schema_definition.json
2. Field Extraction: Extracts all fields from [articleType]Profile section
3. Prompt Building: Dynamically builds field-specific instructions for each generator
4. LLM Processing: Sends prompts to AI provider (DeepSeek) via API
5. Content Generation: LLM returns structured content (YAML metadata, tags list, JSON-LD)
6. File Output: Saves 3 components to local files in output directory

The output of the prompt must adhere to latest and best practices for {component}.

------------------------------------------------------

Prompt:

name: "JSON-LD Generator"
description: "Generates comprehensive JSON-LD for technical articles"
version: "1.0.0"

template: |
  Generate comprehensive JSON-LD for a {article_type} article about {subject}.



  SCHEMA FIELDS FOR JSON-LD MAPPING:
  {schema_template}

  JSON-LD MAPPING METHODOLOGY:
  - Map EVERY schema field that is applicable to appropriate Schema.org properties
  - Create nested objects for complex schema fields
  - Use arrays for schema fields containing multiple values
  - Maintain Schema.org vocabulary compliance
  - Include rich structured data for all field types
  - Use technical precision in all mappings

  OUTPUT FORMAT REQUIREMENTS:
  - Return ONLY valid JSON
  - NO markdown code blocks
  - NO explanatory text
  - NO comments
  - Start with { and end with }
  - Use proper JSON syntax throughout

  CRITICAL REQUIREMENTS:
  - Use nested objects and arrays appropriately
  - Generate rich, comprehensive structured data
  - Maintain valid JSON syntax
  - Include quantitative and technical specifications

  Generate the complete JSON-LD structure now:

parameters:
  max_tokens: 4000
  temperature: 0.7

validation:
  required_fields:
    - "@context"
    - "@type"
    - "headline"
    - "description"
  min_length: 2000
  schema_org_type: "TechnicalArticle"
  required_schema_coverage: 100