# Grok Pipeline 2 Policies

## Objective
- Prefer direct frontmatter generation and review from canonical repository assets rather than CLI-first workflows.

## Canonical Read Order
1. `governance/`
2. `aggregates/`
3. `domains/`
4. `prompts/`
5. `voices/`
6. `frontmatter-templates/`
7. `schemas/pipeline_2_policy.yaml`

## Compatibility Rules
- Treat `run.py`, `.github/`, `docs/`, `data/`, and `shared/voice/profiles/` as compatibility surfaces that must keep working.
- When a canonical file and a compatibility file disagree, update both in the same change or stop and resolve the drift.

## Pipeline 2 Working Rules
- Use aggregate source YAML hubs in `aggregates/` as the primary research context for direct generation.
- Use templates in `frontmatter-templates/` as shape guides for Grok-authored output.
- Use `voices/*.yaml` for author voice guidance; legacy runtime mirrors remain in `shared/voice/profiles/`.
- Use `outputs/` only for preview artifacts and draft frontmatter that is not yet promoted into source or production frontmatter.

## Manifest Parity Rules
- Treat `governance/grok_github_manifest_minimum.md` as the canonical in-repo mirror of the external Grok gist.
- Keep the in-repo manifest and the external gist aligned in section order and path listings.
- If the gist cannot be updated in the same session, update the in-repo manifest first and record the remaining parity gap explicitly.

## Grok Quality And Validation Role
- Grok-backed evaluation remains embedded in the six-pass workflow described by repository docs: pass 2 quality scoring, pass 3 gate enforcement, pass 4 learning adjustment inputs, and pass 6 regeneration decisions.
- Preserve fail-fast behavior for Grok-dependent validation. Missing required Grok services or contracts must stop the affected workflow instead of degrading to mock or fallback scoring.
- Where composite quality weighting is used, preserve the published contract: Grok humanness 60%, subjective quality 30%, readability 10%.

## Fail-Fast Requirements
- Do not invent missing schema fields; validate against repo schemas first.
- Do not patch production frontmatter directly when the source YAML or export contract is the actual source of truth.
- Do not remove legacy compatibility paths until all references and automation are migrated.