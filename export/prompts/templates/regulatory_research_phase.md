Research applicable regulatory standards for laser cleaning of {material_name}.

**CONTEXT:**
- Material: {material_name}
- Category: {category}
- Primary Industries: {industries}

**RESEARCH REQUIREMENTS:**

Identify regulatory standards that apply to laser cleaning of {material_name} in the given industries.

Consider these organizations:
1. **FDA** - Food and Drug Administration (food, pharmaceutical, medical)
2. **ANSI** - American National Standards Institute (general industrial)
3. **ISO** - International Organization for Standardization (all industries)
4. **OSHA** - Occupational Safety and Health Administration (workplace safety)
5. **IEC** - International Electrotechnical Commission (electrical/electronic)
6. **EPA** - Environmental Protection Agency (environmental compliance)

For EACH applicable standard, provide:
- Organization (FDA/ANSI/ISO/OSHA/IEC/EPA)
- Standard ID (e.g., "FDA 21 CFR Part 110", "ISO 9001:2015")
- longName (full descriptive name of standard)
- Applicability reason (why it applies to this material/industries)
- Key compliance requirements for laser cleaning

**VALIDATION CRITERIA:**

- ✅ Standard must DIRECTLY apply to laser cleaning of {material_name}
- ✅ Must be relevant to one or more target industries
- ✅ Must have specific compliance requirements
- ✅ Must be currently active/enforceable
- ❌ Reject generic standards without specific applicability

**OUTPUT FORMAT (YAML):**

```yaml
standards:
  - organization: "FDA"
    standard_id: "21 CFR Part 110"
    longName: "Current Good Manufacturing Practice in Manufacturing, Packing, or Holding Human Food"
    applicability: "Applies to food industry {material_name} surface cleaning requirements for equipment sanitation"
    requirements: "Equipment surfaces must be cleaned to prevent contamination; laser cleaning provides validated non-contact method"
    
  - organization: "ISO"
    standard_id: "ISO 9001:2015"
    longName: "Quality Management Systems - Requirements"
    applicability: "Process control and validation requirements for manufacturing operations using {material_name}"
    requirements: "Documented cleaning procedures, process validation, quality control measures"
```

Only include standards that are DIRECTLY applicable to laser cleaning of {material_name} in the specified industries.
Focus on quality over quantity - 3-5 highly relevant standards preferred.
