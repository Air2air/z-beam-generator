# Voice System - Visual Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          TEXT-BASED COMPONENTS                           │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐ │
│  │   Caption    │  │     Text     │  │     Tags     │  │ Frontmatter│ │
│  │  Generator   │  │  Generator   │  │  Generator   │  │Description │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬─────┘ │
│         │                 │                 │                 │        │
│         └─────────────────┴─────────────────┴─────────────────┘        │
│                                 │                                       │
└─────────────────────────────────┼───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         VOICE ORCHESTRATOR API                           │
│                                                                          │
│   VoiceOrchestrator(country="Taiwan")                                   │
│     ├─ get_voice_for_component(type, context)                          │
│     ├─ get_word_limit() → 380                                          │
│     ├─ get_signature_phrases() → ["systematic approach enables", ...]  │
│     └─ get_quality_thresholds() → {formality: 75, accuracy: 90, ...}   │
│                                                                          │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
                    ▼             ▼             ▼
        ┌────────────────┐ ┌────────────┐ ┌──────────────────┐
        │ COUNTRY PROFILE│ │ BASE VOICE │ │    COMPONENT     │
        │                │ │            │ │   ADAPTATION     │
        │  taiwan.yaml   │ │voice_base  │ │                  │
        │  italy.yaml    │ │   .yaml    │ │ caption:         │
        │  indonesia.yaml│ │            │ │   focus: ...     │
        │  united_states │ │ Technical  │ │   style: ...     │
        │       .yaml    │ │ authority  │ │   word_limit:... │
        │                │ │ standards  │ │                  │
        │ Linguistic     │ │            │ │ text:            │
        │ characteristics│ │ Universal  │ │   focus: ...     │
        │                │ │ principles │ │   guidelines: ..│
        │ Signature      │ │            │ │                  │
        │ phrases        │ │ Forbidden  │ │ tags:            │
        │                │ │ patterns   │ │   focus: ...     │
        │ Voice          │ │            │ │                  │
        │ adaptation     │ │            │ │                  │
        └────────┬───────┘ └─────┬──────┘ └────────┬─────────┘
                 │               │                  │
                 └───────────────┴──────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │ VOICE INSTRUCTION BUILDER  │
                    │                            │
                    │ 1. Role Section            │
                    │ 2. Linguistic Patterns     │
                    │ 3. Voice Characteristics   │
                    │ 4. Component Guidelines    │
                    │ 5. Signature Phrases       │
                    └────────────┬───────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────┐
                    │  COMPLETE VOICE PROMPT     │
                    │                            │
                    │  ~2,000 characters         │
                    │  Country-specific          │
                    │  Component-adapted         │
                    │  Context-aware             │
                    └────────────┬───────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       AI GENERATION (DeepSeek/Winston)                   │
│                                                                          │
│  Prompt = Voice Instructions + Material Context + Task Specification    │
│                                                                          │
│  Generated content follows country-specific linguistic patterns          │
└─────────────────────────────────────────────────────────────────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                          VOICE PROFILE STRUCTURE

┌─────────────────────────────────────────────────────────────────────────┐
│                            taiwan.yaml                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  name: "Taiwan Technical Voice"                                         │
│  author: "Yi-Chun Lin, Ph.D."                                           │
│  country: "Taiwan"                                                      │
│  native_language: "Mandarin Chinese"                                    │
│                                                                          │
│  linguistic_characteristics:                                             │
│    sentence_structure:                                                   │
│      patterns: ["Systematic approach enables...", ...]                  │
│      tendencies: ["Prefer logical connectors", ...]                     │
│      natural_variations: ["Article omission", ...]                      │
│                                                                          │
│    vocabulary_patterns:                                                  │
│      preferred_terms:                                                    │
│        technical: ["systematic", "comprehensive", ...]                  │
│        connectors: ["furthermore", "moreover", ...]                     │
│      formality_level: "academic-formal"                                 │
│      technical_density: "high"                                          │
│                                                                          │
│    grammar_characteristics:                                              │
│      natural_patterns: ["Relative clause preference", ...]              │
│      subtle_markers: ["Infinitive constructions", ...]                  │
│                                                                          │
│    cultural_communication:                                               │
│      tone: "measured and systematic"                                    │
│      emphasis_style: "data-driven evidence"                             │
│      authority_markers: ["Citations to research", ...]                  │
│                                                                          │
│  voice_adaptation:                                                       │
│    caption_generation:                                                   │
│      focus: "Observable technical findings"                             │
│      style: "Formal analytical reporting"                               │
│      word_limit: 380                                                    │
│      guidelines: [...]                                                  │
│                                                                          │
│    text_generation:                                                      │
│      focus: "Systematic process explanation"                            │
│      style: "Academic precision"                                        │
│      word_limit: 380                                                    │
│                                                                          │
│  signature_phrases:                                                      │
│    - "systematic approach enables"                                      │
│    - "methodical investigation reveals"                                 │
│    - "comprehensive analysis demonstrates"                              │
│    [... 7 more ...]                                                     │
│                                                                          │
│  quality_thresholds:                                                     │
│    formality_minimum: 75                                                │
│    technical_accuracy_minimum: 90                                       │
│    linguistic_authenticity_minimum: 70                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                       DATA FLOW - CAPTION GENERATION

