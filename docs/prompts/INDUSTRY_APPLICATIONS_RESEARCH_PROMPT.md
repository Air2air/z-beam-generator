# Industry Applications Research Prompt - Rigorous Version

**Purpose**: Generate highly accurate, well-researched industry applications for laser cleaning of specific materials.

**Problem**: Current prompts generate too many applications with insufficient validation, resulting in generic or inaccurate industry assignments.

---

## 🎯 Proposed Prompt Structure

### Research Phase Prompt (New - Pre-Application Generation)

```
You are a materials science and industrial manufacturing expert researching laser cleaning applications for {material_name}.

**RESEARCH METHODOLOGY - STRICT VALIDATION REQUIRED:**

For each potential industry application, you MUST verify ALL of the following criteria:

1. **Material Usage Verification**
   - Is {material_name} actually used in manufacturing/operations within this industry?
   - What specific products or components use this material?
   - Provide evidence (standards, common practices, published data)

2. **Cleaning Necessity Verification**
   - Does this industry actually need to clean {material_name} surfaces?
   - What specific cleaning scenarios exist (maintenance, manufacturing, restoration)?
   - Why would laser cleaning be preferred over chemical/mechanical methods?

3. **Economic Viability Verification**
   - Is laser cleaning cost-effective for this application?
   - What is the volume/scale of this application?
   - Are there existing laser cleaning implementations in this industry?

4. **Technical Feasibility Verification**
   - Can laser cleaning effectively remove the contaminants in this application?
   - Are there material compatibility concerns?
   - What are the technical constraints or requirements?

**RESEARCH QUALITY REQUIREMENTS:**

- ✅ PRIMARY INDUSTRIES (3-5 max): Industries where {material_name} is COMMONLY used
  - Must cite specific products/components
  - Must have documented laser cleaning applications
  - Must show economic significance

- ⚠️ SECONDARY INDUSTRIES (2-3 max): Industries with specialized/niche uses
  - Must have verifiable {material_name} usage
  - May have emerging laser cleaning applications
  - Lower volume but technically valid

- ❌ REJECT: Speculative or unlikely applications
  - No verified {material_name} usage
  - No cleaning requirements
  - No technical or economic justification

**OUTPUT FORMAT:**

For each VALIDATED industry, provide:

```yaml
industry_research:
  - industry: "Exact Industry Name"
    confidence: "high|medium|low"
    material_usage:
      - "Specific product/component 1"
      - "Specific product/component 2"
    cleaning_scenarios:
      - scenario: "Maintenance cleaning"
        frequency: "high|medium|low"
        contaminants: ["Specific type 1", "Specific type 2"]
      - scenario: "Pre-coating preparation"
        frequency: "medium"
        contaminants: ["Oxide layers", "Residues"]
    justification: "Why laser cleaning is appropriate for this material/industry combination (2-3 sentences with specific technical/economic reasons)"
    evidence: "Reference to standard, publication, or industry practice"
```

**MATERIAL CONTEXT:**
- Material: {material_name}
- Category: {category}
- Properties: {key_properties}
- Known Standards: {regulatory_standards}

**VALIDATION CHECKLIST:**
- [ ] Each industry cites specific {material_name} usage
- [ ] Cleaning scenarios are documented/verifiable
- [ ] Technical feasibility is established
- [ ] Economic justification provided
- [ ] Evidence/references included
- [ ] Total industries: 5-8 (not 10+)
- [ ] No generic/speculative entries
```

---

## 📊 Application Generation Prompt (Enhanced)

