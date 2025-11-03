# FAQ Category Selection Methodology

**Purpose**: Intelligently select FAQ question categories based on material characteristics to ensure relevant, material-specific questions.

---

## 🎯 Core Principle

**Generate questions that address the material's most notable characteristics, challenges, and use cases** rather than using generic templates for all materials.

---

## 📊 Decision Tree Methodology

### Phase 1: Material Profiling (Data Analysis)

Extract key characteristics from Materials.yaml:

```python
material_profile = {
    'thermal': analyze_thermal_properties(),
    'optical': analyze_optical_properties(),
    'mechanical': analyze_mechanical_properties(),
    'chemical': analyze_chemical_reactivity(),
    'applications': analyze_primary_uses(),
    'hazards': analyze_safety_concerns(),
    'rarity': analyze_uniqueness()
}
```

### Phase 2: Category Scoring (Relevance Ranking)

Score each category (0-10) based on material data:

#### **Thermal Categories** (thermal_management, heat_effects)
**Trigger Conditions**:
- ✅ Thermal conductivity < 50 W/(m·K) → Score +8 (poor heat dissipation)
- ✅ Thermal conductivity > 200 W/(m·K) → Score +6 (rapid heat spread)
- ✅ Melting point < 1000°C → Score +7 (heat sensitive)
- ✅ Has 'thermal expansion' property → Score +5
- ✅ Category includes 'polymer', 'composite', 'wood' → Score +9

**Question Selection**:
- High score (7+): "How does heat affect {material} during laser cleaning?"
- Medium score (4-6): "What temperature considerations exist for {material}?"

---

#### **Reflectivity Categories** (reflectivity_challenges, laser_absorption)
**Trigger Conditions**:
- ✅ Reflectivity > 70% → Score +10 (high reflectivity challenge)
- ✅ Reflectivity 50-70% → Score +6 (moderate concern)
- ✅ Category = 'metal' AND no reflectivity data → Score +7 (assume high)
- ✅ Has wavelength-dependent absorption → Score +5
- ✅ Polished/mirror finish mentioned → Score +8

**Question Selection**:
- High score (7+): "Why does {material}'s reflectivity matter for laser cleaning?"
- Medium score (4-6): "What wavelength works best for {material}?"

---

#### **Strength/Fragility Categories** (fragility_risks, damage_resistance)
**Trigger Conditions**:
- ✅ Hardness < 3 Mohs → Score +9 (very fragile)
- ✅ Hardness > 8 Mohs → Score +7 (damage resistant but brittle)
- ✅ Category = 'ceramic', 'glass', 'stone' → Score +8
- ✅ Tensile strength < 100 MPa → Score +7 (weak)
- ✅ Has 'brittle' in properties → Score +10
- ✅ Applications include 'heritage', 'conservation' → Score +9

**Question Selection**:
- High score (7+): "Is {material} fragile during laser cleaning?"
- Medium score (4-6): "What strength characteristics affect {material} cleaning?"

---

#### **Contaminant Categories** (contaminant_removal_difficulty, surface_damage_from_contaminants)
**Trigger Conditions**:
- ✅ Porous material (porosity > 5%) → Score +9 (contaminants penetrate)
- ✅ Category = 'stone', 'concrete', 'wood' → Score +8
- ✅ High surface roughness (Ra > 2 µm) → Score +7
- ✅ Reactive material (forms oxides easily) → Score +8
- ✅ Applications include 'marine', 'outdoor' → Score +7
- ✅ Has 'corrosion resistance' property → Score +6

**Question Selection**:
- High score (7+): "Which contaminants are hardest to remove from {material}?"
- Medium score (4-6): "Can contaminants damage {material}'s surface?"

---

#### **Unusual/Rare Behavior** (rare_behavior, special_requirements)
**Trigger Conditions**:
- ✅ Material not in top 50 most common → Score +8
- ✅ Has phase transformation properties → Score +9
- ✅ Anisotropic properties (direction-dependent) → Score +8
- ✅ Composite with >3 material phases → Score +7
- ✅ Exhibits unique optical phenomena (iridescence, etc.) → Score +9
- ✅ Heritage/archaeological applications → Score +8

