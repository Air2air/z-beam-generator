# Simplified Architecture - Visual Reference

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Z-BEAM GENERATOR ARCHITECTURE                         │
│                      6 Components + Enhanced Prompting                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           MATERIALS.YAML                                     │
│                    (Single Source of Truth)                                  │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             │ orchestrates
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FRONTMATTER COMPONENT                                     │
│                   (Orchestrator + Enhanced Prompting)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  streamlined_generator.py                                                    │
│  ├─ Load Materials.yaml data                                                │
│  ├─ Call specialized prompt builders:                                       │
│  │  ├─ IndustryApplicationsPromptBuilder                                    │
│  │  │   └─ Phase 1: Research (validation criteria)                          │
│  │  │   └─ Phase 2: Generation (50-80 word descriptions)                    │
│  │  │   └─ Quality Gate: 5-8 industries, 70%+ confidence                    │
│  │  ├─ RegulatoryStandardsPromptBuilder                                     │
│  │  │   └─ Research FDA/ANSI/ISO/OSHA/IEC/EPA                               │
│  │  │   └─ longName + applicability + requirements                          │
│  │  └─ EnvironmentalImpactPromptBuilder                                     │
│  │      └─ Quantified comparisons (chemical, water, VOC, energy)            │
│  ├─ Validate quality thresholds (fail-fast)                                 │
│  ├─ Merge results into unified frontmatter                                  │
│  └─ Save to Materials.yaml                                                  │
└────────────────────────────┬────────────────────────────────────────────────┘
                             │
                             │ exports
                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TRIVIAL EXPORTER                                        │
│              (frontmatter/*.yaml for Next.js)                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                    DISCRETE COMPONENTS                                       │
│                  (Self-Contained with Voice Integration)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│  │   CAPTION COMPONENT          │  │   SUBTITLE COMPONENT         │        │
│  ├──────────────────────────────┤  ├──────────────────────────────┤        │
│  │ Pattern: Dual Voice          │  │ Pattern: Single Voice        │        │
│  │ Calls: 2 (before/after)      │  │ Calls: 1                     │        │
│  │ Words: 20-100 per section    │  │ Words: 8-12 total            │        │
│  │                              │  │                              │        │
│  │ Structure:                   │  │ Structure:                   │        │
│  │ ├─ generators/               │  │ ├─ core/                     │        │
│  │ │  └─ generator.py           │  │ │  └─ subtitle_generator.py │        │
│  │ ├─ config/                   │  │ ├─ prompts/                  │        │
│  │ └─ ARCHITECTURE.md           │  │ ├─ config/                   │        │
│  │                              │  │ └─ ARCHITECTURE.md           │        │
│  │ Uses: VoiceOrchestrator      │  │ Uses: VoiceOrchestrator      │        │
│  │ (reusable service)           │  │ (reusable service)           │        │
│  └──────────────────────────────┘  └──────────────────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     STATIC COMPONENTS                                        │
│                  (Data Export - Depend on Frontmatter)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  • author/            - Author information                                   │
│  • badgesymbol/       - Material symbol badges                               │
│  • metatags/          - HTML meta tags                                       │
│  • jsonld/            - JSON-LD structured data                              │
│  • propertiestable/   - Technical properties table                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                     REUSABLE SERVICES                                        │
│               (Shared Across Components - Not Duplicated)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  • VoiceOrchestrator     - Country-specific author voice (caption/subtitle)  │
│  • PropertyManager       - Property extraction and management                │
│  • ValidationOrchestrator - Confidence normalization and validation          │
│  • TemplateService       - Reusable content templates                        │
│  • APIClientFactory      - API client management with caching                │
└─────────────────────────────────────────────────────────────────────────────┘

═════════════════════════════════════════════════════════════════════════════
                              KEY PRINCIPLES
═════════════════════════════════════════════════════════════════════════════

1. 6-Component Consolidation
   └─ Reduced from 11 components for maintainability

2. Enhanced Prompting (Not New Components)
   └─ Specialized prompt builders in frontmatter/prompts/

3. Discrete Component Pattern
   └─ Caption and Subtitle self-contained with core/, prompts/, config/

4. Materials.yaml Orchestration
   └─ Single source of truth, all data flows through it

5. Fail-Fast Architecture
   └─ Quality gates, no mocks/fallbacks, explicit validation

6. Separation of Concerns
   └─ Reusable services (Voice, Property) separate from component logic

═════════════════════════════════════════════════════════════════════════════
                          ENHANCED PROMPTING FLOW
═════════════════════════════════════════════════════════════════════════════

Industry Applications (2-Phase):
  1. Research Prompt → API → Validate (5-8 industries, confidence scoring)
  2. Generation Prompt → API → Parse (50-80 words, evidence-based)
  └─ Quality Gate: 70%+ confidence, specific products, standards citations

Regulatory Standards:
  1. Research Prompt → API → Validate (FDA/ANSI/ISO/OSHA/IEC/EPA)
  └─ Quality Gate: Direct applicability, longName required

Environmental Impact:
  1. Research Prompt → API → Validate (quantified metrics)
  └─ Quality Gate: Chemical/water/VOC/energy comparisons with evidence

═════════════════════════════════════════════════════════════════════════════
                           COMPONENT COUNTS
═════════════════════════════════════════════════════════════════════════════

BEFORE: 11 components (overcomplicated)
AFTER:  6 components (streamlined)

Orchestrator:     1 (frontmatter)
Discrete:         2 (caption, subtitle)
Static:           5 (author, badgesymbol, metatags, jsonld, propertiestable)
────────────────────
TOTAL:            6 active components

Prompt Builders:  3 (industry, regulatory, environmental)
                  └─ Part of frontmatter, NOT separate components

═════════════════════════════════════════════════════════════════════════════
