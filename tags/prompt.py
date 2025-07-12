def build_tags_prompt(context, schema):
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
You are an expert in SEO and technical tagging.
Using ONLY the schema definition below, generate a list of tags for a laser cleaning article.

Schema:
{schema['generatorConfig']['tags']}

Context:
Replace {{{{{subject_placeholder}}}}} with "{subject}".
Replace all other placeholders with values from context.

Instructions:
- Do NOT add any tags or content not defined in the schema.
- Return the tags as a YAML list (e.g., tags: [tag1, tag2, tag3]).
"""
    return prompt