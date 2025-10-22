# Component Architecture Standards

## ⚠️ CRITICAL: Fail-Fast Architecture (MANDATORY)

**ALL COMPONENTS** must implement strict fail-fast behavior - **NO EXCEPTIONS**:

### Universal Fail-Fast Rules

1. **NO Intelligent Defaults**: No category-based defaults, no professional fallbacks
2. **NO 'NA' Values**: Components must fail when data is missing, not return 'NA'
3. **NO Fallback Generation**: No synthetic data generation when primary sources fail
4. **NO Hybrid Approaches**: No combinations of API + defaults or frontmatter + defaults

### Enhanced Frontmatter Integration

**NEW**: All components must use the enhanced frontmatter management system:

#### Frontmatter Manager Integration
```python
# ✅ REQUIRED - Use FrontmatterManager for all frontmatter operations
from frontmatter.management.manager import FrontmatterManager

class MyComponent(EnhancedComponentGenerator):
    def __init__(self):
        super().__init__(component_type="my_component")
    
    def generate(self, material_name: str, **kwargs) -> str:
        # Frontmatter automatically loaded and validated
        frontmatter_data = self.get_frontmatter(material_name)
        return self._generate_content(frontmatter_data, **kwargs)
```

#### Schema Validation Requirements
- ✅ **JSON Schema Validation**: All frontmatter must pass schema validation
- ✅ **Required Fields**: Components must verify required fields exist
- ✅ **Data Types**: Components must validate data types match schema
- ✅ **Field Constraints**: Components must enforce schema constraints

#### Component Generator Base Classes
```python
# ✅ API COMPONENTS - For components that call AI APIs (frontmatter, text, caption, tags)
from generators.component_generators import APIComponentGenerator

# ✅ STATIC COMPONENTS - For components that transform data (table, jsonld, etc.)
from generators.component_generators import StaticComponentGenerator

# ✅ HYBRID COMPONENTS - For components with both API and static logic (metatags, badgesymbol)
from generators.hybrid_generator import HybridComponentGenerator
```

### Component-Specific Fail-Fast Requirements

#### API Components (frontmatter, text)
- ✅ **API Failure**: Fail immediately when API calls fail (no fallback generation)
- ✅ **Missing Dependencies**: Fail when required API client is not provided
- ✅ **Invalid Responses**: Fail when API returns invalid or incomplete data
- ✅ **Frontmatter Validation**: Fail when frontmatter fails schema validation

#### Static Components (caption, jsonld, metatags, etc.)
- ✅ **Missing Frontmatter**: Fail immediately when required frontmatter data is missing
- ✅ **Incomplete Data**: Fail when required fields are missing from frontmatter
- ✅ **Invalid Data**: Fail when frontmatter data is malformed or invalid
- ✅ **Schema Compliance**: Fail when frontmatter doesn't meet schema requirements

### Prohibited Patterns (ALL COMPONENTS)

```python
# ❌ FORBIDDEN - No fallback values
value = frontmatter.get('field', 'NA')
value = frontmatter.get('field', default_value)

# ❌ FORBIDDEN - No intelligent defaults
if category == 'metal':
    wavelength = '1064nm'

# ❌ FORBIDDEN - No fallback generation
if api_failed:
    return self._generate_fallback_content()

# ❌ FORBIDDEN - No hybrid approaches  
value = api_value or frontmatter_value or category_default

# ❌ FORBIDDEN - No error suppression
try:
    required_value = data['required_field']
except KeyError:
    required_value = 'NA'  # Should let KeyError propagate

# ❌ FORBIDDEN - Direct frontmatter file access
with open('content/components/frontmatter/material.md') as f:
    # Should use FrontmatterManager instead

# ❌ FORBIDDEN - Bypassing schema validation
data = yaml.load(frontmatter_file)  # No validation
```

### Required Patterns (ALL COMPONENTS)

```python
# ✅ REQUIRED - Fail fast validation
if not frontmatter_data:
    raise ValueError("Frontmatter data is required")

# ✅ REQUIRED - Direct field access (let KeyError propagate)
wavelength = tech_specs['wavelength']  # No .get() with defaults

# ✅ REQUIRED - API failure handling
if not api_response.success:
    raise GenerationError(f"API call failed: {api_response.error}")

# ✅ REQUIRED - Explicit validation
required_fields = ['wavelength', 'power', 'frequency']
missing = [f for f in required_fields if f not in tech_specs]
if missing:
    raise ValueError(f"Required fields missing: {missing}")
```

### 🚨 Banned Practices (ZERO TOLERANCE)

