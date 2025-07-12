def build_jsonld_prompt(context, schema):
    article_type = context.get("article_type")
    subject = context.get("subject")
    placeholder_map = {
        "material": "materialName",
        "application": "applicationName",
        "region": "regionName",
        "thesaurus": "term"
    }
    subject_placeholder = placeholder_map.get(article_type, "subject")
    prompt = f"""
You are an expert in structured data and schema.org markup.
Using ONLY the schema definition below, generate a JSON-LD block for a laser cleaning article.

Schema:
{schema['generatorConfig']['jsonld']}

Context:
Replace {{{{{subject_placeholder}}}}} with "{subject}".
Replace all other placeholders with values from context.

Instructions:
- Do NOT add any properties or content not defined in the schema.
- Return the JSON-LD as a valid JSON object, formatted for schema.org.
"""
    return prompt