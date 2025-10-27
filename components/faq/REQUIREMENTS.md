# FAQ Component Requirements

**Component Type**: Material-Specific FAQ Generation  
**Complexity**: Complex (Multi-Section, Category-Aware)  
**Created**: October 26, 2025  
**Architecture Pattern**: Following Caption Component dual-voice model

---

## 🎯 Overview

The FAQ component generates material-specific frequently asked questions and answers that highlight unique characteristics, handling requirements, and application-specific considerations for laser cleaning.

### Core Principle

**Focus on what makes THIS material unique** - Not generic laser cleaning FAQs, but material-specific technical details that operators, engineers, and decision-makers need to know.

---

## 📋 FAQ Categories & Question Structure

### Category 1: Thermal Characteristics & Heat Management
**Focus**: Material-specific thermal behavior during laser cleaning

**Required Questions** (5-7 questions):

1. **Heat Sensitivity**
   - Q: "How does {material_name} respond to laser-induced thermal stress during cleaning?"
   - Answer Focus:
     * Thermal conductivity impact on heat dissipation
     * Specific temperature thresholds for damage
     * Heat-affected zone (HAZ) characteristics
     * Cooling requirements (if any)
     * Comparison to similar materials in category

2. **Thermal Damage Indicators**
   - Q: "What are the signs of thermal damage when cleaning {material_name}?"
   - Answer Focus:
     * Visual indicators (discoloration, warping, surface changes)
     * Microscopic damage patterns
     * Irreversible vs recoverable thermal effects
     * Material-specific thermal destruction point

3. **Heat Distribution**
   - Q: "How does heat distribute across {material_name} during laser cleaning?"
   - Answer Focus:
     * Thermal diffusivity characteristics
     * Hot spot formation risks
     * Edge vs center heating differences
     * Thickness-dependent thermal behavior

4. **Cooling Strategies** (if applicable)
   - Q: "Does {material_name} require active cooling during laser cleaning?"
   - Answer Focus:
     * When cooling is necessary vs optional
     * Recommended cooling methods
     * Impact on cleaning efficiency
     * Material-specific cooling considerations

5. **Temperature Monitoring**
   - Q: "What temperature monitoring is recommended for {material_name}?"
   - Answer Focus:
     * Critical temperature thresholds
     * Recommended monitoring techniques
     * Real-time vs post-process monitoring
     * Material-specific thermal limits

---

### Category 2: Physical Properties & Laser Interaction
**Focus**: How material's physical structure affects laser cleaning

**Required Questions** (6-8 questions):

1. **Laser Reflectivity Behavior**
   - Q: "How reflective is {material_name} to common laser wavelengths?"
   - Answer Focus:
     * Wavelength-specific reflectivity values
     * Impact on cleaning efficiency
     * Safety considerations from reflections
     * Comparison to other materials in category
     * Surface finish impact on reflectivity

2. **Absorption Characteristics**
   - Q: "How efficiently does {material_name} absorb laser energy?"
   - Answer Focus:
     * Absorption coefficient at typical wavelengths (1064nm, 532nm, etc.)
     * Depth of laser penetration
     * Surface vs subsurface absorption
     * Wavelength selection recommendations

3. **Surface Morphology Effects**
   - Q: "How does {material_name}'s surface texture affect laser cleaning?"
   - Answer Focus:
     * Rough vs smooth surface considerations
     * Porosity impact on cleaning effectiveness
     * Grain structure influence
     * Surface preparation requirements

4. **Density & Structural Considerations**
   - Q: "How does {material_name}'s density affect laser cleaning parameters?"
   - Answer Focus:
     * Density value and impact on laser interaction
     * Ablation threshold relationship to density
     * Material removal rates
     * Structural integrity during cleaning

5. **Optical Properties**
   - Q: "What optical characteristics of {material_name} influence laser cleaning?"
   - Answer Focus:
     * Transparency, translucency, or opacity
     * Subsurface scatter considerations
     * Color-dependent absorption
     * Special optical behaviors (if any)

6. **Material Thickness Effects**
   - Q: "How does thickness affect laser cleaning of {material_name}?"
   - Answer Focus:
     * Thin vs thick substrate considerations
     * Heat accumulation in different thicknesses
     * Cleaning parameter adjustments by thickness
     * Through-thickness damage risks

---

### Category 3: Material Handling & Damage Resistance
**Focus**: Special handling, strength, and fragility considerations

**Required Questions** (5-7 questions):

