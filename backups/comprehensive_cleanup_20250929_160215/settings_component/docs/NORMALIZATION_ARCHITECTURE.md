# Settings Component Normalization Architecture

## Overview

The Settings Component underwent comprehensive normalization in September 2025 to provide a standardized 4-section YAML structure across all 109 materials. This architecture ensures consistency, completeness, and maintainability of laser cleaning machine settings data.

## Normalization Principles

### 1. Mandatory 4-Section Structure

Every settings file must contain exactly 4 sections regardless of available data:

```yaml
machineSettings:
  settings:
  - header: '## Machine Configuration'
    rows: [...]
  - header: '## Processing Parameters'
    rows: [...]
  - header: '## Safety Parameters'
    rows: [...]
  - header: '## Quality Control Settings'
    rows: [...]
```

### 2. Standardized Section Headers

Section headers are fixed and cannot vary:
- `'## Machine Configuration'`
- `'## Processing Parameters'`
- `'## Safety Parameters'`
- `'## Quality Control Settings'`

### 3. Required Parameters Per Section

Each section has exactly 4 required parameters:

#### Machine Configuration
1. **Power Range** (category: Laser Power)
2. **Wavelength** (category: Optical)
3. **Pulse Duration** (category: Temporal)
4. **Repetition Rate** (category: Timing)

#### Processing Parameters
1. **Fluence Range** (category: Energy Density)
2. **Spot Size** (category: Beam Geometry)
3. **Scanning Speed** (category: Motion Control)
4. **Working Distance** (category: Positioning)

#### Safety Parameters
1. **Safety Class** (category: Laser Safety)
2. **Beam Enclosure** (category: Safety Equipment)
3. **Ventilation Rate** (category: Environmental Safety)
4. **Emergency Stop** (category: Safety Controls)

#### Quality Control Settings
1. **Surface Roughness Target** (category: Surface Quality)
2. **Cleaning Depth Control** (category: Material Removal)
3. **Process Monitoring** (category: Quality Assurance)
4. **Repeatability** (category: Process Control)

## Implementation Architecture

### Generator Design Pattern

```python
class SettingsComponentGenerator:
    def _generate_static_content(self, material: str, material_data: Dict, frontmatter_data: Dict = None) -> str:
        """Main generation method using 4-section structure"""
        
        # 1. Extract machine settings from frontmatter
        machine_settings = frontmatter_data.get('machineSettings', {})
        
        # 2. Generate all 4 sections (mandatory)
        laser_settings = self._extract_laser_settings(machine_settings)
        processing_settings = self._extract_processing_settings(machine_settings)
        safety_settings = self._extract_safety_settings(machine_settings)
        quality_settings = self._extract_quality_settings(machine_settings)
        
        # 3. Build normalized structure
        structure = {
            'machineSettings': {
                'settings': [
                    {'header': '## Machine Configuration', 'rows': laser_settings},
                    {'header': '## Processing Parameters', 'rows': processing_settings},
                    {'header': '## Safety Parameters', 'rows': safety_settings},
                    {'header': '## Quality Control Settings', 'rows': quality_settings}
                ]
            }
        }
        
        return yaml.dump(structure, default_flow_style=False, sort_keys=False)
```

### Field Mapping Strategy

The generator handles multiple field name variations:

```python
def _extract_laser_settings(self, machine_settings: Dict) -> list:
    # Handle multiple field name formats
    power_range = (
        machine_settings.get("powerRange") or      # camelCase
        machine_settings.get("power_range") or     # snake_case
        "20-100W"  # fallback default
    )
    
    wavelength = (
        machine_settings.get("wavelength") or
        machine_settings.get("wavelength_optimal") or  # alternative name
        "1064nm (primary), 532nm (optional)"  # fallback
    )
```

### Range Construction Logic

```python
def _build_range(self, machine_settings: Dict, base_key: str, default_range: str) -> str:
    """Build range string from min/max values or use default"""
    min_key = f"{base_key}Min"
    max_key = f"{base_key}Max"
    
    min_val = machine_settings.get(min_key, "")
    max_val = machine_settings.get(max_key, "")
    
    if min_val and max_val:
        return f"{min_val} - {max_val}"
    elif min_val:
        return f"{min_val} - TBD"
    elif max_val:
        return f"TBD - {max_val}"
    else:
        return default_range
```

## Fallback Value System

### Design Philosophy

When frontmatter data is incomplete, the generator provides reasonable fallback values rather than failing. This ensures all 109 materials have complete settings regardless of data availability.

### Fallback Values by Section

#### Machine Configuration
- **Power Range**: "20-100W" (range: "20W - 500W")
- **Wavelength**: "1064nm (primary), 532nm (optional)" (range: "355nm - 2940nm")
- **Pulse Duration**: "10-100ns" (range: "1ns - 1000ns")
- **Repetition Rate**: "20-100kHz" (range: "1kHz - 1000kHz")

#### Processing Parameters
- **Fluence Range**: "0.5-5.0 J/cm²" (range: "0.1J/cm² - 50J/cm²")
- **Spot Size**: "0.1-2.0mm" (range: "0.01mm - 10mm")
- **Scanning Speed**: "50-200mm/s" (range: "10mm/s - 1000mm/s")
- **Working Distance**: "100-300mm" (range: "50mm - 500mm")

#### Safety Parameters
- **Safety Class**: "Class 4" (range: "Class 1 - Class 4")
- **Beam Enclosure**: "Required" (range: "Required - Optional")
- **Ventilation Rate**: "200-500 CFM" (range: "100CFM - 1000CFM")
- **Emergency Stop**: "Required" (range: "Required - Required")