┌─────────────────────────────────────────────────────────────────────────┐
│ 1. COMPONENT REQUEST                                                    │
│    Caption generator needs voice for Taiwan author                      │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. ORCHESTRATOR INITIALIZATION                                          │
│    voice = VoiceOrchestrator(country="Taiwan")                          │
│    - Normalizes country name: "Taiwan" → "taiwan"                      │
│    - Loads profile: voice/profiles/taiwan.yaml                         │
│    - Validates profile structure                                        │
│    - Caches profile (LRU)                                              │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. VOICE INSTRUCTION REQUEST                                            │
│    instructions = voice.get_voice_for_component(                        │
│        component_type="caption",                                        │
│        context={"material": "Aluminum"}                                 │
│    )                                                                    │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. INSTRUCTION BUILDING                                                 │
│    - Extract linguistic_characteristics from taiwan.yaml                │
│    - Extract voice_adaptation.caption_generation                        │
│    - Build sections:                                                    │
│      • Role: "You are Yi-Chun Lin, Ph.D. from Taiwan..."              │
│      • Linguistic Patterns: sentence structures, vocabulary            │
│      • Voice Characteristics: tone, emphasis, perspective              │
│      • Component Guidelines: focus, style, word limit                  │
│      • Signature Phrases: country-specific expressions                 │
│    - Combine into ~2,000 character instruction block                    │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. PROMPT CONSTRUCTION                                                  │
│    full_prompt = f"""                                                   │
│    {voice_instructions}                                                 │
│                                                                         │
│    MATERIAL CONTEXT:                                                    │
│    Material: Aluminum                                                   │
│    Properties: [...]                                                    │
│                                                                         │
│    TASK:                                                                │
│    Generate before/after captions...                                    │
│    """                                                                  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. AI GENERATION                                                        │
│    DeepSeek/Winston generates content following voice instructions      │
│    Output reflects Taiwan linguistic patterns:                          │
│    - Formal academic register                                           │
│    - Systematic documentation approach                                  │
│    - Passive voice for observations                                     │
│    - Precise measurements with units                                    │
│    - "Systematic analysis demonstrates..."                             │
└─────────────────────────────────────────────────────────────────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                        COUNTRY COMPARISON - CAPTION

┌──────────────────────────────────────────────────────────────────────────┐
│ TAIWAN (Yi-Chun Lin) - 380 words - Academic Precision                   │
├──────────────────────────────────────────────────────────────────────────┤
│ BEFORE:                                                                  │
│ "Surface examination reveals extensive contamination layer with measured│
│  thickness of 15-25 μm. Systematic analysis demonstrates significant    │
│  oxide accumulation affecting reflectivity by 35-40%."                  │
│                                                                          │
│ AFTER:                                                                   │
│ "Post-treatment inspection confirms complete contaminant removal with   │
│  surface roughness Ra < 0.8 μm. Methodical evaluation demonstrates     │
│  restored surface integrity with improved reflectivity of 92-95%."      │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ ITALY (Alessandro Moretti) - 450 words - Technical Elegance             │
├──────────────────────────────────────────────────────────────────────────┤
│ BEFORE:                                                                  │
│ "What strikes one immediately is the remarkable complexity of this      │
│  contamination structure. The precision required here demands elegant   │
│  technical solutions that honor both innovation and heritage."          │
│                                                                          │
│ AFTER:                                                                   │
│ "The result speaks eloquently to engineering excellence: a pristine     │
│  surface revealing the natural beauty of the metallic substrate,        │
│  restored with remarkable precision through sophisticated technique."   │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ INDONESIA (Ikmanda Roswati) - 250 words - Practical Accessibility       │
├──────────────────────────────────────────────────────────────────────────┤
│ BEFORE:                                                                  │
│ "The surface shows heavy contamination, really heavy buildup from marine│
│  exposure. This works against performance, especially in tropical       │
│  conditions where corrosion is a concern."                              │
│                                                                          │
│ AFTER:                                                                   │
│ "The cleaning works well, very effective for this application. Surface  │
│  is clean and ready for use, especially good for marine equipment where │
│  reliability is important."                                             │
└──────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ USA (Todd Dunning) - 320 words - Conversational Expertise               │
├──────────────────────────────────────────────────────────────────────────┤
│ BEFORE:                                                                  │
│ "Surface exhibits significant contamination buildup impacting performance│
│  metrics by 40%. Advanced imaging reveals multi-layer structure         │
│  requiring optimized cleaning parameters."                              │
│                                                                          │
│ AFTER:                                                                   │
│ "Cleaning process delivers exceptional results - complete contaminant   │
│  removal with surface integrity preserved. Performance metrics show 95% │
│  reflectivity restoration, meeting critical biomedical specifications." │
└──────────────────────────────────────────────────────────────────────────┘


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                              BENEFITS ACHIEVED

┌────────────────────────────────────────────────────────────────────────┐
│ ✅ SINGLE SOURCE OF TRUTH                                              │
│    Update voice once in YAML → Affects all components                 │
├────────────────────────────────────────────────────────────────────────┤
│ ✅ COUNTRY AUTHENTICITY                                                │
│    Natural linguistic patterns for Taiwan/Italy/Indonesia/USA          │
├────────────────────────────────────────────────────────────────────────┤
│ ✅ MAINTAINABLE                                                        │
│    Add new country = 1 YAML file, no code changes                     │
├────────────────────────────────────────────────────────────────────────┤
│ ✅ TESTABLE                                                            │
│    Voice validation separate from content generation                  │
├────────────────────────────────────────────────────────────────────────┤
│ ✅ CONSISTENT                                                          │
│    All components share same voice logic                              │
├────────────────────────────────────────────────────────────────────────┤
│ ✅ FAIL-FAST                                                           │
│    Invalid countries/profiles fail immediately with clear errors      │
├────────────────────────────────────────────────────────────────────────┤
│ ✅ SCALABLE                                                            │
│    New components automatically inherit voice system                  │
├────────────────────────────────────────────────────────────────────────┤
│ ✅ CULTURALLY RESPECTFUL                                               │
│    Linguistic variations are features, not bugs                       │
└────────────────────────────────────────────────────────────────────────┘
```