1. **Mechanical Strength Assessment**
   - Q: "How mechanically robust is {material_name} during laser cleaning?"
   - Answer Focus:
     * Tensile, compressive, flexural strength values
     * Vulnerability to mechanical stress during cleaning
     * Fixturing requirements
     * Handling precautions

2. **Fragility & Damage Risks**
   - Q: "What are the primary damage risks when laser cleaning {material_name}?"
   - Answer Focus:
     * Brittle vs ductile behavior
     * Fracture risk factors
     * Stress concentration points
     * Impact resistance during handling

3. **Surface Hardness Considerations**
   - Q: "How does {material_name}'s hardness affect cleaning approach?"
   - Answer Focus:
     * Hardness value (Mohs, Vickers, etc.)
     * Scratch resistance during cleaning
     * Abrasion from contaminants
     * Cleaning intensity adjustments

4. **Pre-Cleaning Inspection**
   - Q: "What should be inspected on {material_name} before laser cleaning?"
   - Answer Focus:
     * Pre-existing cracks or defects
     * Surface condition assessment
     * Structural integrity checks
     * Documentation requirements

5. **Post-Cleaning Handling**
   - Q: "What special handling is needed for {material_name} after laser cleaning?"
   - Answer Focus:
     * Cooling/stabilization time
     * Surface sensitivity post-cleaning
     * Protective measures needed
     * Storage considerations

6. **Repair vs Replace Decisions** (if applicable)
   - Q: "When is {material_name} too damaged for laser cleaning?"
   - Answer Focus:
     * Damage assessment criteria
     * Cleaning limitations
     * Alternative treatment methods
     * Economic considerations

---

### Category 4: Arcane & Unusual Material Characteristics
**Focus**: Unique, unexpected, or specialized properties

**Required Questions** (3-5 questions, highly material-specific):

1. **Unique Material Behaviors**
   - Q: "What unusual characteristics of {material_name} affect laser cleaning?"
   - Answer Focus:
     * Phase transformations
     * Unexpected thermal behaviors
     * Chemical reactions under laser irradiation
     * Magnetic, electrical, or other special properties

2. **Historical or Cultural Significance** (if applicable)
   - Q: "Why is {material_name} historically or culturally significant in laser cleaning contexts?"
   - Answer Focus:
     * Heritage conservation applications
     * Artistic or archaeological importance
     * Specialized preservation requirements
     * Case studies or notable projects

3. **Industry-Specific Quirks**
   - Q: "What industry-specific challenges exist when cleaning {material_name}?"
   - Answer Focus:
     * Sector-specific requirements (aerospace, medical, etc.)
     * Regulatory constraints
     * Quality standards unique to material
     * Specialized equipment needs

4. **Material Aging Effects** (if applicable)
   - Q: "How does aging affect laser cleaning of {material_name}?"
   - Answer Focus:
     * Degradation patterns over time
     * Changes in cleaning parameters for aged material
     * Restoration vs preservation considerations
     * Long-term stability post-cleaning

5. **Rare or Uncommon Applications**
   - Q: "What are lesser-known uses of laser cleaning for {material_name}?"
   - Answer Focus:
     * Emerging applications
     * Experimental techniques
     * Cross-industry knowledge transfer
     * Future possibilities

---

### Category 5: Contaminant Interactions
**Focus**: How contaminants interact with material surface

**Required Questions** (6-8 questions):

1. **Common Contaminant Types**
   - Q: "What contaminants are typically found on {material_name} surfaces?"
   - Answer Focus:
     * Industry-specific contamination sources
     * Organic vs inorganic contaminants
     * Atmospheric vs process-related contamination
     * Seasonal or environmental factors

2. **Physical Surface Damage from Contaminants**
   - Q: "Can contaminants physically damage {material_name} surfaces?"
   - Answer Focus:
     * Corrosion or oxidation effects
     * Chemical etching or pitting
     * Staining or discoloration
     * Subsurface contamination penetration

3. **Laser Removal Difficulty by Contaminant**
   - Q: "Which contaminants are hardest to remove from {material_name}?"
   - Answer Focus:
     * Ranking of contaminant difficulty
     * Reasons for removal challenges
     * Parameter adjustments by contaminant type
     * Alternative approaches for stubborn contaminants

4. **Contaminant-Substrate Bonding**
   - Q: "How strongly do contaminants bond to {material_name}?"
   - Answer Focus:
     * Adhesion mechanisms (mechanical, chemical, etc.)
     * Bond strength variations
     * Impact on fluence requirements
     * Removal without substrate damage