**Question Selection**:
- High score (7+): "What unusual behaviors does {material} exhibit during cleaning?"
- Medium score (4-6): "What makes {material} different from other materials?"

---

#### **Application Categories** (application_advantages, application_challenges)
**Trigger Conditions**:
- ✅ Primary application is highly specialized → Score +8
- ✅ Application count > 6 → Score +7 (versatile material)
- ✅ Application includes 'aerospace', 'medical', 'nuclear' → Score +9 (critical)
- ✅ Application includes 'heritage', 'art' → Score +8 (irreplaceable)
- ✅ Material has unique application advantage → Score +7

**Question Selection**:
- High score (7+): "Why is {material} chosen for {primary_application}?"
- Medium score (4-6): "What challenges does {material} present in use?"

---

#### **Cost Categories** (cost_economics)
**Trigger Conditions**:
- ✅ ALWAYS include (baseline score: +10)
- ✅ Rare/expensive material → Score +12
- ✅ High processing complexity → Score +11

**Question Selection**:
- Always: "How much does it cost to laser clean {material}?"

---

#### **Safety Categories** (safety, damage_risks)
**Trigger Conditions**:
- ✅ Toxic material (Be, Pb, Cd, As) → Score +10
- ✅ Generates hazardous fumes → Score +9
- ✅ Explosive/flammable → Score +10
- ✅ High reflectivity (eye hazard) → Score +8
- ✅ Category = 'metal' → Score +6 (fume concern)

**Question Selection**:
- High score (8+): "Is laser cleaning {material} safe?"
- Medium score (5-7): "What safety precautions are critical for {material}?"

---

### Phase 3: Dynamic Question Selection Algorithm

```python
def select_faq_categories(material_data, question_count=9):
    """
    Select most relevant categories based on material characteristics
    
    Returns: List of (question_template, category, score) sorted by relevance
    """
    
    # Score all categories
    category_scores = {}
    
    # Thermal analysis
    thermal_score = score_thermal_relevance(material_data)
    category_scores['thermal_management'] = thermal_score
    
    # Optical analysis
    reflectivity_score = score_reflectivity_relevance(material_data)
    category_scores['reflectivity_challenges'] = reflectivity_score
    
    # Mechanical analysis
    fragility_score = score_fragility_relevance(material_data)
    category_scores['fragility_risks'] = fragility_score
    
    # Contaminant analysis
    contaminant_score = score_contaminant_relevance(material_data)
    category_scores['contaminant_removal_difficulty'] = contaminant_score
    
    # Unusual behavior analysis
    unusual_score = score_unusual_relevance(material_data)
    category_scores['rare_behavior'] = unusual_score
    
    # Application analysis
    application_score = score_application_relevance(material_data)
    category_scores['application_advantages'] = application_score
    
    # Safety analysis
    safety_score = score_safety_relevance(material_data)
    category_scores['safety'] = safety_score
    
    # Always include (baseline categories)
    baseline_categories = [
        ('cost_economics', 10),  # Always relevant
        ('machine_settings', 8),  # Always needed
    ]
    
    # Sort by score and select top N
    sorted_categories = sorted(
        category_scores.items(), 
        key=lambda x: x[1], 
        reverse=True
    )
    
    # Combine baseline + top scored
    selected = baseline_categories
    remaining_slots = question_count - len(baseline_categories)
    selected.extend(sorted_categories[:remaining_slots])
    
    return selected
```

---

## 🔍 Material Category Profiles

### **Metals** (Titanium, Aluminum, Steel, Copper)
**Prioritize**:
1. ✅ Reflectivity challenges (always high)
2. ✅ Thermal management (conductivity varies widely)
3. ✅ Oxide formation (heat_induced_contamination)
4. ✅ Strength considerations (yield stress, hardness)
5. ✅ Application advantages (why chosen for aerospace/marine)

**Avoid**:
- ❌ Fragility questions (metals are robust)
- ❌ Rare behavior (unless specialty alloy)

---

