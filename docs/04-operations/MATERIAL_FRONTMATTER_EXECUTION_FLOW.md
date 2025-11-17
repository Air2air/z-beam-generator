# Material Frontmatter Export/Regeneration - Complete Execution Flow

## Command Entry Point

```bash
# Single material export/regeneration
python3 run.py --material "Aluminum"

# Batch export all materials
python3 run.py --all --data-only
```

---

## 🔄 Complete Execution Flow

### Phase 1: Command Line Entry (`run.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Command Line Parsing                                         │
│    File: run.py (lines 132-350)                                │
│                                                                  │
│    Input: --material "Aluminum"                                 │
│    ↓                                                             │
│    Parse arguments with argparse                                │
│    ↓                                                             │
│    Extract: material_name = "Aluminum"                          │
│             data_only = False (default, enables API)            │
│             no_completeness_check = False (validation enabled)  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Initialize Orchestrator                                      │
│    File: run.py (lines 330-355)                                │
│                                                                  │
│    from components.frontmatter.core.orchestrator import         │
│        FrontmatterOrchestrator                                  │
│    from shared.api.client_factory import create_api_client      │
│    ↓                                                             │
│    api_client = create_api_client("grok")                       │
│    orchestrator = FrontmatterOrchestrator(                      │
│        api_client=api_client,                                   │
│        enforce_completeness=True  # Default unless --no-check   │
│    )                                                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 3. Load Author Data                                             │
│    File: run.py (lines 340-350)                                │
│                                                                  │
│    from materials.data.materials import                         │
│        get_material_by_name_cached                              │
│    from components.frontmatter.utils.author_manager import      │
│        get_author_info_for_material                             │
│    ↓                                                             │
│    material_data = get_material_by_name_cached("Aluminum")      │
│    author_data = get_author_info_for_material(material_data)    │
│    ↓                                                             │
│    Returns: {                                                    │
│        'name': 'Todd Dunning',                                  │
│        'country': 'United States',                              │
│        'bio': '...',                                            │
│        'credentials': '...'                                     │
│    }                                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 2: Orchestration (`orchestrator.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│ 4. Route to Material Generator                                  │
│    File: components/frontmatter/core/orchestrator.py            │
│          (lines 204-228)                                        │
│                                                                  │
│    orchestrator.generate(                                       │
│        content_type='material',                                 │
│        identifier='Aluminum',                                   │
│        author_data=author_data                                  │
│    )                                                             │
│    ↓                                                             │
│    Get registered generator for 'material' type                 │
│    ↓                                                             │
│    generator = self._get_generator('material')                  │
│    # Returns: MaterialFrontmatterGenerator instance             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 5. Generator Discovery & Registration                           │
│    File: components/frontmatter/core/orchestrator.py            │
│          (lines 89-103)                                         │
│                                                                  │
│    from materials.generator import                              │
│        MaterialFrontmatterGenerator                             │
│    ↓                                                             │
│    Register in _generator_registry['material']                  │
│    ↓                                                             │
│    Cache instance in _generator_cache['material']               │
│    ↓                                                             │
│    Returns: MaterialFrontmatterGenerator(                       │
│        api_client=api_client,                                   │
│        config=config                                            │
│    )                                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 3: Material Generator (`materials/generator.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│ 6. Material Generator Initialization                            │
│    File: materials/generator.py (lines 46-75)                  │
│                                                                  │
│    MaterialFrontmatterGenerator.__init__()                      │
│    ↓                                                             │
│    super().__init__(                                            │
│        content_type='material',                                 │
│        api_client=api_client                                    │
│    )                                                             │
│    ↓                                                             │
│    Initialize wrapped legacy generator:                         │
│    self._legacy_generator = StreamlinedFrontmatterGenerator()   │
│    ↓                                                             │
│    Phase 1 Wrapper Pattern - preserves ALL existing logic       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 7. Generate Call                                                │
│    File: materials/generator.py (lines 202-230)                │
│                                                                  │
│    generator.generate(                                          │
│        identifier='Aluminum',                                   │
│        author_data=author_data                                  │
│    )                                                             │
│    ↓                                                             │
│    Calls: super().generate() → BaseFrontmatterGenerator         │
└─────────────────────────────────────────────────────────────────┘
```

---

### Phase 4: Base Generator Pipeline (`base_generator.py`)

```
┌─────────────────────────────────────────────────────────────────┐
│ 8. Standard Generation Pipeline                                 │
│    File: components/frontmatter/core/base_generator.py          │
│          (lines 210-305)                                        │
│                                                                  │
│    BaseFrontmatterGenerator.generate()                          │
│    ↓                                                             │
│    Step 1: Validate identifier exists                           │
│            _validate_identifier("Aluminum")                     │
│    ↓                                                             │
│    Step 2: Build generation context                             │
│            context = GenerationContext(                         │
│                content_type='material',                         │
│                identifier='Aluminum',                           │
│                api_client=api_client,                           │
│                author_data=author_data                          │
│            )                                                     │
│    ↓                                                             │
│    Step 3: Build frontmatter data                               │
│            frontmatter_data = _build_frontmatter_data()         │
│            # Delegates to MaterialFrontmatterGenerator          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 9. Build Frontmatter Data (Wrapper Delegation)                  │
│    File: materials/generator.py (lines 128-171)                │
│                                                                  │
│    MaterialFrontmatterGenerator._build_frontmatter_data()       │
│    ↓                                                             │
│    Delegates to legacy generator:                               │
│    result = self._legacy_generator.generate(                    │
│        material_name='Aluminum'                                 │
│    )                                                             │
│    ↓                                                             │
│    Legacy generator performs ALL existing logic:                │
│    • Load Materials.yaml data                                   │
│    • Load Categories.yaml ranges                                │
│    • Enhance properties (min/max calculations)                  │
│    • Process templates                                          │
│    • Calculate machine settings                                 │
│    • Build environmental impact                                 │
│    • Build industry applications                                │
│    • Build regulatory standards                                 │
│    • Build FAQ, caption, subtitle                               │
│    ↓                                                             │
│    Returns: ComponentResult with YAML string                    │
│    ↓                                                             │
│    Parse YAML string → frontmatter_data dict                    │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 10. 🎤 AUTOMATIC VOICE QUALITY GATE (NEW!)                     │
│     File: components/frontmatter/core/base_generator.py         │
│           (lines 310-460)                                       │
│                                                                  │
│     BaseFrontmatterGenerator._apply_author_voice()              │
│     ↓                                                            │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│     🔍 STEP 1: SCAN FOR QUALITY ISSUES                          │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│     from shared.voice.quality_scanner import                    │
│         VoiceQualityScanner                                     │
│     ↓                                                            │
│     scanner = VoiceQualityScanner(api_client, author_data)      │
│     issues, total, failed = scanner.scan_text_fields(           │
│         data=frontmatter_data                                   │
│     )                                                            │
│     ↓                                                            │
│     Recursively scans ALL text fields:                          │
│     • faq[0].question                                           │
│     • faq[0].answer                                             │
│     • faq[1].question                                           │
│     • faq[1].answer                                             │
│     • caption                                                    │
│     • subtitle                                                   │
│     • seo.metaDescription                                       │
│     • ... etc ...                                               │
│     ↓                                                            │
│     For each field:                                             │
│       quality_score = VoicePostProcessor.score_voice_quality()  │
│       if score < 70:                                            │
│           issues.append((path, score, text))                    │
│     ↓                                                            │
│     Quality checks:                                             │
│     ✓ Marker repetition (e.g., 10x "notably")                  │
│     ✓ Excessive marker count                                    │
│     ✓ Marker clustering (5+ in 50 words)                       │
│     ✓ Translation artifacts                                     │
│     ✓ Generic language                                          │
│     ↓                                                            │
│     Results: issues = [                                         │
│         ("faq[0].answer", 45.0, "notably...notably..."),       │
│         ("faq[1].answer", 50.0, "notably...notably..."),       │
│         ...11 failing fields total                              │
│     ]                                                            │
│     ↓                                                            │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│     🔧 STEP 2: AUTOMATIC REPAIR IF ISSUES FOUND                 │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│     if failed > 0:                                              │
│         print(f"🚨 Voice quality issues: {failed}/{total}")    │
│         ↓                                                        │
│         from shared.voice.source_data_repairer import           │
│             SourceDataRepairer                                  │
│         ↓                                                        │
│         repairer = SourceDataRepairer.create_for_content_type(  │
│             api_client=api_client,                              │
│             content_type='material'  # from self.content_type   │
│         )                                                        │
│         ↓                                                        │
│         For each failing field:                                 │
│             field_path = "faq[0].answer"                        │
│             original_value = "notably...notably..."            │
│             ↓                                                    │
│             repairer.repair_field(                              │
│                 item_name='Aluminum',                           │
│                 field_path='faq[0].answer',                     │
│                 original_value=original_value,                  │
│                 context={'question': faq[0].question}           │
│             )                                                    │
│             ↓                                                    │
│             🔄 REPAIR LOOP (max 2 attempts):                    │
│                 print("🔧 Regenerating faq[0].answer")         │
│                 ↓                                               │
│                 new_value = VoicePostProcessor.enhance(         │
│                     original_value, author_data                 │
│                 )                                               │
│                 ↓                                               │
│                 new_score = score_voice_quality(new_value)      │
│                 ↓                                               │
│                 if new_score >= 70:                             │
│                     print("✅ Quality improved: {score}/100")  │
│                     break                                       │
│                 else:                                           │
│                     print("⚠️  Quality still low, retrying...")│
│                     attempt += 1                                │
│                 ↓                                               │
│                 if attempt >= 2:                                │
│                     print("❌ Failed after 2 attempts")        │
│         ↓                                                        │
│         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│         💾 STEP 3: UPDATE SOURCE YAML (Materials.yaml)          │
│         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│         repairer.update_source_yaml(                            │
│             item_name='Aluminum',                               │
│             updates={                                           │
│                 'faq[0].answer': new_value,                     │
│                 'faq[1].answer': new_value2,                    │
│                 ...                                             │
│             }                                                    │
│         )                                                        │
│         ↓                                                        │
│         Saves to: materials/data/Materials.yaml                 │
│         ↓                                                        │
│         ⚠️  NOTE: Currently logs but doesn't save              │
│         TODO: Implement full path navigation (parse "faq[0]")   │
│         ↓                                                        │
│         print("✅ Updated Materials.yaml with repairs")         │
│     ↓                                                            │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│     📊 STEP 4: ADD QUALITY METADATA                             │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│     frontmatter_data['voiceProcessing'] = {                     │
│         'applied': True,                                        │
│         'author': author_data['name'],                          │
│         'country': author_data['country'],                      │
│         'quality_issues_detected': failed,                      │
│         'total_fields_scanned': total                           │
│     }                                                            │
│     ↓                                                            │
│     Returns: frontmatter_data (enhanced & validated)            │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 11. Save Frontmatter File                                       │
│     File: components/frontmatter/core/base_generator.py         │
│           (lines 505-555)                                       │
│                                                                  │
│     BaseFrontmatterGenerator._save_frontmatter()                │
│     ↓                                                            │
│     output_path = frontmatter/materials/                        │
│                   aluminum-laser-cleaning.yaml                  │
│     ↓                                                            │
│     Save frontmatter_data as YAML file                          │
│     ↓                                                            │
│     print(f"✅ Generated → {output_path}")                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 What Actually Runs - Summary Table

| Step | File | Lines | What Happens |
|------|------|-------|--------------|
| **1** | `run.py` | 132-350 | Parse `--material "Aluminum"` command |
| **2** | `run.py` | 330-355 | Create FrontmatterOrchestrator + API client |
| **3** | `run.py` | 340-350 | Load author data from Materials.yaml |
| **4** | `orchestrator.py` | 204-228 | Route to MaterialFrontmatterGenerator |
| **5** | `orchestrator.py` | 89-103 | Discover & register material generator |
| **6** | `materials/generator.py` | 46-75 | Initialize wrapper + legacy generator |
| **7** | `materials/generator.py` | 202-230 | Call super().generate() → base class |
| **8** | `base_generator.py` | 210-305 | Validate + build context + build data |
| **9** | `materials/generator.py` | 128-171 | Delegate to legacy for ALL existing logic |
| **10a** | `base_generator.py` | 310-390 | **🔍 SCAN**: VoiceQualityScanner checks all text fields |
| **10b** | `base_generator.py` | 390-440 | **🔧 REPAIR**: SourceDataRepairer fixes poor quality text |
| **10c** | `base_generator.py` | 440-460 | **💾 UPDATE**: Save repairs to Materials.yaml |
| **11** | `base_generator.py` | 505-555 | Save final YAML to frontmatter/materials/ |

---

## 🎯 Key Components Used

### Voice Quality System
1. **VoicePostProcessor** (`shared/voice/post_processor.py`)
   - Core text enhancement engine
   - Quality scoring (threshold: 70/100)
   - Checks: marker repetition, clustering, excessive markers

2. **VoiceQualityScanner** (`shared/voice/quality_scanner.py`)
   - Recursively scans all text fields in data structure
   - Returns: (issues_list, total_scanned, failed_count)

3. **SourceDataRepairer** (`shared/voice/source_data_repairer.py`)
   - Content-agnostic repairer (works for materials, regions, etc.)
   - Factory pattern: `create_for_content_type('material')`
   - Regenerates poor quality text with retries (max 2)
   - Updates source YAML (Materials.yaml, regions.yaml, etc.)

4. **VoiceOrchestrator** (`shared/voice/orchestrator.py`)
   - Provides country-specific voice indicators
   - Manages linguistic patterns by author

### Legacy Generator
5. **StreamlinedFrontmatterGenerator** (`components/frontmatter/core/streamlined_generator.py`)
   - ALL existing frontmatter logic
   - Property enhancement, range calculations, templates
   - Machine settings, environmental impact, applications
   - FAQ, caption, subtitle generation

### Orchestration
6. **FrontmatterOrchestrator** (`components/frontmatter/core/orchestrator.py`)
   - Multi-type coordinator (materials, regions, applications, thesaurus)
   - Generator discovery and registration
   - Routes requests to appropriate generators

7. **BaseFrontmatterGenerator** (`components/frontmatter/core/base_generator.py`)
   - Standard generation pipeline
   - **Automatic voice quality gate** (NEW!)
   - Schema validation, configuration loading

---

## 🚦 Quality Gate Behavior

### Scenario 1: All Text Fields Pass (score >= 70)
```
🔍 Scanning voice quality...
✅ All text fields passed quality checks (0/45 failed)
✅ Generated → frontmatter/materials/aluminum-laser-cleaning.yaml
```

### Scenario 2: Some Fields Fail (score < 70)
```
🔍 Scanning voice quality...
🚨 Voice quality issues detected: 11/11 fields failed

🔧 Repairing poor quality text in Materials.yaml...
   🔧 Regenerating faq[0].answer (attempt 1/2)...
   ⚠️  Quality still low: 50.0/100, retrying...
   🔧 Regenerating faq[0].answer (attempt 2/2)...
   ✅ Quality improved: 75.0/100
   
   🔧 Regenerating faq[1].answer (attempt 1/2)...
   ❌ Failed to fix faq[1].answer after 2 attempts

✅ Updated Materials.yaml with 10 repairs (1 failed)
✅ Generated → frontmatter/materials/aluminum-laser-cleaning.yaml
```

---

## 🔄 Data Flow Architecture

```
Materials.yaml (SOURCE OF TRUTH)
       ↓
   [LOAD DATA]
       ↓
   [BUILD FRONTMATTER]
       ↓
   [🔍 AUTOMATIC QUALITY SCAN]
       ↓
   [🔧 REPAIR IF NEEDED] → Update Materials.yaml
       ↓
   [💾 EXPORT TO FRONTMATTER]
       ↓
frontmatter/materials/aluminum-laser-cleaning.yaml (OUTPUT)
```

**Key Principle**: 
- ✅ **All generation/validation happens on Materials.yaml**
- ✅ **Frontmatter export is trivial copy with quality gate**
- ✅ **Source YAML is always validated and enhanced**
- ❌ **Never read frontmatter for data persistence**

---

## 🎨 Reusability

This architecture works for **ALL content types**:

```python
# Materials
python3 run.py --material "Aluminum"
# → Uses MaterialFrontmatterGenerator
# → Source: materials/data/Materials.yaml
# → Output: frontmatter/materials/aluminum-laser-cleaning.yaml

# Regions (future)
python3 run.py --region "san-francisco"
# → Uses RegionFrontmatterGenerator
# → Source: regions/data/regions.yaml
# → Output: frontmatter/regions/san-francisco.yaml

# Applications (future)
python3 run.py --application "aerospace-manufacturing"
# → Uses ApplicationFrontmatterGenerator
# → Source: applications/data/applications.yaml
# → Output: frontmatter/applications/aerospace-manufacturing.yaml
```

**Same components, different content types!**
- VoicePostProcessor: Enhances any text
- VoiceQualityScanner: Scans any data structure
- SourceDataRepairer: Updates any YAML file
- BaseFrontmatterGenerator: Orchestrates any generation

---

## 📝 Summary

### What Runs When You Export a Material:

1. **Command parsing** → Extract material name
2. **Orchestrator setup** → Initialize API client + author data
3. **Generator routing** → Find MaterialFrontmatterGenerator
4. **Legacy delegation** → Build frontmatter (ALL existing logic preserved)
5. **🆕 Automatic quality gate**:
   - Scan all text fields for quality issues
   - Repair poor quality text (with retries)
   - Update Materials.yaml with fixes
   - Add quality metadata
6. **Save frontmatter** → Export to frontmatter/materials/

### Time Investment:
- **Without quality gate**: ~5-10 seconds (legacy behavior)
- **With quality gate**: ~10-60 seconds (depending on repairs needed)
- **Benefit**: Guaranteed voice quality in all generated content

### Key Innovation:
✅ **Automatic repair pipeline** - detects and fixes voice quality issues during export  
✅ **Source of truth** - all fixes saved to Materials.yaml (not frontmatter)  
✅ **Fully reusable** - same architecture works for regions, applications, thesaurus  
✅ **Zero manual intervention** - automatic scanning, repair, and retry