5. **Heat Effects During Contaminant Removal**
   - Q: "What heat-related challenges occur when removing contaminants from {material_name}?"
   - Answer Focus:
     * Contaminant burning or vaporization
     * Secondary contamination from thermal decomposition
     * Heat transfer through contaminant layer
     * Material damage during high-energy removal

6. **Multi-Layer Contamination**
   - Q: "How should multi-layer contamination on {material_name} be addressed?"
   - Answer Focus:
     * Layer-by-layer cleaning strategies
     * Selective removal techniques
     * Parameter progression approaches
     * Verification between layers

7. **Re-Contamination Risks**
   - Q: "How susceptible is cleaned {material_name} to re-contamination?"
   - Answer Focus:
     * Surface energy changes post-cleaning
     * Protective coating recommendations
     * Storage environment requirements
     * Time-sensitive processing needs

---

### Category 6: Application-Specific Considerations
**Focus**: Why material is chosen and challenges in applications

**Required Questions** (5-7 questions):

1. **Material Selection Rationale**
   - Q: "Why is {material_name} chosen for {primary_application}?"
   - Answer Focus:
     * Key performance advantages
     * Critical properties for application
     * Comparison to alternative materials
     * Cost-benefit considerations

2. **Application-Specific Cleaning Challenges**
   - Q: "What unique cleaning challenges does {material_name} present in {primary_application}?"
   - Answer Focus:
     * Geometry complexity
     * Access limitations
     * Tolerance requirements
     * Quality verification methods

3. **Performance Impact of Cleaning**
   - Q: "How does laser cleaning affect {material_name} performance in its applications?"
   - Answer Focus:
     * Functional property changes (if any)
     * Surface finish requirements
     * Dimensional stability
     * Long-term performance validation

4. **Industry Standards Compliance**
   - Q: "What standards govern laser cleaning of {material_name} for {application}?"
   - Answer Focus:
     * Regulatory requirements (FDA, ANSI, etc.)
     * Industry-specific quality standards
     * Documentation and traceability needs
     * Certification requirements

5. **Problem Prevention Strategies**
   - Q: "How can problems be prevented when laser cleaning {material_name} in {application}?"
   - Answer Focus:
     * Process control measures
     * Quality monitoring techniques
     * Operator training requirements
     * Troubleshooting guidelines

6. **Alternative Treatment Comparison**
   - Q: "How does laser cleaning of {material_name} compare to alternative methods?"
   - Answer Focus:
     * Chemical cleaning comparison
     * Mechanical cleaning comparison
     * Cost-effectiveness analysis
     * When laser is NOT the best option

---

## 🏗️ Architecture & Implementation

### Component Structure

Following Caption component pattern:

```
FAQ Component
  ├── Category-specific question generation (6 categories)
  ├── Material-aware answer generation (pulls from Materials.yaml + Categories.yaml)
  ├── Voice service integration (country-specific author voice)
  ├── Validation (technical accuracy, word counts, completeness)
  └── Materials.yaml persistence
```

### Voice Service Integration

**Pattern**: Multiple independent Voice calls, one per FAQ

```python
# For each FAQ question:
answer = voice.generate_content(
    template="technical_faq_answer",
    material_name=material_name,
    material_data=material_data,
    question=question_text,
    answer_focus=answer_requirements,
    target_words=150-300,  # Per answer
    technical_depth="expert",
    include_values=True,  # Pull actual property values
    category_context=category_data
)
```

### Data Sources

**Material Properties** (from Materials.yaml):
- `materialProperties.material_characteristics` → Physical properties, strength, hardness
- `materialProperties.laser_material_interaction` → Reflectivity, absorption, thermal behavior
- `machineSettings` → Recommended parameters
- `applications` → Primary use cases
- `category` → Material category for context

**Category Defaults** (from Categories.yaml):
- `category_ranges` → Property ranges for comparison
- `common_applications` → Typical industry uses
- `regulatory_standards` → Relevant standards

**Generated Content**:
- Author voice (country-specific technical writing)
- Real property values integrated into answers
- Category comparisons ("compared to other metals...")
- Application-specific examples

---

## 📊 Generation Requirements

### Question Count & Focus

**Based on z-beam.com live implementation**: 7-12 questions per material (not 30-42)

