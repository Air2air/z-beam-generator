# Component Summary Generation Prompt

> **Domain**: Settings  
> **Output**: `component_summaries` field in `{material}-settings.yaml`  
> **Purpose**: Material-specific help text for interactive UI components

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Domain Context](#domain-context)
3. [Processing Requirements](#processing-requirements)
4. [Component Definitions](#component-definitions)
5. [Input Data](#input-data)
6. [Output Specification](#output-specification)
7. [Quality Guidelines](#quality-guidelines)
8. [Complete Example](#complete-example)

---

## Quick Start

**What**: Generate 2-3 sentence descriptions for each interactive component on the Settings page.

**Where**: Add `component_summaries` to `frontmatter/settings/{material}-settings.yaml`

**How**: 
1. Load material data from Settings YAML
2. Research material's unique characteristics within its category
3. Generate descriptions through author voice pipeline
4. Save to `component_summaries` field

**Template**:
```
[Component] provides [what it shows/does] for [material] laser cleaning.
[Material-specific insight about unique characteristics].
This helps operators [specific problem it solves].
```

---

## Domain Context

### What Are Domains?

**Domains** = page types in the application  
**Components** = sections within each page  

```
Domain (page type)
└── Components (page sections)
    └── Text content (generated via prompts)
```

### Domain → Component Mapping

| Domain | Page URL | Components |
|--------|----------|------------|
| **materials** | `/laser-cleaning/{material}` | `material_description`, `caption`, `faq` |
| **settings** | `/laser-cleaning/{material}/settings` | `settings_description`, `component_summaries` |
| **contaminants** | `/contaminants/{pattern}` | `material_description`, `caption`, `faq` |

### This Document: Settings Domain

Component summaries belong to the **Settings domain** because they:
- Appear on Settings pages (`/laser-cleaning/{material}/settings`)
- Explain interactive UI components (heatmaps, simulators, diagnostics)
- Help users configure and troubleshoot machine parameters
- Draw from Settings YAML data

**Context for writing**:
- Assume user is actively configuring/troubleshooting
- Reference Settings properties (`machineSettings`, `thermalProperties`, `laserMaterialInteraction`)
- Focus on "what this tool helps you do" not "what this material is"

### Directory Structure

```
domains/settings/text/prompts/        # Domain-specific prompts
├── settings_description.txt          # Existing
└── component_summaries.txt           # NEW: Add prompt template here

frontmatter/settings/                 # Generated output
└── {material}-settings.yaml          # Contains component_summaries field
```

---

## Processing Requirements

### 1. Author Voice Processing (REQUIRED)

All descriptions must go through the standard text generation pipeline:

**Three-Layer Architecture**:
| Layer | Source | Purpose |
|-------|--------|---------|
| Base | `domains/settings/text/prompts/component_summaries.txt` | Content requirements |
| Persona | `data/authors/registry.py` | Author characteristics (4 authors) |
| Formatting | Author's `persona_file` + `formatting_file` | Cultural presentation |

**Quality Gates** (via `QualityGatedGenerator`):
- Winston.ai: 69%+ human score
- Realism: 7.0+/10
- Up to 5 retry attempts with parameter adjustment

**Voice/Variation Parameters**:
- `parameters/voice/professional_voice.py`
- `parameters/voice/jargon_removal.py`
- `parameters/variation/sentence_rhythm_variation.py`
- `parameters/variation/imperfection_tolerance.py`

### 2. Unique Characteristic Research (REQUIRED)

Before generating, research and identify:
- What makes this material **different from others in its category**?
- How do those differences affect laser cleaning?
- How does each component address those unique characteristics?

**Example**: For "316 Stainless Steel" vs "304 Stainless Steel":
- 316 has molybdenum for better corrosion resistance
- Different thermal properties affect safe operating zones
- Material Safety Heatmap should reference these specific differences

---

## Component Definitions

### Summary Table

| ID | Component | Shows | Solves |
|----|-----------|-------|--------|
| 1 | `machine_settings` | Parameter table | "What settings should I use?" |
| 2 | `material_safety_heatmap` | Safe/danger zones | "What will damage this material?" |
| 3 | `energy_coupling_heatmap` | Energy transfer efficiency | "Why isn't it cleaning effectively?" |
| 4 | `thermal_stress_heatmap` | Warping/stress risk | "Why is my material warping?" |
| 5 | `process_effectiveness_heatmap` | Cleaning effectiveness | "Why do I still see residue?" |
| 6 | `heat_buildup_simulator` | Temperature over passes | "How many passes before overheating?" |
| 7 | `diagnostic_center` | Challenges + troubleshooting | "What's causing this problem?" |
| 8 | `research_citations` | Academic sources | "Where did these recommendations come from?" |
| 9 | `faq_settings` | Common Q&A | Quick answers |
| 10 | `dataset_download` | JSON exports | "Can I import these settings?" |
| 11 | `parameter_relationships` | Parameter dependencies | "What else needs adjustment?" |

---

### Detailed Definitions

#### 1. Machine Settings (`machine_settings`)

**Shows**: Table of recommended parameters (power, pulse width, repetition rate, scan speed)

**Generation focus**: Reference `machineSettings` from YAML. Highlight parameters critical for this specific material.

---

#### 2. Material Safety Heatmap (`material_safety_heatmap`)

**Shows**: 2D heatmap of safe (green) to dangerous (red) zones by power × pulse width

**Generation focus**: Reference `laserDamageThreshold`, `thermalDestruction`. Emphasize narrow vs wide safe zones based on material sensitivity.

---

#### 3. Energy Coupling Heatmap (`energy_coupling_heatmap`)

**Shows**: Laser energy transfer efficiency across parameter combinations

**Generation focus**: Reference `absorptivity`, `reflectivity`, `absorptionCoefficient`. Highlight energy coupling challenges for reflective materials.

---

#### 4. Thermal Stress Heatmap (`thermal_stress_heatmap`)

**Shows**: Warping/distortion risk across parameters

**Generation focus**: Reference `thermalExpansionCoefficient`, `thermalShockResistance`, `thermalDiffusivity`. Emphasize warping for high-expansion materials, cracking for brittle materials.

---

#### 5. Process Effectiveness Heatmap (`process_effectiveness_heatmap`)

**Shows**: Cleaning effectiveness (under/optimal/over) across parameters

**Generation focus**: Reference `ablationThreshold` and typical contaminants. Balance under-cleaning vs over-cleaning zones.

---

#### 6. Heat Buildup Simulator (`heat_buildup_simulator`)

**Shows**: Animated temperature accumulation over multiple passes

**Generation focus**: Reference `thermalDiffusivity`, `thermalConductivity`, `passCount`. Materials with low diffusivity need fewer passes.

---

#### 7. Diagnostic Center (`diagnostic_center`)

**Shows**: Material Challenges tab + Troubleshooting tab

**Generation focus**: Reference `material_challenges` and `common_issues`. Mention 1-2 challenges unique to this material (charring, oxide reformation, melting).

---

#### 8. Research Citations (`research_citations`)

**Shows**: Academic/industry papers supporting recommendations

**Generation focus**: Reference `research_library` if present. Mention industrial importance and research relevance.

---

#### 9. FAQ Settings (`faq_settings`)

**Shows**: Common questions about configuring this material

**Generation focus**: Reference common operator questions. Mention material-specific quirks or misconceptions.

---

#### 10. Dataset Download (`dataset_download`)

**Shows**: JSON export of settings and properties

**Generation focus**: Emphasize automation/integration for industrial materials, compliance documentation for heritage materials.

---

#### 11. Parameter Relationships (`parameter_relationships`)

**Shows**: Network visualization of parameter dependencies

**Generation focus**: Highlight critical relationships (power↔speed↔passes for thermal sensitivity, wavelength↔power for absorption challenges).

---

## Input Data

### Required Data Sources

| Source | Location | Fields Used |
|--------|----------|-------------|
| Materials YAML | `frontmatter/materials/{material}-laser-cleaning.yaml` | `material_characteristics`, `laser_material_interaction` |
| Settings YAML | `frontmatter/settings/{material}-settings.yaml` | `machineSettings`, `thermalProperties`, `laserMaterialInteraction`, `material_challenges`, `common_issues` |
| Category knowledge | Domain expertise | Use cases, industry concerns, common contaminants |

### Material-Specific Research

For each material, identify:
1. **Category position**: What category/subcategory?
2. **Differentiators**: What makes it unique within category?
3. **Critical properties**: Which properties most affect laser cleaning?
4. **Industry context**: Aerospace, automotive, heritage, medical?

---

## Output Specification

### YAML Location

Insert `component_summaries` in Settings YAML after `laserMaterialInteraction`, before `material_challenges`:

```yaml
# {material}-settings.yaml

laserMaterialInteraction:
  # ... existing data ...

component_summaries:           # ← INSERT HERE
  machine_settings:
    title: Machine Settings
    description: |
      [2-3 sentences]
  
  material_safety_heatmap:
    title: Material Safety Heatmap
    description: |
      [2-3 sentences]
  
  # ... all 11 components ...

material_challenges:
  # ... existing data ...
```

### Field Structure

```yaml
component_summaries:
  {component_id}:
    title: {Display Name}      # Used in UI headers
    description: |             # YAML multiline string
      {2-3 sentences specific to this material}
```

---

## Quality Guidelines

### DO ✅

- Apply author voice processing (required)
- Use specific numeric values from YAML
- Reference material properties by name
- Mention industry-relevant applications
- Keep to 2-3 sentences
- Use active voice, operator-focused language
- Highlight what makes THIS material unique

### DON'T ❌

- Use generic descriptions that apply to any material
- Include jargon without context
- Make claims not supported by YAML data
- Exceed 3 sentences
- Copy base descriptions verbatim

### Validation Checklist

- [ ] References at least one specific property value
- [ ] Mentions a problem unique to this material type
- [ ] Useful to an operator configuring the machine
- [ ] Factually accurate based on YAML data
- [ ] Reads naturally in Settings page context

---

## Complete Example

### Aluminum Settings Component Summaries

```yaml
# frontmatter/settings/aluminum-settings.yaml

component_summaries:
  machine_settings:
    title: Machine Settings
    description: |
      Displays recommended laser parameters for aluminum cleaning, including the optimal 80-120W power range and 100-200ns pulse width. The high thermal conductivity of aluminum (237 W/m·K) allows for aggressive settings that would damage other materials. Use these validated starting points to avoid the trial-and-error typically required when cleaning reflective metals.
  
  material_safety_heatmap:
    title: Material Safety Heatmap
    description: |
      Interactive heatmap showing aluminum's safe operating zones across power and pulse width combinations. The 660°C melting point and excellent heat dissipation create a wide safe zone compared to other materials. This visualization prevents surface damage by clearly marking the boundary where heat accumulation exceeds aluminum's thermal limits.
  
  energy_coupling_heatmap:
    title: Energy Coupling Heatmap
    description: |
      Maps how efficiently laser energy transfers to aluminum surfaces, accounting for its high reflectivity (0.92 at 1064nm). Polished aluminum reflects most incident light, requiring higher power settings than the heatmap's green zones might suggest for oxidized surfaces. Use this to understand why cleaning parameters differ dramatically between polished and oxidized aluminum.
  
  thermal_stress_heatmap:
    title: Thermal Stress Heatmap
    description: |
      Shows thermal stress and warping risk for aluminum across parameter combinations. Aluminum's high thermal expansion coefficient (23 μm/m·K) makes thin sheets susceptible to distortion. This helps prevent warping on precision parts by identifying parameter zones that keep thermal gradients within acceptable limits.
  
  process_effectiveness_heatmap:
    title: Process Effectiveness Heatmap
    description: |
      Maps cleaning effectiveness for aluminum oxide removal across power and pulse settings. The ablation threshold of 2.5 J/cm² for aluminum oxide is relatively low, meaning effective cleaning occurs at moderate power levels. This balances thoroughness against the risk of substrate damage.
  
  heat_buildup_simulator:
    title: Heat Buildup Simulator
    description: |
      Simulates temperature accumulation during multi-pass aluminum cleaning. Aluminum's excellent thermal diffusivity (97 mm²/s) allows heat to spread rapidly, enabling higher pass counts without localized overheating. Plan multi-pass strategies knowing aluminum handles repeated passes better than most materials.
  
  diagnostic_center:
    title: Diagnostic Center
    description: |
      Provides aluminum-specific troubleshooting for challenges like rapid oxide reformation and reflectivity variations. Aluminum re-oxidizes within minutes of cleaning in ambient air, a unique challenge addressed in the prevention guidance. Use the symptom-based troubleshooting when results don't match expectations.
  
  research_citations:
    title: Research Citations
    description: |
      References peer-reviewed research on aluminum laser cleaning, including studies on oxide layer removal and aerospace applications. The parameter recommendations are backed by published data from industrial and academic sources. Access the full citations for compliance documentation or deeper technical understanding.
  
  faq_settings:
    title: Settings FAQ
    description: |
      Answers common questions about aluminum laser cleaning, including oxide management and surface finish expectations. Addresses the frequent question of why freshly cleaned aluminum dulls quickly (rapid re-oxidation). Quick reference for operators new to aluminum cleaning.
  
  dataset_download:
    title: Dataset Download
    description: |
      Download aluminum-specific machine settings and material properties as JSON datasets. Integrate these validated parameters directly into automated cleaning systems or CNC controllers. Useful for documenting cleaning procedures for aerospace or automotive quality compliance.
  
  parameter_relationships:
    title: Parameter Relationships
    description: |
      Visualizes how aluminum cleaning parameters interact—increasing power typically requires higher scan speeds to prevent heat buildup. The network shows why aluminum's high thermal conductivity creates different trade-offs than steel or titanium. Understand parameter dependencies before making adjustments.
```

### Oak Wood Example (Contrast)

```yaml
material_safety_heatmap:
  title: Material Safety Heatmap
  description: |
    Shows safe operating zones for oak laser cleaning, with power and pulse width combinations color-coded from safe (green) to damage risk (red). Oak's charring threshold of 250°C creates a narrow safe zone that requires careful parameter selection. This prevents charring and discoloration by clearly visualizing the boundary between effective cleaning and thermal damage.
```

Note the contrast: Aluminum has a "wide safe zone" due to heat dissipation; Oak has a "narrow safe zone" due to low charring threshold. Each summary reflects the material's unique characteristics.