#### Quality Control Settings
- **Surface Roughness Target**: "Ra 0.1-0.5μm" (range: "Ra 0.05μm - Ra 2.0μm")
- **Cleaning Depth Control**: "1-10μm" (range: "0.1μm - 50μm")
- **Process Monitoring**: "Real-time optical" (range: "Manual - Real-time")
- **Repeatability**: "±5%" (range: "±1% - ±10%")

## Data Flow Architecture

### Input Processing

```mermaid
graph LR
    A[Frontmatter Data] --> B[Field Mapping]
    B --> C[Value Extraction]
    C --> D[Range Construction]
    D --> E[Fallback Application]
    E --> F[4-Section Structure]
    F --> G[YAML Output]
```

### Error Handling Strategy

1. **Missing Frontmatter**: Use all fallback values
2. **Missing machineSettings**: Use all fallback values
3. **Partial Data**: Use available data + fallbacks for missing fields
4. **Invalid Data**: Log warning, use fallback values
5. **Range Construction Failure**: Use default ranges

## Validation Architecture

### Structural Validation

```python
def validate_normalized_structure(parsed_yaml: Dict) -> bool:
    """Validate normalized 4-section structure"""
    
    # 1. Root structure validation
    if 'machineSettings' not in parsed_yaml:
        return False
        
    if 'settings' not in parsed_yaml['machineSettings']:
        return False
    
    settings = parsed_yaml['machineSettings']['settings']
    
    # 2. Section count validation
    if len(settings) != 4:
        return False
    
    # 3. Header validation
    expected_headers = [
        '## Machine Configuration',
        '## Processing Parameters',
        '## Safety Parameters',
        '## Quality Control Settings'
    ]
    
    actual_headers = [section['header'] for section in settings]
    if actual_headers != expected_headers:
        return False
    
    # 4. Row structure validation
    for section in settings:
        if 'rows' not in section:
            return False
            
        if len(section['rows']) != 4:
            return False
            
        for row in section['rows']:
            required_fields = ['parameter', 'value', 'range', 'category']
            if not all(field in row for field in required_fields):
                return False
    
    return True
```

### Parameter Validation

```python
def validate_section_parameters(section_header: str, rows: List[Dict]) -> bool:
    """Validate parameters for specific section"""
    
    parameter_requirements = {
        '## Machine Configuration': [
            'Power Range', 'Wavelength', 'Pulse Duration', 'Repetition Rate'
        ],
        '## Processing Parameters': [
            'Fluence Range', 'Spot Size', 'Scanning Speed', 'Working Distance'
        ],
        '## Safety Parameters': [
            'Safety Class', 'Beam Enclosure', 'Ventilation Rate', 'Emergency Stop'
        ],
        '## Quality Control Settings': [
            'Surface Roughness Target', 'Cleaning Depth Control', 
            'Process Monitoring', 'Repeatability'
        ]
    }
    
    expected_parameters = parameter_requirements[section_header]
    actual_parameters = [row['parameter'] for row in rows]
    
    return actual_parameters == expected_parameters
```

## Performance Architecture

### Generation Performance

- **Generation Time**: ~0.1-0.2 seconds per material
- **Memory Usage**: ~50KB per generation
- **Concurrency**: Supports parallel generation across materials
- **Caching**: YAML structure is lightweight, no caching needed

### Output Optimization

```yaml
# Optimized structure (no renderInstructions)
machineSettings:
  settings:
  - header: '## Machine Configuration'
    rows:
    - parameter: Power Range
      value: 50-200W
      range: 20W - 500W
      category: Laser Power
```

### File Size Metrics

- **Average File Size**: 1.8KB per file
- **Structure Overhead**: ~200 bytes (headers and YAML structure)
- **Data Content**: ~1.6KB (parameter rows)
- **Compression Ratio**: ~3:1 when gzipped

## Integration Architecture

### Component Factory Integration

```python
# components/settings/__init__.py
from .generators.generator import SettingsComponentGenerator

def get_generator_class():
    return SettingsComponentGenerator

# Automatic registration with ComponentGeneratorFactory
```

### Next.js Integration

```typescript
// types/settings.ts
interface SettingsRow {
  parameter: string;
  value: string;
  range: string;
  category: string;
}

interface SettingsSection {
  header: string;
  rows: SettingsRow[];
}

interface SettingsData {
  machineSettings: {
    settings: SettingsSection[];
  };
}

// components/SettingsTable.tsx
export function SettingsTable({ data }: { data: SettingsData }) {
  return (
    <div className="settings-table">
      {data.machineSettings.settings.map((section, index) => (
        <div key={index} className="settings-section">
          <MDXRemote source={section.header} />
          <table className="settings-table">
            <thead>
              <tr>
                <th>Parameter</th>
                <th>Value</th>
                <th>Range</th>
                <th>Category</th>
              </tr>
            </thead>
            <tbody>
              {section.rows.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  <td>{row.parameter}</td>
                  <td>{row.value}</td>
                  <td>{row.range}</td>
                  <td>{row.category}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
```

## Future Architecture Considerations

### Extensibility

The normalized structure allows for future extensions:

1. **Additional Sections**: Can add new sections while maintaining backward compatibility
2. **Parameter Extensions**: Can add new parameters to existing sections
3. **Metadata Additions**: Can add section-level metadata
4. **Validation Rules**: Can add parameter-specific validation

### Migration Strategy

For future changes to the normalized structure:

1. **Version Tagging**: Add version field to YAML structure
2. **Backward Compatibility**: Maintain support for current structure
3. **Progressive Migration**: Update materials incrementally
4. **Validation Pipeline**: Automated validation during migration

---

*Architecture Documentation | September 2025 | Normalized 4-Section Structure*
