# Table Component - Complete Reference

## 🎯 Overview
The Table component generates deterministic technical data tables containing exact specifications and properties for materials used in laser cleaning applications. Uses fail-fast architecture with no fallbacks or randomization.

## 📋 Component Requirements

### **Functional Requirements**
- Generate deterministic technical data tables following exact example format
- Include material specifications, laser parameters, and performance characteristics
- Support markdown table format only (no HTML or other formats)
- Ensure data accuracy and consistency across materials
- Provide tables suitable for technical documentation and industrial use
- **FAIL-FAST**: No fallbacks, defaults, or randomization allowed

### **Technical Requirements**
- **Type**: Static deterministic component
- **API Provider**: None (static generation)
- **AI Detection**: Disabled (deterministic data generation)
- **Priority**: 7 (later in generation pipeline)
- **Dependencies**: Frontmatter (for material context and properties)
- **Architecture**: Fail-fast with immediate validation

### **Input Requirements**
```python
Required Inputs:
- material_name: str (e.g., "copper", "steel", "aluminum")
- material_data: Dict containing:
  - name: str
  - properties: Dict (optional, uses defaults if missing)
  - specifications: Dict (optional)
- No API client required (static generation)
```

### **Output Requirements**
```python
Output Format: ComponentResult with:
- content: str (markdown table format - exact same output every time)
- success: bool
- metadata: Dict containing:
  - row_count: int (exact count per table type)
  - column_count: int (always 3)
  - data_categories: List[str] (fixed categories)
```

## 🏗️ Architecture & Implementation

### **Core Classes**
```python
class TableComponentGenerator(ComponentGenerator):
    """Generates deterministic technical data tables - FAIL-FAST: No fallbacks"""
    
    def get_component_type(self) -> str:
        return "table"
    
    def generate(self, **kwargs) -> ComponentResult:
        """Main generation method with strict validation and immediate failure"""
```

### **Generation Process**
1. **Input Validation**: Verify material data exists - FAIL IMMEDIATELY if missing
2. **Data Extraction**: Use exact material properties from database or fail
3. **Table Structure Creation**: Generate exact tables following example format
4. **Content Assembly**: Combine tables in fixed order with no variation
5. **Format Validation**: Ensure markdown syntax is perfect
6. **Output**: Return identical content for same inputs

### **Table Structure**
```markdown
| Property | Value | Unit |
|----------|-------|------|
| Density | 8.96 | g/cm³ |
| Melting Point | 1085 | °C |
| Thermal Conductivity | 401 | W/(m·K) |
```

## 📊 Data Flow & Dependencies

### **Input Data Flow**
```
Material Name + Data → Validation → Exact Table Generation → Formatted Output
```

### **Dependency Chain**
1. **Frontmatter Component** (Priority 1): Provides material properties and specifications
2. **Table Component** (Priority 7): Uses frontmatter data to generate deterministic tables

### **Error Handling - FAIL-FAST**
- **Missing Material Data**: Immediate failure with clear error message
- **Invalid Material Type**: No fallback to generic data - fail immediately
- **Incomplete Properties**: No defaults or approximations - fail immediately
- **No Retry Logic**: Single attempt only, fail-fast on any issue

## 🔧 Configuration

### **Component Configuration**
```yaml
# In COMPONENT_CONFIG
table:
  generator: "table"
  api_provider: "none"  # Static generation
  priority: 7
  required: true
  ai_detection: false
  fail_fast: true  # No fallbacks allowed
```

### **Table Configuration**
```yaml
# components/table/config.yaml
table_structure:
  columns: 3  # Fixed: Property | Value | Unit
  tables:
    - material_properties: 8  # Exact row count
    - grades: 4
    - performance: 4
    - standards: 4
    - environmental: 4
    - laser_parameters: 6
  deterministic: true  # Always same output
  fail_fast: true  # No fallbacks
```

### **Material Database**
```python
# Static material properties - no API required
material_properties = {
    "copper": {
        "density": "8.96 g/cm³",
        "melting_point": "1085°C",
        "thermal_conductivity": "401 W/(m·K)",
        # ... exact values for deterministic generation
    }
}
```

## 📝 Usage Examples

