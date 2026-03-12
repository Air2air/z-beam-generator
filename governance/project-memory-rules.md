# Grok Process & Rules – Laser Cleaning YAML Database (March 2026)

This document records the current agreed-upon rules, procedures, and improvements for Grok-assisted generation in the Z-Beam project.

## Core Schema
- Single shared schema: schemas/all_domains_schema.yaml
- EEAT additions: credentials, ymyLCompliance, biasDisclaimer, sourceLinks array
- Mandatory section pattern: Every sectionTitle / _section must have a sibling sectionDescription (20–70 words, high random variation, surprising structure)

## Text Generation Rules (All Text Fields)
1. Length: Random high variation 20–70 words per field (average ~45, session variance ±15 words)
2. Structure variation: Sentence fragments, embedded lists, inverted phrasing, no repetition
3. Author voice: Random immutable assignment from Authors.yaml (4 authors); neutral US-English base + subtle non-excessive nationality nuance via voice profile
4. Humanness: Multi-agent realism scoring (≥7.0/10), Grok 60% weight, no >20% AI-derived untweaked
5. EEAT: Embed AI disclosure in trustworthiness; use sourceLinks (>2 citations/field, tested non-404); biasDisclaimer if needed

## Upstream vs Downstream Split
- Grok: Research, populate/repair upstream content in aggregates/ (factual wording, descriptions, unusual effects, healthEffects, etc.)
- Python/repo: Downstream validation, normalization, metadata hydration, export to frontmatter
- Never patch frontmatter directly — always fix at source (aggregates/) or in export logic

## Citation & Link Verification Policy (Mandatory)

Every link included in any research, citation, sourceLinks array, riskCitations, or inline reference **must** be:

- Actively tested and verified to load successfully (no 404, no redirect to error page, no paywall block)
- Confirmed to actually contain the specific information claimed (not just a related page)
- Live and publicly accessible at the time of generation

**Strict prohibitions**:
- Placeholder URLs (e.g., example.com, todo-link-here, future-pubchem-url)
- Untested or assumed links
- Links that require login/subscription unless explicitly marked as such

**Enforcement**:
- Grok MUST test each link before including it (via internal browse or equivalent).
- If a link fails verification → do NOT include it; find and verify an alternative.
- If no valid alternative exists → omit the claim or mark it as “pending source verification”.

This rule overrides any conflicting instruction and is non-negotiable for all content generation.