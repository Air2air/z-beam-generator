# Z-Beam Hybrid Architecture Specification

**Date:** September 1, 2025
**Status:** ACTIVE SPECIFICATION
**Version:** 1.0

## 🏗️ Architecture Overview

The Z-Beam generator implements a **hybrid architecture** where API-based components have standard access to frontmatter data for enhanced context and consistency.

## 📋 Component Categories

### **Category 1: Hybrid Components (API + Frontmatter)**
These components use AI APIs for intelligent generation while requiring frontmatter data for context:

| Component | API Provider | Data Provider | Frontmatter Access | Purpose |
|-----------|--------------|---------------|-------------------|---------|
| `frontmatter` | `deepseek` | `hybrid` | ❌ (source) | Primary material data source + provides data |
| `text` | `deepseek` | `hybrid` | ✅ | AI-generated articles with material context |
| `bullets` | `deepseek` | `hybrid` | ✅ | AI-generated bullet points with technical accuracy |
| `caption` | `deepseek` | `hybrid` | ✅ | AI-generated captions with material specifics |
| `tags` | `deepseek` | `hybrid` | ✅ | AI-generated tags with material context |
| `metatags` | `deepseek` | `hybrid` | ✅ | AI-generated meta tags with material context |
| `propertiestable` | `deepseek` | `hybrid` | ✅ | AI-generated property tables with material data |

### **Category 2: Frontmatter-Dependent Components (Schema-Driven)**
These components extract and transform data directly from frontmatter:

| Component | API Provider | Data Provider | Purpose |
|-----------|--------------|---------------|---------|
| `jsonld` | `none` | `frontmatter` | Schema.org structured data extraction |
| `badgesymbol` | `none` | `frontmatter` | Material badges from frontmatter data |

### **Category 3: Static Components**
These components use static data without API or frontmatter dependencies:

| Component | API Provider | Data Provider | Purpose |
|-----------|--------------|---------------|---------|
| `table` | `none` | `static` | Technical tables (static generation) |
| `author` | `none` | `static` | Static author profiles from authors.json |

## 🔄 Standard API Component Interface

### **Required Method Signature**
```python
def generate(self, material_name: str, material_data: Dict,
            api_client, author_info: Optional[Dict] = None,
            frontmatter_data: Optional[Dict] = None,  # REQUIRED for all API components
            schema_fields: Optional[Dict] = None) -> ComponentResult:
```

### **Frontmatter Data Structure**
```python
frontmatter_data = {
    'title': str,
    'description': str,
    'category': str,
    'chemical_formula': str,
    'properties': {
        'density': str,
        'melting_point': str,
        'thermal_conductivity': str,
        # ... other properties
    },
    'laser_cleaning': {
        'wavelength': str,
        'pulse_duration': str,
        'fluence_range': str,
        # ... laser parameters
    },
    'applications': List[str],
    'contaminants': List[str],
    # ... additional frontmatter fields
}
```

## 🎯 Implementation Benefits

### **For API-Based Components:**
1. **Enhanced Context**: Rich material data improves AI generation accuracy
2. **Technical Consistency**: All components reference same technical specifications
3. **Quality Assurance**: Frontmatter data validates and enhances AI output
4. **Semantic Coherence**: Components share common technical vocabulary

### **For System Architecture:**
1. **Data Flow Clarity**: Clear dependency hierarchy (frontmatter → API components)
2. **Consistency Guarantee**: Single source of truth for material properties
3. **Error Reduction**: Frontmatter validation prevents inconsistent data
4. **Maintainability**: Standardized interface across all API components

## 🔧 Implementation Requirements

### **Generation Orchestration Order**
```yaml
orchestration_order:
  1. frontmatter      # MUST BE FIRST - provides data for all other components
  2. propertiestable  # Depends on frontmatter data
  3. badgesymbol      # Depends on frontmatter data
  4. author           # Static component, no dependencies
  5. text             # AI + frontmatter context
  6. bullets          # AI + frontmatter context
  7. caption          # AI + frontmatter context
  8. table            # AI + frontmatter context
  9. tags             # AI + frontmatter context
  10. metatags        # Extract from frontmatter
  11. jsonld          # Extract from frontmatter (LAST)
```

### **Component Configuration**
```yaml
components:
  # Hybrid components (API + frontmatter data)
  frontmatter:    {enabled: true, api_provider: "deepseek", data_provider: "hybrid"}
  text:           {enabled: true, api_provider: "deepseek", data_provider: "hybrid"}
  bullets:        {enabled: true, api_provider: "deepseek", data_provider: "hybrid"}
  caption:        {enabled: true, api_provider: "deepseek", data_provider: "hybrid"}
  tags:           {enabled: true, api_provider: "deepseek", data_provider: "hybrid"}
  metatags:       {enabled: true, api_provider: "deepseek", data_provider: "hybrid"}
  propertiestable: {enabled: true, api_provider: "deepseek", data_provider: "hybrid"}

  # Frontmatter-dependent components (pure extraction)
  jsonld:         {enabled: true, api_provider: "none", data_provider: "frontmatter"}
  badgesymbol:    {enabled: true, api_provider: "none", data_provider: "frontmatter"}

  # Static components (no dependencies)
  table:          {enabled: true, api_provider: "none", data_provider: "static"}
  author:         {enabled: true, api_provider: "none", data_provider: "static"}
```

> **Note**: "hybrid" data_provider indicates components that require BOTH frontmatter data AND AI API calls. This is different from "API" (AI-only) and "static" (no dependencies).

## 🧪 Validation Requirements

### **API Component Requirements**
- ✅ Must accept `frontmatter_data` parameter
- ✅ Must validate frontmatter data structure
- ✅ Must use frontmatter data to enhance AI generation
- ✅ Must handle missing/incomplete frontmatter gracefully

### **Integration Testing**
- ✅ Test frontmatter data flow to all API components
- ✅ Verify enhanced generation quality with frontmatter context
- ✅ Validate consistency across components using same frontmatter
- ✅ Test graceful degradation with missing frontmatter data

## 🎉 Expected Outcomes

### **Quality Improvements**
- **Technical Accuracy**: AI generation enhanced with real material data
- **Consistency**: All components reference same technical specifications
- **Coherence**: Shared vocabulary and technical context
- **Reliability**: Frontmatter validation prevents data inconsistencies

### **System Benefits**
- **Clear Data Flow**: Frontmatter → API components → derived components
- **Standardized Interface**: All API components follow same pattern
- **Enhanced Testing**: Frontmatter data provides testable inputs
- **Future Extensibility**: Standard pattern for new API components

This hybrid architecture ensures all API-based components can leverage rich frontmatter context while maintaining clear separation between AI generation and data extraction components.