**Actual question types observed** (Poplar example):
1. "What types of contaminants can be removed from {material}?"
2. "What makes {material} challenging to laser clean?"
3. "Why is {wavelength} recommended for {material}?"
4. "Why is laser cleaning preferred for {material} in {primary_application}?"
5. "How does {material} compare to similar materials for laser cleaning?"
6. "What surface quality results can I expect from laser cleaning {material}?"
7. "What are the environmental benefits of laser cleaning {material}?"

**Recommended Range**: 7-12 questions per material (allows flexibility for material complexity)

### Answer Requirements

**Length**: 150-300 words per answer
- Brief answers (150-200 words): Simple yes/no with explanation
- Standard answers (200-250 words): Technical details with examples
- Comprehensive answers (250-300 words): Multi-faceted topics with comparisons

**Technical Depth**:
- ✅ Include actual property values from Materials.yaml
- ✅ Reference specific settings from machineSettings
- ✅ Compare to category ranges ("Copper's thermal conductivity of 398 W/m·K is among the highest for metals...")
- ✅ Use author's country-specific voice and technical style
- ✅ Include relevant standards references

**Accuracy**:
- ❌ NO generic/template answers
- ❌ NO made-up values
- ✅ ALL values must come from Materials.yaml or Categories.yaml
- ✅ Clear indication when data is unavailable ("specific thermal damage threshold not yet characterized")

---

## 🎭 Author Voice Integration

Each FAQ answer written in author's voice (like Caption):

### Yi-Chun Lin (Taiwan)
- Systematic technical approach
- Precise measurements with units
- Comparative analysis with peer materials
- CNS standard references

### Alessandro Moretti (Italy)
- Engineering sophistication
- Refined technical vocabulary  
- European perspective on applications
- UNI EN ISO standards

### Todd Dunning (USA)
- Efficiency-focused pragmatism
- Bottom-line practical advice
- Industrial application emphasis
- ASTM/ASME standards

### Ikmanda Roswati (Indonesia)
- Collaborative language patterns
- Environmental responsibility
- Regional application contexts
- SNI standard compliance

**Voice Authenticity**: Each answer maintains author credibility with country-specific linguistic markers, technical depth, and cultural perspective.

---

## 📝 Output Format

### YAML Structure (in Materials.yaml)

**Based on existing z-beam.com implementation (Poplar example):**

```yaml
materials:
  Poplar:
    # ... existing fields ...
    
    faq:
      generated: '2025-10-26T12:00:00.000000Z'
      author: Todd Dunning  # Same as material author
      generation_method: ai_research
      total_questions: 7
      total_words: 2100  # ~300 words per answer
      
      questions:
        - question: "What types of contaminants can be removed from Poplar?"
          answer: "Poplar surfaces commonly accumulate organic residues, dirt particles, oily smears, and environmental deposits that degrade the wood's natural appearance and structural integrity. Laser cleaning effectively removes surface contamination including dust, grime, old finishes, and oxidized layers without damaging the delicate wood fibers..."
          category: contaminants
          word_count: 298
          includes_properties: [porosity, density, laserAbsorption]
        
        - question: "What makes Poplar challenging to laser clean?"
          answer: "Poplar's low density of 0.43 g/cm³ and high porosity of 0.72 create unique challenges during laser cleaning. The soft, porous structure absorbs laser energy differently than harder woods, requiring precise parameter control to avoid fiber damage or scorching..."
          category: material_handling
          word_count: 287
          includes_properties: [density, porosity, thermalConductivity, hardness]
        
        - question: "Why is 1064 nm wavelength recommended for Poplar?"
          answer: "The 1064 nm Nd:YAG wavelength provides optimal balance for Poplar cleaning due to the material's laser absorption coefficient of 32.7% and reflectivity of 42.7% at this wavelength. This combination enables effective contaminant removal while minimizing heat buildup in the wood substrate..."
          category: physical_properties
          word_count: 312
          includes_properties: [laserAbsorption, laserReflectivity, wavelength]
        
        - question: "Why is laser cleaning preferred for Poplar in Aerospace applications?"
          answer: "In aerospace applications, Poplar is valued for its exceptional strength-to-weight ratio (tensile strength 101 MPa, density 0.43 g/cm³) in composite structures and tooling. Laser cleaning preserves these critical properties while removing contamination from precision surfaces..."
          category: applications
          word_count: 295
          includes_properties: [tensileStrength, density, youngsModulus]
        
        - question: "How does Poplar compare to similar materials for laser cleaning?"
          answer: "Compared to other hardwoods in its category, Poplar's thermal conductivity of 0.12 W/(m·K) and thermal destruction point of 300°C position it as a moderate-sensitivity material. Harder woods like Oak require higher energy densities, while softer woods like Pine need gentler parameters..."
          category: physical_properties
          word_count: 278
          includes_properties: [thermalConductivity, thermalDestruction, hardness, density]
        
        - question: "What surface quality results can I expect from laser cleaning Poplar?"
          answer: "Properly parameterized laser cleaning restores Poplar's natural grain structure and color while maintaining surface roughness within acceptable limits. The process achieves contaminant removal efficiency of 95-99% while preserving wood fiber integrity, as evidenced by microscopic analysis showing intact grain patterns and no thermal damage..."
          category: outcome_quality
          word_count: 318
          includes_properties: [surfaceRoughness, thermalDestruction]
        
        - question: "What are the environmental benefits of laser cleaning Poplar?"
          answer: "Laser cleaning of Poplar eliminates chemical waste streams, reduces water consumption by 100% compared to wet cleaning methods, and produces no VOC emissions. The process generates minimal waste (vaporized contaminants only) and requires no hazardous disposal procedures, making it ideal for sustainable woodworking operations..."
          category: environmental
          word_count: 312
          includes_environmental_impacts: [Chemical Waste Elimination, Water Usage Reduction]
```