### **Ceramics** (Alumina, Silicon Carbide, Porcelain)
**Prioritize**:
1. ✅ Fragility risks (always brittle)
2. ✅ Thermal damage (thermal shock sensitivity)
3. ✅ Strength characteristics (high hardness, low toughness)
4. ✅ Heat effects (poor thermal conductivity)
5. ✅ Contaminant removal (porous surfaces)

**Avoid**:
- ❌ Reflectivity (usually low concern)
- ❌ Application advantages (limited to niche uses)

---

### **Stone** (Marble, Granite, Alabaster)
**Prioritize**:
1. ✅ Heritage/conservation concerns
2. ✅ Contaminant penetration (porous)
3. ✅ Fragility (varies by type)
4. ✅ Unique properties (mineral composition)
5. ✅ Surface damage from contaminants

**Avoid**:
- ❌ Speed/efficiency (not primary concern for heritage)
- ❌ Cost (preservation > cost)

---

### **Polymers** (Plastics, Composites)
**Prioritize**:
1. ✅ Thermal damage (low melting points)
2. ✅ Heat effects (poor conductivity)
3. ✅ Damage risks (easily degraded)
4. ✅ Unusual behavior (phase changes)
5. ✅ Limitations (many contraindications)

**Avoid**:
- ❌ Reflectivity (not metallic)
- ❌ Strength considerations (low strength expected)

---

### **Composites** (Carbon Fiber, Fiberglass)
**Prioritize**:
1. ✅ Unusual behavior (multi-phase interaction)
2. ✅ Special requirements (differential heating)
3. ✅ Damage risks (delamination)
4. ✅ Thermal management (anisotropic properties)
5. ✅ Application challenges (aerospace complexity)

---

## 📈 Scoring Functions (Implementation Examples)

### Thermal Relevance Scoring
```python
def score_thermal_relevance(material_data):
    score = 0
    props = material_data.get('materialProperties', {})
    
    # Check thermal conductivity
    thermal_cond = get_property_value(props, 'thermalConductivity')
    if thermal_cond:
        if thermal_cond < 50:
            score += 8  # Poor heat dissipation
        elif thermal_cond > 200:
            score += 6  # Rapid heat spread
    
    # Check melting point
    melting_point = get_property_value(props, 'meltingPoint')
    if melting_point and melting_point < 1000:
        score += 7  # Heat sensitive
    
    # Category-based
    category = material_data.get('category', '').lower()
    if category in ['polymer', 'composite', 'wood']:
        score += 9  # Thermally sensitive categories
    
    return min(score, 10)  # Cap at 10
```

### Reflectivity Relevance Scoring
```python
def score_reflectivity_relevance(material_data):
    score = 0
    props = material_data.get('materialProperties', {})
    
    # Check reflectivity value
    reflectivity = get_property_value(props, 'laserReflectivity')
    if reflectivity:
        if reflectivity > 70:
            score += 10  # Major challenge
        elif reflectivity > 50:
            score += 6  # Moderate concern
    
    # Category-based assumption
    category = material_data.get('category', '').lower()
    if category == 'metal' and not reflectivity:
        score += 7  # Assume high for metals
    
    return min(score, 10)
```

---

## 🎯 Quality Thresholds

**Minimum Score to Include**: 5/10
- Categories scoring < 5 are likely not relevant enough

**Maximum Questions per Category Group**: 3
- Avoid over-concentration in one area (e.g., max 3 thermal questions)

**Diversity Requirement**: 
- Must have at least 5 different category groups represented
- Ensures broad coverage

---

## 🔄 Fallback Strategy

If insufficient high-scoring categories:
1. Include baseline categories (cost, machine_settings, safety)
2. Add generic practical questions (time_duration, quality_verification)
3. Include comparison questions (vs similar materials)
4. Add operator questions (training, troubleshooting)

---

## 📝 Implementation Checklist

### Phase 1: Data Extraction
- [ ] Extract all material properties from Materials.yaml
- [ ] Parse category and applications
- [ ] Identify hazards and special characteristics
- [ ] Calculate complexity metrics

