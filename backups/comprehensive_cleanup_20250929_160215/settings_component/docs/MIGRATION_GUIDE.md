# Settings Component Migration Guide

## Overview

This guide covers the migration from the original settings component to the normalized 4-section structure implemented in September 2025.

## What Changed

### Before Normalization (Original)
- Variable number of sections (2-4 depending on data availability)
- Conditional section inclusion based on data presence
- Inconsistent parameter coverage across materials
- Beam Delivery and Performance sections
- renderInstructions included in YAML output

### After Normalization (September 2025)
- Exactly 4 sections for every material
- Mandatory section inclusion with fallback values
- Consistent 16 parameters across all materials
- Safety and Quality Control sections replace Beam/Performance
- Clean YAML output without renderInstructions

## Structural Changes

### Section Headers Changed

#### Removed Sections
```yaml
# OLD - These sections were removed
- header: '## Beam Delivery Settings'
- header: '## Performance Specifications'
```

#### Added Sections
```yaml
# NEW - These sections were added
- header: '## Safety Parameters'
- header: '## Quality Control Settings'
```

#### Unchanged Sections
```yaml
# SAME - These sections remained
- header: '## Machine Configuration'
- header: '## Processing Parameters'
```

### Parameter Changes

#### Machine Configuration (Unchanged)
- Power Range ✅
- Wavelength ✅  
- Pulse Duration ✅
- Repetition Rate ✅

#### Processing Parameters (Updated)
- Fluence Range ✅ (unchanged)
- Spot Size ✅ (unchanged)
- Scanning Speed ✅ (unchanged)
- Working Distance ✅ (moved from Performance)

#### Safety Parameters (New Section)
- Safety Class 🆕 (moved from Beam Delivery)
- Beam Enclosure 🆕
- Ventilation Rate 🆕
- Emergency Stop 🆕

#### Quality Control Settings (New Section)
- Surface Roughness Target 🆕
- Cleaning Depth Control 🆕 (moved from Performance)
- Process Monitoring 🆕
- Repeatability 🆕

## Code Migration

### Generator Method Changes

#### Old Implementation
```python
def _generate_static_content(self, material: str, material_data: Dict, frontmatter_data: Dict = None) -> str:
    # Conditional section generation
    sections = []
    
    if laser_settings:
        sections.append({'header': '## Machine Configuration', 'rows': laser_settings})
    
    if processing_settings:
        sections.append({'header': '## Processing Parameters', 'rows': processing_settings})
    
    # Optional sections based on data availability
    if beam_settings:
        sections.append({'header': '## Beam Delivery Settings', 'rows': beam_settings})
    
    if performance_settings:
        sections.append({'header': '## Performance Specifications', 'rows': performance_settings})
```

#### New Implementation
```python
def _generate_static_content(self, material: str, material_data: Dict, frontmatter_data: Dict = None) -> str:
    # Mandatory 4-section generation
    machine_settings = frontmatter_data.get('machineSettings', {})
    
    # Always generate all 4 sections
    laser_settings = self._extract_laser_settings(machine_settings)
    processing_settings = self._extract_processing_settings(machine_settings)
    safety_settings = self._extract_safety_settings(machine_settings)
    quality_settings = self._extract_quality_settings(machine_settings)
    
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
```

### Method Signature Changes

#### Removed Methods
```python
# These methods were removed
def _extract_beam_settings(self, machine_settings: Dict) -> list:
def _extract_performance_settings(self, machine_settings: Dict) -> list:
```

#### Added Methods
```python
# These methods were added
def _extract_safety_settings(self, machine_settings: Dict) -> list:
def _extract_quality_settings(self, machine_settings: Dict) -> list:
def _build_range(self, machine_settings: Dict, base_key: str, default_range: str) -> str:
```

## Data Migration

### Field Mapping Updates

#### Safety Parameters Mapping
```python
# Map existing fields to safety parameters
safety_class = (
    machine_settings.get("safetyClass") or
    machine_settings.get("safety_class") or
    "Class 4"  # fallback
)

ventilation_rate = (
    machine_settings.get("ventilationRate") or
    "200-500 CFM"  # fallback
)
```