### Frontmatter Export Format

**Matches existing z-beam.com structure (simple question list):**

```yaml
# In frontmatter YAML files
faq:
  questions:
    - question: "What types of contaminants can be removed from Poplar?"
      answer: "Poplar surfaces commonly accumulate organic residues, dirt particles..."
    
    - question: "What makes Poplar challenging to laser clean?"
      answer: "Poplar's low density of 0.43 g/cm³ and high porosity of 0.72..."
    
    - question: "Why is 1064 nm wavelength recommended for Poplar?"
      answer: "The 1064 nm Nd:YAG wavelength provides optimal balance..."
    
    # ... remaining questions ...
```

**Frontend Display** (based on z-beam.com):
- Accordion/expandable format
- Questions visible, answers hidden until clicked
- Material name inserted into questions dynamically
- Clean, scannable list format

---

## ✅ Validation Requirements

### Content Validation

1. **Question Coverage**:
   - All 6 categories must have questions
   - Minimum question count per category met
   - No duplicate questions

2. **Answer Quality**:
   - Word count within range (150-300 per answer)
   - Technical values included from Materials.yaml
   - Author voice consistency
   - No generic/template responses

3. **Technical Accuracy**:
   - All numerical values traceable to Materials.yaml or Categories.yaml
   - Property values within category ranges
   - Consistent units
   - Proper scientific notation

4. **Completeness**:
   - Required questions answered
   - Material-specific content (not generic laser cleaning)
   - Application-specific examples
   - Category comparisons included

### Fail-Fast Conditions

❌ **Generate Error If**:
- Material missing critical properties (thermal_conductivity, density, etc.)
- Author voice template not found
- Required category data unavailable
- Answer generation fails validation
- Word count violations
- Duplicate questions detected

✅ **Allow Graceful Degradation For**:
- Optional arcane characteristics (3-5 questions vs exact count)
- Missing non-critical properties (skip that technical detail)
- Application-specific questions (adjust to available applications)

---

## 🔄 Generation Workflow

### Step 1: Material Analysis
```python
# Analyze material data to determine FAQ focus
material_category = material_data['category']
key_properties = extract_critical_properties(material_data)
applications = material_data['applications']
unique_characteristics = identify_unique_traits(material_data, category_data)
```

### Step 2: Question Generation
```python
# Generate category-specific questions
questions = []
for category in FAQ_CATEGORIES:
    category_questions = generate_category_questions(
        category=category,
        material_name=material_name,
        material_data=material_data,
        count=category_min_max[category]
    )
    questions.extend(category_questions)
```

### Step 3: Answer Generation (Multiple Voice Calls)
```python
# Generate each answer independently via Voice service
answers = []
for question in questions:
    answer = voice.generate_content(
        template="technical_faq_answer",
        material_name=material_name,
        material_data=material_data,
        question=question['text'],
        answer_focus=question['focus_points'],
        target_words=calculate_answer_length(question),
        category_context=category_data
    )
    answers.append(answer)
```

### Step 4: Validation & Combination
```python
# Validate all answers
validated_faqs = validate_faq_content(questions, answers, material_data)

# Combine into structured format
faq_data = structure_faq_output(validated_faqs)
```