### **Basic Usage**
```python
from components.table.generators.generator import TableComponentGenerator

generator = TableComponentGenerator()
result = generator.generate(
    material_name="copper",
    material_data={
        "name": "Copper",
        "properties": {}  # Optional - uses exact defaults
    }
    # No API client needed for static generation
)

if result.success:
    print(result.content)  # Always identical markdown tables
    print(f"Table dimensions: {result.metadata['row_count']}x{result.metadata['column_count']}")
else:
    print(f"FAIL-FAST: {result.error_message}")  # Immediate failure with clear message
```

### **Integration with Dynamic Generator**
```python
from generators.dynamic_generator import DynamicGenerator

generator = DynamicGenerator()

# Generate frontmatter first (provides material data)
frontmatter_result = generator.generate_component("copper", "frontmatter")

# Generate deterministic table using exact format
table_result = generator.generate_component("copper", "table")

# Process results - always identical output
if table_result.success:
    table_content = table_result.content
    # Content is always exactly the same for same material
    # No variation or randomization
```

## 🧪 Testing & Validation

### **Unit Tests**
```python
# components/table/testing/test_table.py
class TestTableComponentGenerator:
    
    def test_deterministic_generation(self):
        """Test deterministic table generation - same input = same output"""
        generator = TableComponentGenerator()
        
        # Generate twice with same input
        result1 = generator.generate(material_name="copper", material_data={})
        result2 = generator.generate(material_name="copper", material_data={})
        
        assert result1.success is True
        assert result2.success is True
        assert result1.content == result2.content  # Must be identical
        assert "| Property |" in result1.content
        assert result1.metadata['row_count'] == 30  # Exact count: 8+4+4+4+4+6
    
    def test_fail_fast_on_missing_material(self):
        """Test fail-fast behavior for missing material data"""
        generator = TableComponentGenerator()
        
        result = generator.generate(material_name="", material_data={})
        
        assert result.success is False
        assert "Material name is required" in result.error_message
    
    def test_exact_table_structure(self):
        """Test tables follow exact example format"""
        generator = TableComponentGenerator()
        result = generator.generate(material_name="copper", material_data={})
        
        content = result.content
        
        # Must contain exact table headers in order
        assert "## Material Properties" in content
        assert "## Material Grades and Purity" in content
        assert "## Performance Metrics" in content
        assert "## Standards and Compliance" in content
        assert "## Environmental Data" in content
        assert "## Laser Cleaning Parameters" in content
        
        # Must have exact row counts
        lines = content.split('\n')
        table_lines = [line for line in lines if line.startswith('|')]
        assert len(table_lines) == 36  # 6 headers + 6 separators + 24 data rows
```

### **Integration Tests**
- **Deterministic Output Validation**: Verify identical output across multiple runs
- **Material Coverage**: Test all supported materials (copper, steel, aluminum)
- **Format Consistency**: Ensure perfect markdown table syntax
- **Fail-Fast Validation**: Confirm immediate failure on invalid inputs

### **Mock Implementation - REMOVED**
```python
# Mock implementation removed - no fallbacks allowed in fail-fast architecture
# All tests use real deterministic generation or fail immediately
```

## 📈 Performance & Quality Metrics

### **Performance Targets**
- **Generation Time**: < 1 second per material (static generation)
- **API Calls**: 0 calls per material (no external dependencies)
- **Success Rate**: 100% for valid inputs, 0% for invalid (fail-fast)
- **Table Size**: Exact 30 rows with 3 columns (6 tables × ~5 rows each)

### **Quality Metrics**
- **Deterministic Accuracy**: 100% identical output for same inputs
- **Technical Accuracy**: 100% of data must be technically correct
- **Completeness Score**: 100% of required properties included (no variation)
- **Format Consistency**: 100% perfect markdown table formatting
- **Fail-Fast Reliability**: 100% immediate failure on invalid inputs

### **Monitoring**
- **Generation Consistency**: Verify identical outputs across runs
- **Data Quality**: Static validation of material property databases
- **Format Compliance**: Automated markdown syntax validation
- **Fail-Fast Effectiveness**: Track immediate failure on invalid inputs

## 🔄 Maintenance & Updates