### Phase 2: Scoring
- [ ] Implement scoring function for each category group
- [ ] Apply material category profiles
- [ ] Rank categories by relevance score
- [ ] Filter scores below threshold (5/10)

### Phase 3: Question Selection
- [ ] Select top N scored categories
- [ ] Include mandatory baseline categories
- [ ] Apply diversity constraints
- [ ] Generate question templates with proper focus points

### Phase 4: Validation
- [ ] Verify category diversity (≥5 groups)
- [ ] Check material-specific question text
- [ ] Ensure no duplicate question types
- [ ] Validate focus points match category

---

## 💡 Examples

### Example 1: Titanium (Aerospace Metal)
**Material Profile**:
- High reflectivity (moderate)
- Low thermal conductivity (21.9 W/m·K)
- High strength, excellent corrosion resistance
- Reactive (forms oxides easily)
- Primary use: Aerospace, marine

**Scoring Results**:
```
reflectivity_challenges: 7/10 ✅
thermal_management: 8/10 ✅
heat_induced_contamination: 8/10 ✅
strength_considerations: 7/10 ✅
application_advantages: 9/10 ✅ (aerospace)
rare_behavior: 6/10 ✅ (oxide iridescence)
cost_economics: 10/10 ✅ (baseline)
machine_settings: 8/10 ✅ (baseline)
safety: 6/10 ✅

fragility_risks: 2/10 ❌ (robust metal)
```

**Selected Questions** (9 total):
1. Cost (baseline)
2. Machine settings (baseline)
3. Application advantages (9/10)
4. Thermal management (8/10)
5. Heat-induced contamination (8/10)
6. Reflectivity challenges (7/10)
7. Strength considerations (7/10)
8. Rare behavior (6/10)
9. Safety (6/10)

---

### Example 2: Alabaster (Heritage Stone)
**Material Profile**:
- Low hardness (1.5-3 Mohs)
- Porous, translucent
- Heritage/conservation applications
- Calcium sulfate composition
- Delicate surface

**Scoring Results**:
```
fragility_risks: 10/10 ✅
contaminant_removal_difficulty: 9/10 ✅ (porous)
surface_damage_from_contaminants: 9/10 ✅
unique_properties: 8/10 ✅ (translucency)
thermal_damage: 7/10 ✅
application_challenges: 7/10 ✅ (conservation)
cost_economics: 10/10 ✅ (baseline)
damage_risks: 9/10 ✅

reflectivity_challenges: 2/10 ❌ (stone)
speed_efficiency: 3/10 ❌ (not priority for heritage)
```

**Selected Questions** (9 total):
1. Cost (baseline)
2. Fragility risks (10/10)
3. Contaminant removal difficulty (9/10)
4. Surface damage from contaminants (9/10)
5. Damage risks (9/10)
6. Unique properties (8/10)
7. Thermal damage (7/10)
8. Application challenges (7/10 - conservation)
9. Special requirements (6/10)

---

## 🚀 Benefits of This Methodology

1. **Material-Specific**: Questions match material's actual characteristics
2. **Data-Driven**: Decisions based on Materials.yaml properties
3. **Scalable**: Works for all 132 materials automatically
4. **Quality**: High-relevance questions only
5. **Diverse**: Ensures broad topic coverage
6. **Intelligent**: Avoids irrelevant questions (e.g., fragility for steel)
7. **Maintainable**: Clear scoring logic for future updates

---

## 📊 Success Metrics

**Per Material**:
- ✅ Category diversity: ≥5 different category groups
- ✅ Relevance score: Average ≥6/10 for selected questions
- ✅ Material-specific: 100% questions mention material name
- ✅ Property integration: ≥80% questions reference actual property values

**Across All Materials**:
- ✅ No two materials have identical question sets
- ✅ Category distribution reflects material diversity
- ✅ High-scoring categories (8+) always included
- ✅ User satisfaction with question relevance

---

**Status**: Proposed Methodology  
**Next Step**: Implement scoring functions in `_generate_material_questions()`  
**Expected Impact**: 40-60% improvement in question relevance per material
