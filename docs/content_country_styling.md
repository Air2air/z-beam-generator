# Requirement: Country-Based Author Writing Style for Content Component

## Overview
The content component must support country-based writing styles, reflecting the subtle language patterns of non-native English speakers from specific countries. This is determined by the `author_id` in `ARTICLE_CONTEXT`, which maps to a country in `components/author/authors.json`. Only the `author_id` is passed in from `ARTICLE_CONTEXT`; the frontmatter component is responsible for looking up and injecting the corresponding author fields (such as `author_name` and `author_country`) into the frontmatter.

## Details

- **Author Country Source:**  
  The country is determined by looking up the `author_id` in `components/author/authors.json`. The frontmatter component performs this lookup and adds `author_name` and `author_country` to the frontmatter.

- **Styling Mechanism:**  
  When generating content, the system uses the `author_country` field from the frontmatter to influence the writing style. The output should subtly reflect the language patterns, idioms, and phrasing typical of a non-native English speaker from that country.

- **Prompt Variation:**  
  The content generator uses one of four sub-prompts, each tailored to the country of one of the four authors. These sub-prompts guide the AI to emulate the writing style of a native speaker from the specified country.

- **Configuration:**  
  - `ARTICLE_CONTEXT` includes an `author_id` (int).
  - The frontmatter component looks up and injects `author_name` and `author_country` into the frontmatter.
  - The content component automatically applies the appropriate style based on the `author_country` field in the frontmatter.

- **Effect:**  
  The generated content should read as if written by a non-native English speaker from the author's country, providing a more authentic and regionally nuanced voice.

## Example Workflow

1. `ARTICLE_CONTEXT` specifies `"author_id": 2`.
2. The frontmatter component looks up author 2 in `components/author/authors.json` and finds their country (e.g., "Germany").
3. The frontmatter includes `author_name` and `author_country` (e.g., "Germany").
4. The content generator selects the "Germany" sub-prompt for writing style based on the `author_country` in the frontmatter.
5. The generated article content subtly reflects German-influenced English.