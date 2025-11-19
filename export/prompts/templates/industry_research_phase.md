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
- Key Properties:
{properties}

**VALIDATION CHECKLIST:**
- [ ] Each industry cites specific {material_name} usage
- [ ] Cleaning scenarios are documented/verifiable
- [ ] Technical feasibility is established
- [ ] Economic justification provided
- [ ] Evidence/references included
- [ ] Total industries: 5-8 (not 10+)
- [ ] No generic/speculative entries