#### Quality Control Mapping
```python
# Map existing fields to quality parameters
surface_roughness = (
    machine_settings.get("surfaceRoughness") or
    "Ra 0.1-0.5μm"  # fallback
)

cleaning_depth = (
    machine_settings.get("cleaningDepth") or
    "1-10μm"  # fallback
)
```

### Frontmatter Data Compatibility

The normalized generator maintains backward compatibility with existing frontmatter data:

```python
# All these field variations work
frontmatter_data = {
    'machineSettings': {
        # Original format
        'powerRange': '50-200W',
        'wavelength': '1064nm',
        
        # Alternative formats
        'power_range': '50-200W',
        'wavelength_optimal': '1064nm',
        
        # New safety fields
        'safetyClass': 'Class 4',
        'ventilationRate': '200-500 CFM',
        
        # New quality fields
        'surfaceRoughness': 'Ra 0.1-0.5μm',
        'cleaningDepth': '1-10μm',
        'processMonitoring': 'Real-time optical',
        'repeatability': '±5%'
    }
}
```

## Testing Migration

### Old Test Structure
```python
def test_section_generation(self):
    # Test variable section count
    self.assertTrue(2 <= len(sections) <= 4)
    
    # Test conditional headers
    headers = [section['header'] for section in sections]
    self.assertIn('## Machine Configuration', headers)
    # Other sections optional
```

### New Test Structure
```python
def test_normalized_4_section_structure(self):
    # Test exactly 4 sections
    self.assertEqual(len(settings), 4)
    
    # Test mandatory headers
    expected_headers = [
        '## Machine Configuration',
        '## Processing Parameters',
        '## Safety Parameters',
        '## Quality Control Settings'
    ]
    actual_headers = [section['header'] for section in settings]
    self.assertEqual(actual_headers, expected_headers)
```

## File Migration

### Bulk Regeneration Process

```bash
# Regenerate all settings files with normalized structure
python3 run.py --all --component settings

# Verify normalization
python3 components/settings/testing/test_settings_normalized.py
```

### File Format Changes

#### Before (Example)
```yaml
machineSettings:
  settings:
  - header: '## Machine Configuration'
    rows:
    - parameter: Power Range
      value: 50-200W
      range: 20W - 500W
      category: Laser Power
  - header: '## Processing Parameters'
    rows: [...]
  # Variable sections based on data
renderInstructions: In Next.js, loop over settings[].rows...
```

#### After (Example)
```yaml
machineSettings:
  settings:
  - header: '## Machine Configuration'
    rows:
    - parameter: Power Range
      value: 50-200W
      range: 20W - 500W
      category: Laser Power
    - parameter: Wavelength
      value: 1064nm (primary), 532nm (optional)
      range: 355nm - 2940nm
      category: Optical
    - parameter: Pulse Duration
      value: 10-200ns
      range: 1ns - 1000ns
      category: Temporal
    - parameter: Repetition Rate
      value: 20-100kHz
      range: 1kHz - 1000kHz
      category: Timing
  - header: '## Processing Parameters'
    rows: [4 parameters]
  - header: '## Safety Parameters'
    rows: [4 parameters]
  - header: '## Quality Control Settings'
    rows: [4 parameters]
# No renderInstructions
```

## Next.js Integration Migration

### Component Updates

#### Old Rendering
```typescript
// Variable section handling
{settings?.map((section, index) => (
  <div key={index}>
    <MDXRemote source={section.header} />
    {section.rows?.map((row, rowIndex) => (
      <tr key={rowIndex}>
        <td>{row.parameter}</td>
        <td>{row.value}</td>
        <td>{row.range}</td>
        <td>{row.category}</td>
      </tr>
    ))}
  </div>
))}
```

#### New Rendering (Unchanged)
```typescript
// Fixed 4-section structure (same code works)
{settings.map((section, index) => (
  <div key={index}>
    <MDXRemote source={section.header} />
    <table>
      {section.rows.map((row, rowIndex) => (
        <tr key={rowIndex}>
          <td>{row.parameter}</td>
          <td>{row.value}</td>
          <td>{row.range}</td>
          <td>{row.category}</td>
        </tr>
      ))}
    </table>
  </div>
))}
```