1. **Random Function Calls**
   ```python
   # ❌ FORBIDDEN - WILL CAUSE SYSTEM FAILURE
   random.choice(['option1', 'option2', 'option3'])
   random.randint(100, 500)
   random.uniform(0.1, 1.0)
   np.random.choice([...])
   ```

2. **Template-based Randomization**
   ```python
   # ❌ FORBIDDEN - WILL CAUSE SYSTEM FAILURE
   options = ['good', 'excellent', 'outstanding']
   result = random.choice(options)
   
   # ❌ FORBIDDEN - WILL CAUSE SYSTEM FAILURE
   value = f"{random.randint(200, 800)} mm/min"
   ```

3. **Probabilistic Value Selection**
   ```python
   # ❌ FORBIDDEN - WILL CAUSE SYSTEM FAILURE
   if random.random() > 0.5:
       return 'option_a'
   else:
       return 'option_b'
   ```

4. **Any Form of Randomization**
   ```python
   # ❌ ALL FORBIDDEN - WILL CAUSE SYSTEM FAILURE
   secrets.choice([...])
   uuid.uuid4().hex[:8]  # When used for content generation
   time.time() % 10  # When used for variation
   hash(str) % 2  # When used for selection
   ```

### Required Practices

1. **Deterministic Values**
   ```python
   # ✅ REQUIRED
   scanning_speed = "500 mm/min"  # Standard consistent value
   beam_delivery = "fiber optic"  # Standard method
   surface_finish = "Ra < 0.6 μm"  # Professional specification
   ```

2. **Frontmatter-Driven Values with 'NA' Fallback**
   ```python
   # ✅ REQUIRED - Use 'NA' when frontmatter data is missing
   value = frontmatter_data.get('laser_parameters', {}).get('scanning_speed', 'NA')
   contamination = frontmatter_data.get('surfaceContamination', 'NA')
   wavelength = tech_specs.get('wavelength', 'NA')
   ```

3. **Professional Standards with 'NA' for Missing Data**
   ```python
   # ✅ REQUIRED - Use first option (most conservative/professional) or 'NA'
   if category_options:
       return category_options[0]  # Not random.choice()
   else:
       return 'NA'  # When no valid data available
   ```

4. **'NA' Value Policy**
   ```python
   # ✅ REQUIRED - Always use 'NA' for missing data
   laser_params = {
       'wavelength': frontmatter.get('wavelength', 'NA'),
       'power': frontmatter.get('power', 'NA'),
       'frequency': frontmatter.get('frequency', 'NA')
   }
   ```

## Rationale

1. **Consistency**: Professional technical documentation requires consistent, repeatable results
2. **Reproducibility**: Generated content must be identical across multiple runs
3. **Quality Control**: Eliminates variability that could introduce inaccuracies
4. **Professional Standards**: Technical specifications must follow industry standards
5. **Testing Reliability**: Enables accurate testing and validation
6. **Data Transparency**: 'NA' clearly indicates missing data rather than generating false values

## Missing Data Policy

### 'NA' Value Standard
When frontmatter or required data is not available after normal validation attempts:

1. **Use 'NA' Value**: Always use the string 'NA' (not null, not empty string)
2. **Clear Indication**: 'NA' explicitly shows data is missing rather than defaulting
3. **Downstream Processing**: Components can detect and handle 'NA' values appropriately
4. **Documentation**: All 'NA' values should be documented in component outputs

### Implementation Examples
```python
# ✅ CORRECT - Use 'NA' for missing data
wavelength = frontmatter_data.get('wavelength', 'NA')
power = tech_specs.get('powerRange', 'NA')
scanning_speed = laser_params.get('scanning_speed', 'NA')

# ❌ INCORRECT - Don't use defaults or generate values
wavelength = frontmatter_data.get('wavelength', '1064nm')  # Don't assume
power = tech_specs.get('powerRange', '100W')  # Don't default
scanning_speed = laser_params.get('scanning_speed', f'{random.randint(200,800)}mm/min')  # FORBIDDEN
```

## Implementation Guidelines

### For Existing Components

1. Replace `random.choice(options)` with `options[0]` (first/most professional option)
2. Replace `random.uniform(min, max)` with standard industry values
3. Replace `random.randint(min, max)` with consistent specifications
4. Remove all `import random` statements

### For New Components

1. Use deterministic values from industry standards
2. Prioritize frontmatter data over generated values
3. Implement fail-fast architecture for missing required data
4. Use professional/conservative defaults when fallback is needed

## Component-Specific Standards

### Caption Component
- **Surface Roughness**: Use standard Ra values (before: 3.2 μm, after: 0.6 μm)
- **Laser Parameters**: Use standard professional specifications
- **Contamination Types**: Use first/most common type for material category
- **Analysis Methods**: Use consistent professional terminology