### Step 5: Materials.yaml Persistence
```python
# Write to Materials.yaml (like Caption component)
write_faq_to_materials(material_name, faq_data)
```

---

## 🎯 Use Cases

### 1. **Operator Training**
Engineers and technicians use FAQs to understand material-specific challenges before cleaning operations.

### 2. **Troubleshooting**
When cleaning problems occur, FAQs provide immediate material-specific guidance.

### 3. **Process Planning**
Project managers reference FAQs to assess feasibility and plan cleaning operations.

### 4. **Quality Assurance**
QA teams use FAQs to understand inspection criteria and damage indicators.

### 5. **Customer Education**
Sales/support teams provide FAQs to customers evaluating laser cleaning for specific materials.

### 6. **Documentation**
FAQs serve as technical documentation for regulatory compliance and knowledge management.

---

## 🚀 Future Enhancements

### Phase 2 Features
- **Interactive FAQ Filtering**: Filter by category, application, property range
- **Cross-Reference Linking**: Link FAQ answers to specific property values
- **Comparative FAQs**: "How does Material A vs Material B differ in..."
- **Case Study Integration**: Real-world examples in FAQ answers
- **Video/Image Links**: Visual demonstrations referenced in FAQs

### Phase 3 Features
- **Dynamic FAQ Generation**: Generate custom FAQs based on user query
- **FAQ Search**: Natural language search across all material FAQs
- **FAQ Versioning**: Track FAQ updates as material knowledge improves
- **Expert Review System**: Subject matter expert validation workflow

---

## 📚 References

### Similar Components
- **Caption Component**: Dual-voice architecture pattern
- **Text Component**: Long-form content generation
- **Voice Service**: Country-specific author authenticity

### Data Sources
- **Materials.yaml**: Material-specific property values
- **Categories.yaml**: Category ranges and defaults
- **RegulatoryStandards.yaml** (future): Standards references

### Standards
- **Technical Writing**: IEEE Technical Writing Standards
- **FAQ Best Practices**: Nielsen Norman Group (UX Research)
- **Voice Authenticity**: Linguistic pattern research by country

---

## ✅ Success Criteria

### MVP Requirements
- ✅ Generate 30-42 questions per material
- ✅ All 6 categories covered
- ✅ Answers include real property values
- ✅ Author voice consistency maintained
- ✅ Technical accuracy validated
- ✅ Materials.yaml persistence working
- ✅ Frontmatter export includes FAQ data

### Quality Metrics
- **Coverage**: 100% of materials have FAQs
- **Completeness**: All required categories present
- **Accuracy**: 100% of values traceable to source data
- **Voice**: 95%+ author authenticity score
- **Utility**: User feedback shows FAQs answer real questions

---

**Status**: ✅ Requirements Complete - Ready for Implementation  
**Complexity**: High (Multi-category, 30-42 questions, extensive material integration)  
**Estimated Implementation**: 2-3 days  
**Dependencies**: Voice service, Materials.yaml, Categories.yaml

---

## 🔧 Implementation Checklist

### Setup
- [ ] Create `components/faq/` directory structure
- [ ] Create FAQ generator class following Caption pattern
- [ ] Create Voice template `technical_faq_answer`
- [ ] Create question generation logic for each category

### Core Generation
- [ ] Implement material analysis for FAQ customization
- [ ] Implement question generation per category
- [ ] Implement answer generation via Voice service (multiple calls)
- [ ] Implement validation (word counts, technical accuracy, completeness)

### Data Integration
- [ ] Pull property values from Materials.yaml
- [ ] Pull category ranges from Categories.yaml
- [ ] Pull applications for context
- [ ] Include machineSettings in relevant answers

### Persistence
- [ ] Implement Materials.yaml write-back
- [ ] Implement frontmatter export format
- [ ] Add metadata (generation timestamp, word counts, etc.)

### Testing
- [ ] Test with each material category (metal, ceramic, stone, etc.)
- [ ] Validate all 6 FAQ categories generate
- [ ] Verify author voice consistency
- [ ] Confirm technical values accuracy
- [ ] Test frontmatter export

### Documentation
- [ ] Create ARCHITECTURE.md (like Caption)
- [ ] Document Voice template usage
- [ ] Add usage examples
- [ ] Update component registry

---

**Document Version**: 1.0  
**Last Updated**: October 26, 2025  
**Next Review**: After MVP implementation
