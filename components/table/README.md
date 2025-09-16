# Table Component - Frontmatter-Based YAML Generator

## 🎯 Overview
The Table component generates deterministic YAML table structures from frontmatter data containing material properties. Uses fail-fast architecture with no API calls needed - processes frontmatter directly to create Next.js-optimized table data.

## 📋 Component Requirements

### **Functional Requirements**
- Generate deterministic YAML table structures from frontmatter properties data
- Group properties into logical categories (Physical, Thermal, Mechanical, Optical, Laser Parameters)
- Include HTML visualization snippets for Next.js rendering with Tailwind CSS
- Support min/max ranges with percentile calculations and progress bars
- Provide tables suitable for technical documentation and industrial use
- **FAIL-FAST**: No API calls, no fallbacks - requires valid frontmatter data

### **Technical Requirements**
- **Type**: Frontmatter-based deterministic component  
- **API Provider**: None (processes frontmatter directly)
- **AI Detection**: Disabled (deterministic data processing)
- **Priority**: 7 (after frontmatter generation)
- **Dependencies**: Frontmatter component (required for properties data)
- **Architecture**: Fail-fast with immediate validation

### **Input Requirements**
```python
Required Inputs:
- material_name: str (e.g., "Alumina", "Copper", "Steel")
- frontmatter_data: Dict containing:
  - properties: Dict with material properties (density, meltingPoint, etc.)
  - chemicalProperties: Dict (optional, for composition)
- No API client required (frontmatter processing only)
```

### **Output Requirements**
```python
Output Format: ComponentResult with:
- content: str (YAML format for Next.js consumption)
- success: bool
- metadata: Dict containing:
  - tables_generated: int
  - properties_processed: int
  - data_source: "frontmatter"
```
```

## 🏗️ Architecture & Implementation

### **Core Classes**
```python
class TableComponentGenerator(ComponentGenerator):
    """Generates YAML tables from frontmatter data - FAIL-FAST: No API calls"""
    
    def get_component_type(self) -> str:
        return "table"
    
    def generate(self, **kwargs) -> ComponentResult:
        """Main generation method processing frontmatter properties"""
```

### **Generation Process**
1. **Input Validation**: Verify frontmatter data exists - FAIL IMMEDIATELY if missing
2. **Property Extraction**: Extract properties from frontmatter data or fail
3. **Category Grouping**: Group properties into logical categories (Physical, Thermal, etc.)
4. **YAML Generation**: Create structured YAML with HTML visualizations
5. **Validation**: Ensure YAML syntax and structure is perfect
6. **Output**: Return deterministic YAML content for Next.js

### **YAML Structure**
```yaml
materialTables:
  tables:
    - header: "## Physical Properties"
      rows:
        - property: "Density"
          value: "8.96 g/cm³"
          min: "0.9"
          max: "22"
          percentile: 85.0
          unit: "g/cm³"
          htmlVisualization: "<div class=\"w-full bg-gray-200 rounded-full h-2\">..."
```

### **Property Categories**
- **Physical Properties**: density, meltingPoint
- **Thermal Properties**: thermalConductivity, thermalDiffusivity, thermalExpansion, specificHeat  
- **Mechanical Properties**: tensileStrength, hardness, youngsModulus
- **Optical Properties**: laserAbsorption, laserReflectivity
- **Laser Processing Parameters**: laserType, wavelength, fluenceRange
- **Composition**: chemicalFormula (if present)

## 📊 Data Flow & Dependencies

### **Input Data Flow**
```
Frontmatter Data → Property Extraction → Category Grouping → YAML Generation → Next.js Tables
```

### **Dependency Chain**
1. **Frontmatter Component** (Priority 1): Provides complete material properties data
2. **Table Component** (Priority 7): Processes frontmatter to generate YAML tables

### **Error Handling - FAIL-FAST**
- **Missing Frontmatter Data**: Immediate failure with clear error message
- **No Properties Section**: Fail immediately - "No table-appropriate data"
- **Invalid Property Format**: No defaults or approximations - fail immediately
- **No Retry Logic**: Single attempt only, fail-fast on any issue

## 🔧 Configuration

### **Component Configuration**
```yaml
# In COMPONENT_CONFIG
table:
  generator: "table"
  api_provider: "none"  # Frontmatter processing
  priority: 7
  required: true
  ai_detection: false
  fail_fast: true  # No fallbacks allowed
```

### **Property Mapping**
```yaml
# Property categories for grouping
categories:
  physical: ["density", "meltingPoint"]
  thermal: ["thermalConductivity", "thermalDiffusivity", "thermalExpansion", "specificHeat"]
  mechanical: ["tensileStrength", "hardness", "youngsModulus"] 
  optical: ["laserAbsorption", "laserReflectivity"]
  laser: ["laserType", "wavelength", "fluenceRange"]
  composition: ["chemicalFormula"]
```

## 📝 Usage Examples

### **Basic Usage**
```python
from components.table.generators.generator import TableComponentGenerator

generator = TableComponentGenerator()

# Frontmatter data from previous component
frontmatter_data = {
    'properties': {
        'density': '8.96 g/cm³',
        'densityMin': '0.9 g/cm³',
        'densityMax': '22 g/cm³', 
        'densityPercentile': 85.0,
        'meltingPoint': '1085°C',
        'thermalConductivity': '401 W/m·K',
        'tensileStrength': '210 MPa',
        'laserType': 'Pulsed Fiber Laser',
        'wavelength': '1064nm',
        'fluenceRange': '0.5-5 J/cm²'
    },
    'chemicalProperties': {
        'formula': 'Cu'
    }
}

result = generator.generate(
    material_name="Copper",
    material_data={"name": "Copper"},
    frontmatter_data=frontmatter_data
)

if result.success:
    yaml_content = result.content  # YAML structure for Next.js
    print(f"Generated {result.metadata['tables_generated']} tables")
    print(f"Processed {result.metadata['properties_processed']} properties")
else:
    print(f"FAIL-FAST: {result.error_message}")
```

### **Integration with Dynamic Generator** 
```python
from generators.dynamic_generator import DynamicGenerator

generator = DynamicGenerator()

# Generate frontmatter first (provides properties data)
frontmatter_result = generator.generate_component("Copper", "frontmatter")

# Extract frontmatter data for table processing
if frontmatter_result.success:
    frontmatter_data = frontmatter_result.metadata.get('frontmatter_data')
    
    # Generate YAML tables from frontmatter properties
    table_result = generator.generate_component(
        "Copper", 
        "table",
        frontmatter_data=frontmatter_data
    )
    
    if table_result.success:
        yaml_tables = table_result.content
        # Use in Next.js application for rendering
```

### **Next.js Integration**
```javascript
// In Next.js component
import yaml from 'js-yaml';
import tableYaml from './copper-tables.yaml';

const TableComponent = () => {
  const tableData = yaml.load(tableYaml);
  
  return (
    <div>
      {tableData.materialTables.tables.map((table, index) => (
        <div key={index}>
          <h2>{table.header.replace('## ', '')}</h2>
          <table className="min-w-full">
            <thead>
              <tr>
                <th>Property</th>
                <th>Value</th>
                <th>Range</th>
                <th>Percentile</th>
                <th>Visualization</th>
              </tr>
            </thead>
            <tbody>
              {table.rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  <td>{row.property}</td>
                  <td>{row.value} {row.unit}</td>
                  <td>{row.min && row.max ? `${row.min}-${row.max}` : '-'}</td>
                  <td>{row.percentile ? `${row.percentile}%` : 'N/A'}</td>
                  <td dangerouslySetInnerHTML={{ __html: row.htmlVisualization }} />
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
};
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