### Type Definitions

```typescript
// Updated interface for normalized structure
interface SettingsData {
  machineSettings: {
    settings: [
      LaserSystemSection,
      ProcessingParametersSection,
      SafetyParametersSection,
      QualityControlSection
    ];
  };
}

interface SettingsSection {
  header: '## Machine Configuration' | 
          '## Processing Parameters' | 
          '## Safety Parameters' | 
          '## Quality Control Settings';
  rows: [SettingsRow, SettingsRow, SettingsRow, SettingsRow]; // Always 4 rows
}
```

## Validation Migration

### New Validation Requirements

```python
def validate_normalized_file(file_path: str) -> bool:
    """Validate normalized settings file structure"""
    with open(file_path, 'r') as f:
        data = yaml.safe_load(f.read())
    
    # Check 4-section structure
    if len(data['machineSettings']['settings']) != 4:
        return False
    
    # Check headers
    expected_headers = [
        '## Machine Configuration',
        '## Processing Parameters',
        '## Safety Parameters',
        '## Quality Control Settings'
    ]
    
    actual_headers = [s['header'] for s in data['machineSettings']['settings']]
    if actual_headers != expected_headers:
        return False
    
    # Check 4 parameters per section
    for section in data['machineSettings']['settings']:
        if len(section['rows']) != 4:
            return False
    
    return True
```

## Deployment Migration

### Deployment Process

1. **Backup Existing Files**
   ```bash
   cp -r content/components/settings content/components/settings_backup_$(date +%Y%m%d)
   ```

2. **Regenerate Normalized Files**
   ```bash
   python3 run.py --all --component settings
   ```

3. **Validate Migration**
   ```bash
   python3 components/settings/testing/test_settings_normalized.py
   ```

4. **Deploy to Production**
   ```bash
   python3 run.py --deploy
   ```

### Migration Verification

```bash
# Check file count (should be 109)
ls content/components/settings/*.yaml | wc -l

# Check structure consistency
python3 -c "
import yaml
import glob

files = glob.glob('content/components/settings/*.yaml')
for file in files[:5]:  # Check first 5 files
    with open(file) as f:
        data = yaml.safe_load(f)
    sections = len(data['machineSettings']['settings'])
    print(f'{file}: {sections} sections')
"
```

## Breaking Changes

### ⚠️ Incompatible Changes

1. **Section Count**: Files now always have 4 sections (was 2-4)
2. **Section Headers**: "Beam Delivery" and "Performance" removed
3. **renderInstructions**: No longer included in YAML output
4. **Parameter Count**: Each section has exactly 4 parameters
5. **New Required Sections**: Safety and Quality Control now mandatory

### ✅ Backward Compatible

1. **Field Names**: Both camelCase and snake_case supported
2. **Data Extraction**: Existing frontmatter fields still work
3. **Rendering Code**: Next.js components don't need changes
4. **API Interface**: Generator interface unchanged
5. **Component Factory**: Registration unchanged

## Rollback Plan

If rollback is needed:

1. **Restore Backup**
   ```bash
   rm -rf content/components/settings
   mv content/components/settings_backup_YYYYMMDD content/components/settings
   ```

2. **Revert Generator Code**
   ```bash
   git checkout HEAD~1 components/settings/generators/generator.py
   ```

3. **Redeploy**
   ```bash
   python3 run.py --deploy
   ```

## Migration Checklist

### Pre-Migration
- [ ] Backup existing settings files
- [ ] Document current section counts per material
- [ ] Test normalized generator on sample materials
- [ ] Review frontmatter data completeness

### Migration
- [ ] Regenerate all 109 settings files
- [ ] Validate 4-section structure
- [ ] Test parameter completeness
- [ ] Verify fallback value usage

### Post-Migration
- [ ] Run normalized test suite
- [ ] Deploy to production
- [ ] Verify Next.js rendering
- [ ] Monitor for any issues

### Validation
- [ ] All 109 files have exactly 4 sections
- [ ] All sections have 4 parameters each
- [ ] No renderInstructions in output
- [ ] Safety and Quality sections present
- [ ] Field mapping works correctly

---

*Migration Guide | September 2025 | Settings Component Normalization*