### JSON-LD Component
- **Technical Specifications**: Use frontmatter data, fail-fast on missing values
- **Quality Metrics**: Use industry-standard performance indicators
- **Material Properties**: Extract from frontmatter, no generated values

### All Components
- **Author Information**: Use consistent professional credentials
- **Technical Terminology**: Use standardized industry language
- **Measurement Units**: Use consistent SI units and professional formatting
- **Quality Descriptors**: Use conservative professional language

## Enforcement

1. **Code Review**: All components must be reviewed for randomization removal
2. **Testing**: Automated tests verify deterministic output and proper 'NA' handling
3. **Documentation**: This standard must be referenced in all component documentation
4. **Architecture**: Use 'NA' for missing frontmatter data rather than failing or using random defaults
5. **API Restriction**: Only frontmatter and text components may use API providers
6. **Zero Tolerance**: Any randomization will cause immediate system failure

## API Provider Restrictions

**ONLY** these components may use API providers:
- ✅ **frontmatter**: Uses DeepSeek API for content generation
- ✅ **text**: Uses DeepSeek API for content generation

**ALL OTHER COMPONENTS** must use:
- ❌ **api_provider**: "none"
- ❌ **data_provider**: "static"

## Fail-Fast Architecture (MANDATORY)

**ALL COMPONENTS** must implement strict fail-fast behavior:

- ✅ **API Components** (frontmatter, text): Fail immediately when API calls fail
- ✅ **Static Components** (caption, jsonld, metatags, etc.): Fail immediately when required frontmatter data is missing
- ❌ **NO HYBRID APPROACH**: No intelligent defaults, no category-based fallbacks
- ❌ **NO FALLBACKS**: Components must fail cleanly when dependencies are missing

### Fail-Fast Implementation Rules

1. **Required Data Validation**
   ```python
   # ✅ REQUIRED - Fail fast when required data missing
   if not frontmatter_data:
       raise ConfigurationError(f"Frontmatter data required for {component_name}")
   
   if 'wavelength' not in tech_specs:
       raise ValueError(f"Wavelength data required but missing from frontmatter")
   ```

2. **API Failure Handling**
   ```python
   # ✅ REQUIRED - Fail fast on API errors
   if not api_response.success:
       raise GenerationError(f"API call failed: {api_response.error}")
   ```

3. **No Intelligent Defaults**
   ```python
   # ❌ FORBIDDEN - No category-based defaults
   # value = self._get_category_defaults(category)
   
   # ❌ FORBIDDEN - No 'NA' fallbacks  
   # value = frontmatter.get('field', 'NA')
   
   # ✅ REQUIRED - Fail fast validation
   value = frontmatter['field']  # Let it raise KeyError
   ```

## API Provider Restrictions

**ONLY** these components may use API providers:
- ✅ **frontmatter**: Uses DeepSeek API for content generation
- ✅ **text**: Uses DeepSeek API for content generation

**ALL OTHER COMPONENTS** must use:
- ❌ **api_provider**: "none"
- ❌ **data_provider**: "static" or "frontmatter"

## Data Dependency Policy

### API Components (frontmatter, text)
- **Primary**: API generation (required)
- **Fail Fast**: When API fails, component fails immediately
- **No Fallbacks**: No intelligent defaults or category-based generation

### Static Components (caption, jsonld, metatags, etc.)
- **Primary**: Frontmatter data (required)
- **Fail Fast**: When frontmatter data missing, component fails immediately  
- **No Fallbacks**: No 'NA' values, no intelligent defaults

### Prohibited Practices (ALL COMPONENTS)
```python
# ❌ FORBIDDEN - No fallback generation
if api_failed:
    return self._generate_fallback_content()

# ❌ FORBIDDEN - No 'NA' values
wavelength = tech_specs.get('wavelength', 'NA')

# ❌ FORBIDDEN - No category defaults
if category == 'metal':
    wavelength = '1064nm'

# ❌ FORBIDDEN - No hybrid approaches
value = api_value or frontmatter_value or default_value
```

### Violating Components Will Be Disabled
Any component found using randomization or unauthorized API access will be immediately disabled in the system configuration.

## Migration Checklist

- [ ] Remove all `import random` statements
- [ ] Replace `random.choice()` with deterministic selection
- [ ] Replace `random.uniform()` with standard values
- [ ] Replace `random.randint()` with professional specifications
- [ ] Update documentation to reflect new standards
- [ ] Test components for consistent output
- [ ] Verify no randomization in fallback scenarios

---

**Status**: ✅ IMPLEMENTED  
**Last Updated**: 2024-12-19  
**Scope**: All components, generators, and content creation systems