```
Based on the validated industry research above, generate detailed laser cleaning applications for {material_name}.

**STRICT REQUIREMENTS:**

1. **Industry Accuracy**
   - ONLY include industries from validated research
   - Use exact industry names from research phase
   - Match confidence levels (high confidence = detailed, medium = concise)

2. **Description Quality (50-80 words)**
   - Reference SPECIFIC products/components from research
   - Mention SPECIFIC contaminants from cleaning scenarios
   - Explain WHY laser cleaning vs alternatives
   - Include technical constraints or requirements
   - Cite industry standards if applicable

3. **Cleaning Types (2-4 types per application)**
   - Must match cleaning scenarios from research
   - Use standard Categories.yaml terminology
   - No generic "surface cleaning" without context

4. **Contaminant Types (2-4 per application)**
   - Must match contaminants from research phase
   - Be specific (e.g., "MIL-PRF-23377 Type I Primer" not just "coatings")
   - Include chemical formulas where relevant

**QUALITY VALIDATION:**

Each application must pass:
- ✅ Verifiable industry usage of {material_name}
- ✅ Documented cleaning requirement
- ✅ Specific products/components mentioned
- ✅ Technical justification provided
- ✅ Realistic contaminant types
- ✅ Appropriate cleaning types
- ✅ 50-80 word description (not generic filler)

**OUTPUT FORMAT:**

```yaml
applications:
  - industry: "Aerospace"
    description: "Removal of MIL-PRF-23377 Type I epoxy primer and Alodine 1200 conversion coatings from {material_name} structural components during depot-level maintenance of commercial aircraft. Laser cleaning enables inspection of underlying substrate for fatigue cracks and corrosion without introducing thermal stress that could compromise airworthiness, meeting Boeing D6-17487 and Airbus AIMS 09-00-002 specifications for non-destructive surface preparation."
    cleaningTypes:
      - "Coating Removal"
      - "Conversion Coating Removal"
      - "Pre-Inspection Surface Preparation"
    contaminantTypes:
      - "Epoxy Primers (MIL-PRF-23377)"
      - "Chromate Conversion Coatings (Alodine)"
      - "Hydraulic Fluids (MIL-PRF-83282)"
    confidence: "high"
    evidence: "Boeing D6-17487, Airbus AIMS 09-00-002"
```

**REJECTION CRITERIA:**

Reject applications that:
- ❌ Use vague industry names ("General Manufacturing")
- ❌ Lack specific products/components
- ❌ Have generic descriptions (<50 words or filler content)
- ❌ List unrealistic contaminants
- ❌ Show no verifiable {material_name} usage
- ❌ Duplicate other applications with slight wording changes
```

---

## 🔍 Material-Specific Research Guidelines

### For Metals
**Focus on:**
- Corrosion/oxidation removal (aerospace, marine, infrastructure)
- Coating removal (automotive, aerospace, manufacturing)
- Weld cleaning (shipbuilding, fabrication, pressure vessels)
- Surface preparation (bonding, painting, plating)

**Verify:**
- Alloy specifications (e.g., 6061-T6, 316L stainless)
- Industry standards (ASTM, MIL-SPEC, ASME)
- Coating systems used
- Corrosion products expected

### For Ceramics
**Focus on:**
- Contamination removal (electronics, medical, aerospace)
- Restoration (cultural heritage, art conservation)
- Pre-bonding preparation (manufacturing, assembly)

**Verify:**
- Ceramic composition and grade
- Contamination sources
- Thermal shock sensitivity
- Surface finish requirements

### For Polymers/Composites
**Focus on:**
- Surface activation (bonding, painting)
- Contamination removal (manufacturing, assembly)
- Degradation layer removal (weathering, UV damage)

**Verify:**
- Polymer type and grade
- Thermal damage thresholds
- Bond strength requirements
- Cleaning alternatives and limitations

### For Stone/Masonry
**Focus on:**
- Heritage conservation (monuments, buildings, art)
- Restoration (architecture, infrastructure)
- Graffiti removal (public spaces)

**Verify:**
- Stone type and geological formation
- Historical significance
- Conservation standards (UNESCO, ICOMOS)
- Weathering/degradation patterns

### For Wood
**Focus on:**
- Restoration (furniture, cultural heritage, architecture)
- Surface preparation (coating, finishing)
- Contamination removal (manufacturing, restoration)

**Verify:**
- Wood species and grade
- Historical/cultural context
- Finish systems used
- Fire/char damage scenarios

---

## 📋 Implementation Example

### Current (Too Many, Low Quality)
```yaml
applications:
  - Aerospace
  - Automotive  
  - Electronics Manufacturing
  - Medical Device Manufacturing
  - Marine and Offshore
  - Cultural Heritage
  - Energy Production
  - Food Processing  # Unlikely for most materials
  - Research and Laboratory  # Too generic
  - Industrial Manufacturing  # Too vague
```

