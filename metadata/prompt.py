def build_metadata_prompt(context, schema):
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
You are an expert technical writer.
Using ONLY the schema definition below, generate the metadata for a laser cleaning article.

Schema:
{schema['generatorConfig']['metadata']}

Context:
Replace {{{{{subject_placeholder}}}}} with "{subject}".
Replace all other placeholders with values from context.

Instructions:
- Do NOT add any fields or content not defined in the schema.
- Return the metadata as a valid YAML frontmatter block.
"""
    return prompt