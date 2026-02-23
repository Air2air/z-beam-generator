# PROPOSED 3-COMPONENT PROMPT FORMAT

## 🎯 STRUCTURE OVERVIEW

Each prompt file should generate three distinct components:

1. **sectionTitle** - Concise, material-specific title (3-7 words)
2. **sectionDescription** - Brief explanation of section purpose (1-2 sentences)  
3. **sectionContent** - Detailed section content with specific data/examples

---

## 📄 TEMPLATE FORMAT

```
# SECTION: [Section Name]
# PURPOSE: Generate complete section with title, description, and content

## 1. SECTION TITLE GENERATION
Generate a concise, material-specific title (3-7 words) that:
- Identifies THIS specific material/contaminant/compound/setting
- Distinguishes from similar items in the same category  
- Uses active, descriptive language
- Avoids generic terms like "Overview" or "Information"

## 2. SECTION DESCRIPTION GENERATION  
Generate a 1-2 sentence description that:
- Explains what this section covers
- Highlights why it's important for THIS item specifically
- Sets context for the detailed content below
- Uses clear, professional language

## 3. SECTION CONTENT GENERATION
[Detailed content instructions specific to each section type]

## OUTPUT FORMAT
{
  "sectionTitle": "[Generated title]",
  "sectionDescription": "[Generated description]", 
  "sectionContent": "[Detailed content]"
}
```

---

## 🔬 EXAMPLE: healthEffects.txt

```
# SECTION: Health Effects
# PURPOSE: Generate complete health effects section with safety assessment

## 1. SECTION TITLE GENERATION
Generate a title that identifies the specific health risks for THIS material:
- Examples: "Aluminum Inhalation Risks", "Steel Dust Health Concerns"
- Focus on the PRIMARY health concern for this specific material
- Use medical/safety terminology where appropriate

## 2. SECTION DESCRIPTION GENERATION  
Generate description explaining:
- What types of health effects are covered
- Why these effects are specifically important for THIS material
- Brief context about exposure scenarios

## 3. SECTION CONTENT GENERATION
Generate comprehensive health effects content including:

### Risk Assessment Matrix
- Exposure levels (low, moderate, high)
- Routes of exposure (inhalation, dermal, ingestion)
- Severity ratings for each combination

### Target Organ Systems
- Primary affected organs/systems
- Mechanism of action for THIS specific material
- Dose-response relationships

### Health Impact Timeline
- Acute effects (immediate, < 24 hours)
- Short-term effects (24 hours - 2 weeks)
- Chronic effects (> 2 weeks, long-term)

### Safety Recommendations
- Personal protective equipment requirements
- Exposure limits and monitoring
- Medical surveillance recommendations
- Emergency response procedures

## OUTPUT FORMAT
{
  "sectionTitle": "[Material-specific health title]",
  "sectionDescription": "[1-2 sentences about health effects scope]", 
  "sectionContent": "[Detailed health assessment with matrix, organs, timeline, safety]"
}
```

---

## ⚗️ EXAMPLE: applications.txt

```
# SECTION: Applications
# PURPOSE: Generate complete applications section with industry contexts

## 1. SECTION TITLE GENERATION
Generate a title that captures the PRIMARY application domain:
- Examples: "Aerospace Grade Applications", "Industrial Coating Uses"
- Focus on the MOST significant or distinctive application area
- Emphasize what makes THIS material special in applications

## 2. SECTION DESCRIPTION GENERATION  
Generate description explaining:
- What types of applications are covered
- Why THIS material is chosen over alternatives
- Brief context about performance advantages

## 3. SECTION CONTENT GENERATION
Generate comprehensive applications content including:

### Primary Industry Sectors
- Main industries using this material
- Specific products or components
- Market size and importance

### Performance Advantages
- Property-driven benefits
- Comparison to alternative materials
- Cost-effectiveness considerations

### Application Requirements
- Technical specifications needed
- Quality standards and certifications
- Processing/handling requirements

### Emerging Applications
- New or developing uses
- Research and development areas
- Future market potential

## OUTPUT FORMAT
{
  "sectionTitle": "[Material-specific application title]",
  "sectionDescription": "[1-2 sentences about application scope]", 
  "sectionContent": "[Detailed application analysis with industries, advantages, requirements]"
}
```

---

## 🔧 IMPLEMENTATION BENEFITS

✅ **Complete Section Generation** - Single prompt produces all needed components
✅ **Consistent Structure** - Standardized format across all sections
✅ **Rich Content** - Detailed, specific information beyond basic descriptions
✅ **JSON Output** - Machine-readable format for easy parsing
✅ **Material-Specific** - Tailored content for each item, not generic templates