### Proposed (Fewer, High Quality)
```yaml
applications:
  - industry: "Aerospace"
    description: "Removal of chromate conversion coatings (MIL-DTL-5541) and epoxy primers (MIL-PRF-23377) from 2024-T3 aluminum aircraft skin panels during C-check maintenance intervals. Laser cleaning preserves base material integrity while exposing subsurface corrosion and fatigue cracks for NDT inspection, meeting FAA AC 43-4B and EASA Part-M requirements without chemical waste streams or thermal distortion."
    cleaningTypes:
      - "Coating Removal"
      - "Conversion Coating Removal"
      - "Pre-Inspection Preparation"
    contaminantTypes:
      - "Chromate Conversion Coatings (Alodine 1200S)"
      - "Epoxy Primers (MIL-PRF-23377)"
      - "Skydrol Hydraulic Fluid"
    confidence: "high"
    evidence: "FAA AC 43-4B, Boeing D6-17487, Industry practice at major MROs"

  - industry: "Automotive Manufacturing"
    description: "Pre-weld surface preparation of aluminum body panels and space frame components in battery electric vehicle (BEV) production. Removes mill scale, forming lubricants, and oxidation to achieve AWS D17.1 weld quality requirements for structural joints. Laser cleaning eliminates VOC emissions from solvent degreasing while maintaining ±0.05mm dimensional tolerances critical for automated robotic welding systems."
    cleaningTypes:
      - "Pre-Weld Preparation"
      - "Oxide Removal"
      - "Lubricant Removal"
    contaminantTypes:
      - "Mill Scale"
      - "Drawing Lubricants (Synthetic Esters)"
      - "Aluminum Oxide (Al₂O₃)"
    confidence: "high"
    evidence: "AWS D17.1, ISO 9606-2, Tesla/Rivian production processes"
```

---

## 🎯 Key Improvements

1. **Research Phase Separation**
   - Validate industries BEFORE generating applications
   - Establish evidence for each industry
   - Reject unverifiable claims early

2. **Quality Over Quantity**
   - Target 5-8 well-researched applications
   - Each backed by specific evidence
   - Realistic and verifiable claims

3. **Specificity Requirements**
   - Named products/components
   - Specific standards and specifications
   - Actual contaminant types with chemistry
   - Real cleaning scenarios

4. **Evidence-Based Approach**
   - Cite industry standards
   - Reference published practices
   - Verify material usage
   - Justify technical choices

5. **Confidence Scoring**
   - High: Documented, common, established practice
   - Medium: Verifiable but niche application
   - Low: Emerging or specialized use (include with caveat)

---

## 📐 Implementation Strategy

### Phase 1: Research (New Step)
1. Input material name, category, properties
2. Run research validation prompt
3. Receive validated industry list with evidence
4. Filter to 5-8 highest confidence industries

### Phase 2: Application Generation (Enhanced)
1. Use validated industries only
2. Generate detailed descriptions with evidence
3. Include specific contaminants and cleaning types
4. Validate against quality checklist

### Phase 3: Quality Review (New Step)
1. Verify each application meets word count (50-80)
2. Check for specific products/components mentioned
3. Validate contaminant types are realistic
4. Ensure no duplicate or generic entries
5. Confirm evidence/standards cited

---

## 💡 Benefits

1. **Accuracy**: Only include industries where material is actually used
2. **Credibility**: Cite specific standards and practices
3. **Usability**: Detailed descriptions help users understand applications
4. **SEO**: Specific product/component names improve search relevance
5. **Trust**: Evidence-based approach builds user confidence
6. **Efficiency**: Fewer, better applications vs many generic ones

---

## ⚠️ Quality Control Metrics

Track and enforce:
- **Average word count**: 60-70 words per description
- **Specificity score**: % of applications with named products
- **Evidence rate**: % of applications citing standards/sources
- **Rejection rate**: % of initial industry candidates rejected
- **Confidence distribution**: >70% high confidence applications

---

**Next Steps:**
1. Test with 5 representative materials
2. Validate against known industry practices
3. Measure quality improvement vs current approach
4. Refine prompt based on results
5. Deploy to production