### **Regular Maintenance**
- **Weekly**: Validate deterministic output consistency
- **Monthly**: Review material property databases for accuracy
- **Quarterly**: Verify fail-fast behavior with invalid inputs

### **Update Procedures**
1. **Data Updates**: Modify exact material property values in database
2. **Table Structure**: Update extraction methods for new properties
3. **Technical Standards**: Refresh specifications to current standards
4. **Validation**: Update tests to match new deterministic outputs

### **Version History**
- **v1.0.0**: Initial implementation with basic table generation
- **v1.1.0**: Enhanced technical accuracy and property coverage
- **v1.2.0**: Improved table formatting and data validation
- **v2.0.0**: Complete rewrite for deterministic generation and fail-fast architecture

## 🚨 Error Handling & Troubleshooting

### **Common Issues - FAIL-FAST**
1. **Missing Material Name**
   - **Symptom**: Immediate failure with "Material name is required"
   - **Solution**: Provide valid material name
   - **Prevention**: Validate inputs before generation

2. **Unsupported Material Type**
   - **Symptom**: Immediate failure with "No properties found for material"
   - **Solution**: Use supported materials (copper, steel, aluminum)
   - **Prevention**: Check material support before generation

3. **Incomplete Material Data**
   - **Symptom**: Immediate failure with specific missing data error
   - **Solution**: Provide complete material specifications
   - **Prevention**: Validate data completeness upfront

### **Debug Information**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check component state
generator = TableComponentGenerator()
print(f"Component type: {generator.get_component_type()}")

# Test deterministic generation
result1 = generator.generate(material_name="copper", material_data={})
result2 = generator.generate(material_name="copper", material_data={})
print(f"Outputs identical: {result1.content == result2.content}")

# Validate table structure
lines = result1.content.split('\n')
table_count = result1.content.count('## ')  # Should be 6
print(f"Generated {table_count} tables as expected")
```

## 📚 Related Documentation

### **Component References**
- **[Frontmatter Component](../frontmatter/README.md)**: Required dependency providing material data
- **[Component Standards](../../COMPONENT_STANDARDS.md)**: Overall component development standards
- **[Generator Base](../../components/generator_base.md)**: Base class implementation patterns

### **System Documentation**
- **[Fail-Fast Architecture](../../docs/FAIL_FAST_ARCHITECTURE.md)**: Fail-fast design principles
- **[Deterministic Generation](../../docs/DETERMINISTIC_GENERATION.md)**: Deterministic output standards
- **[Testing Patterns](../../testing/component_testing.md)**: Component testing approaches

## ✅ Validation Checklist

### **Pre-Generation Validation**
- [ ] Material name provided and valid (copper, steel, aluminum)
- [ ] Material data dictionary exists (can be empty for defaults)
- [ ] No API client required (static generation)
- [ ] Component follows fail-fast architecture (no fallbacks)

### **Post-Generation Validation**
- [ ] Generated content is identical markdown tables every time
- [ ] Table has exact 30 rows (6 tables × 5 rows each)
- [ ] All 6 required table types are present in correct order
- [ ] Data is technically accurate and matches material specifications
- [ ] Markdown table syntax is perfect with proper alignment
- [ ] No malformed or missing data entries

### **Integration Validation**
- [ ] Component integrates properly with dynamic generator
- [ ] Dependencies are correctly specified and enforced
- [ ] Fail-fast behavior works as expected (immediate failure)
- [ ] Deterministic output verified across multiple runs

---

## 📞 Support & Contact

**Component Owner**: Table Component Team
**Last Updated**: September 8, 2025
**Version**: 2.0.0
**Status**: 🟢 Production Ready - Deterministic Generation

For issues or questions about the Table component:
1. Check this documentation first
2. Review the test suite for deterministic behavior examples
3. Check system logs for fail-fast error details
4. Contact the development team for support

**Critical Notes:**
- This component uses fail-fast architecture - no fallbacks allowed
- Output is always deterministic - same input produces identical tables
- No API dependencies - static generation only
- Immediate failure on any validation error</content>
<parameter name="filePath">/Users/todddunning/Desktop/Z-Beam/z-beam-generator/components/table/README.md
