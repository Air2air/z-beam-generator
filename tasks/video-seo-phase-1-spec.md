# Video SEO Phase 1 Spec

Date: 2026-03-25
Scope: frontend-only improvements in `z-beam`
Objective: improve video SEO richness without widening into provider migration, transcript systems, or generator-side content production

## Success Criteria

- Every video watch page emits a richer `VideoObject` than the current baseline.
- Watch-page metadata is internally consistent for video pages across title, description, canonical, Open Graph, and Twitter/video tags.
- The video sitemap remains valid and gains any low-risk enrichments that are already available from current data.
- Video enhancement copy quality improves for sparse or promotional source descriptions.
- The Phase 1 changes stay frontend-only and do not require changes to generator runtime or YouTube provider architecture.

## In Scope

1. Richer watch-page `VideoObject` and page-level metadata
2. Video-specific metadata cleanup for watch pages and the `/videos` hub
3. Enhancement-copy quality improvements where current summaries are generic or promotional
4. Relationship-population pass guidance for the current website-side video overlays

## Out Of Scope

- YouTube Data API migration
- Transcript or caption ingestion systems
- Key-moment or clip extraction pipelines
- Generator-side prompt/pipeline changes
- Broad redesign of the `/videos` hub UI

## Workstream 1: Richer VideoObject Schema

### Files

- `z-beam/app/utils/schemas/generators/video.ts`
- `z-beam/app/utils/schemas/videoSchemas.ts`
- `z-beam/app/videos/[slug]/page.tsx`
- `z-beam/app/video-sitemap.xml/route.ts`

### Current Gap

The watch pages expose a valid but thin `VideoObject` with `name`, `description`, `url`, `sameAs`, `embedUrl`, `thumbnailUrl`, `uploadDate`, keywords, subject, publisher, and watch action. The homepage video schema is richer than the dedicated watch pages because it already carries fields such as `contentUrl` and `duration`.

### Deliverables

1. Add richer low-risk `VideoObject` fields where current data already exists or can be safely derived.
2. Prefer the watch page as the canonical `url` and keep YouTube as `sameAs`.
3. Add `contentUrl` when the current data contract supports a stable source URL.
4. Add `duration` only if it can be reliably populated from existing authored or source data; otherwise leave it out in Phase 1.
5. Ensure `mainEntityOfPage`, `publisher`, `about`, and `potentialAction` remain coherent.
6. Consider a light `description` split between watch-page lead copy and shorter summary if the schema currently feels too repetitive.

### Acceptance Criteria

- `buildVideoWatchSchema()` emits a richer `VideoObject` than it does today.
- No schema validator regressions are introduced.
- The watch page remains canonical over the external YouTube URL.

## Workstream 2: Video-Native Metadata Cleanup

### Files

- `z-beam/app/utils/metadata.ts`
- `z-beam/app/videos/[slug]/page.tsx`
- `z-beam/app/videos/page.tsx`

### Current Gap

The shared metadata helper still treats most pages as `article` or `website`, and the Twitter card strategy is mixed: `summary_large_image` is emitted alongside `twitter:player` tags. The watch pages already pass video metadata to the helper, but the helper itself is not consistently video-native.

### Deliverables

1. Define the intended social metadata contract for video watch pages.
2. Decide whether video watch pages should emit a player-oriented Twitter contract or stay image-card-only, then make the implementation consistent.
3. Review whether watch pages should remain `article` in Open Graph or use a simpler `website` contract with stronger `other` video tags in Phase 1.
4. Keep hub-page metadata simpler than watch-page metadata.

### Acceptance Criteria

- Watch-page metadata is internally consistent across OG, Twitter, and custom video meta tags.
- `/videos` hub metadata stays clean and does not pretend to be a watch page.
- No duplicate or contradictory video-social signals remain.

## Workstream 3: Enhancement Copy Quality Pass

### Files

- `z-beam/app/utils/videoEnhancements.ts`
- `z-beam/app/utils/videoNormalization.ts`
- representative overlays in `z-beam/frontmatter/videos/*.yaml`

### Current Gap

Some video summaries are still generic fallback copy, and at least one summary remains too promotional for strong SEO/snippet quality. The current enhancement pipeline is solid enough to improve without changing the discovery architecture.

### Deliverables

1. Tighten promotional filtering in `buildVideoSummary()`.
2. Prefer substrate/process/outcome language when source descriptions are usable.
3. Keep sparse-source fallbacks stable, but reduce repetitive generic phrasing when higher-quality detail exists.
4. Refresh current video overlays after the helper changes.

### Acceptance Criteria

- Current live summaries are descriptive and non-promotional.
- Sparse scrape-only videos still have stable fallbacks.
- Existing frontmatter contract tests remain green.

## Workstream 4: Relationship Population Guidance

### Files

- `z-beam/frontmatter/videos/*.yaml`
- `z-beam/app/utils/videoFrontmatter.ts`
- `z-beam/app/utils/videoCatalog.ts`

### Current Gap

Many overlays still ship with empty `related_materials`, `related_contaminants`, `related_compounds`, and `related_applications` sections, which limits internal-linking and entity depth.

### Deliverables

1. Audit the current 18 overlays and identify the videos with obvious high-confidence relationships.
2. Prioritize `related_materials` and `related_applications` first.
3. Add only editorially confident relationships in Phase 1.
4. Leave weak or speculative contaminant/compound links out rather than diluting quality.

### Acceptance Criteria

- Most videos have at least one meaningful related entity.
- Relationship sections improve topical depth without introducing weak matches.
- Watch pages visibly become more connected to the rest of the site.

## Recommended Execution Order

1. `VideoObject` enrichment
2. metadata/social cleanup
3. enhancement-copy quality pass
4. overlay relationship population
5. rerun focused tests
6. rerun `npm run prebuild:deploy`
7. rerun `npm run prebuild` if the change set grows large

## Validation Commands

Run in `z-beam`:

```bash
npx jest tests/pages/video-watch-page.test.tsx tests/app/videos-page.test.tsx tests/seo/video-sitemap.test.ts tests/seo/youtube-feed.test.ts tests/frontmatter/videoFrontmatter.contract.test.ts tests/utils/videoEnhancements.test.ts tests/utils/videoNormalization.test.ts --runInBand
```

Then:

```bash
npm run videos:sync-frontmatter -- --refresh-derived-metadata --refresh-enhancements
```

Then:

```bash
npm run prebuild:deploy
```

If the metadata/schema surface changes materially:

```bash
npm run prebuild
```

## Implementation Notes

- Keep the provider boundary in `app/utils/youtubeVideoSource.ts` unchanged in Phase 1.
- Do not widen scope into transcript extraction or API-provider changes.
- Prefer authored relationship population over aggressive derived matching.
- Prefer improvements that raise the quality of the current 18 live pages immediately.