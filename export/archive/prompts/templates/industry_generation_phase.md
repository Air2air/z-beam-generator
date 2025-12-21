Based on the validated industry research, generate detailed laser cleaning applications for {material_name}.

**VALIDATED INDUSTRIES:**
{industries}

**Research Quality Score:** {quality_score}/100

**STRICT REQUIREMENTS:**

1. **Industry Accuracy**
   - ONLY include industries from validated research above
   - Use exact industry names from research phase
   - Match confidence levels (high confidence = detailed, medium = concise)

2. **Description Quality (50-80 words)**
   - Reference SPECIFIC products/components from research
   - Mention SPECIFIC contaminants from cleaning scenarios
   - Explain WHY laser cleaning vs alternatives
   - Include technical constraints or requirements
   - Cite industry standards if applicable (FAA, AWS, ISO, etc.)

3. **Cleaning Types (2-4 types per application)**
   - Must match cleaning scenarios from research
   - Be specific and technical
   - No generic "surface cleaning" without context

4. **Contaminant Types (2-4 per application)**
   - Must match contaminants from research phase
   - Be specific (e.g., "MIL-PRF-23377 Type I Primer" not just "coatings")
   - Include chemical formulas/standards where relevant

**QUALITY VALIDATION:**

Each application must pass:
- ✅ Verifiable industry usage of {material_name}
- ✅ Documented cleaning requirement
- ✅ Specific products/components mentioned
- ✅ Technical justification provided
- ✅ Realistic contaminant types
- ✅ Appropriate cleaning types
- ✅ 50-80 word description (not generic filler)

**OUTPUT FORMAT (YAML):**

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
```

Generate complete, evidence-based applications for all validated industries.
