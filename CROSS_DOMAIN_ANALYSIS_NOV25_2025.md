# Cross-Domain Analysis: Materials → Contaminants Feature Identification

**Date**: November 25, 2025  
**Purpose**: Identify useful Materials domain features for Contaminants domain enhancement  
**Status**: Analysis Complete - Recommendations Ready

---

## Executive Summary

**Analysis Scope**: Compared `domains/materials/` vs `domains/contaminants/` structures to identify feature gaps and enhancement opportunities.

**Key Finding**: Materials domain has **7 architectural components** that Contaminants lacks:
1. ✅ **CategoryDataLoader** - Highly useful for pattern-level data
2. ✅ **Schema.py** - Python dataclasses with validation
3. ✅ **Services Layer** - Property management, validation, templates
4. ✅ **Utils Library** - Property helpers, taxonomy, caching
5. ✅ **Modules Pattern** - Frontmatter generation pipeline
6. ⚠️ **Prompts Directory** - Component templates (already exists in root `prompts/`)
7. ❌ **Image Directory** - Not applicable to Contaminants

**Recommendation**: Implement components 1-5 for Contaminants domain with contamination-specific adaptations.

---

## Component-by-Component Analysis

### 1. ✅ CategoryDataLoader (HIGHLY RECOMMENDED)

**Materials Implementation**: `domains/materials/category_loader.py` (311 lines)

**Purpose**:
- Loads category-level data from `CategoryTaxonomy.yaml`
- Provides lazy loading with LRU caching
- Unified API for category metadata, property descriptions, machine settings
- Thread-safe caching with fail-fast validation
- Backward compatibility with split/monolithic YAML architectures

**Key Features**:
```python
loader = CategoryDataLoader()
settings = loader.get_machine_settings()       # Parameter ranges/descriptions
properties = loader.get_material_properties()  # Property descriptions per category
taxonomy = loader.get_property_taxonomy()      # Property classification
safety = loader.get_safety_regulatory()        # Safety standards
```

**Usefulness for Contaminants**: ⭐⭐⭐⭐⭐ (5/5)

**Why Contaminants Needs This**:
1. **Pattern-Level Data**: Current `Contaminants.yaml` has 11 patterns with shared metadata needs
2. **Taxonomy Management**: Contamination types, severity levels, removal difficulty classifications
3. **Laser Parameters**: Pattern-specific laser parameter ranges (wavelength, fluence, scan speed)
4. **Safety Data**: Fume compositions, PPE requirements, ventilation standards per pattern
5. **Performance Caching**: Avoid repeated YAML parsing (especially important with 11 patterns × laser properties)

**Adaptation for Contaminants**:
```python
# domains/contaminants/pattern_loader.py
class PatternDataLoader:
    """
    Load pattern-level contamination data with caching.
    
    Mirrors CategoryDataLoader architecture but for contamination patterns.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.contaminants_file = project_root / 'data' / 'contaminants' / 'Contaminants.yaml'
        self._cache = {}
        self._cache_lock = threading.Lock()
    
    def get_pattern_metadata(self) -> Dict[str, Any]:
        """Get pattern descriptions, removal mechanisms, characteristics"""
        return self._get_key('patterns')
    
    def get_laser_parameters(self) -> Dict[str, Any]:
        """Get laser parameter ranges per pattern (from LaserPropertiesResearcher data)"""
        return {
            pattern_id: pattern_data.get('laser_properties', {}).get('laser_parameters', {})
            for pattern_id, pattern_data in self._load_contaminants_data()['patterns'].items()
        }
    
    def get_safety_data(self) -> Dict[str, Any]:
        """Get safety requirements per pattern"""
        return {
            pattern_id: pattern_data.get('laser_properties', {}).get('safety_data', {})
            for pattern_id, pattern_data in self._load_contaminants_data()['patterns'].items()
        }
    
    def get_removal_characteristics(self) -> Dict[str, Any]:
        """Get removal mechanisms, efficiency, surface quality per pattern"""
        return {
            pattern_id: pattern_data.get('laser_properties', {}).get('removal_characteristics', {})
            for pattern_id, pattern_data in self._load_contaminants_data()['patterns'].items()
        }
    
    def get_optical_properties(self, wavelength: str = '1064nm') -> Dict[str, Any]:
        """Get absorption coefficients, reflectivity per pattern at wavelength"""
        pass
    
    def get_pattern_ranges(self, pattern_id: str) -> Dict[str, Any]:
        """Get thickness ranges, adhesion strength, layer properties for pattern"""
        pass
```

**Implementation Priority**: 🔥 **HIGH** (foundational architecture)

---

### 2. ✅ Schema.py (STRONGLY RECOMMENDED)

**Materials Implementation**: `domains/materials/schema.py` (483 lines)

**Purpose**:
- Python dataclasses for type-safe content structure
- Comprehensive validation (required fields, format checks, schema compliance)
- Research specifications (field types, research methods, validation rules)
- Citation architecture (MaterialPropertyValue, CategoryRangeValue with full citations)
- Zero-fallback policy enforcement (null values MUST have needs_research flag)
- Dict conversion for YAML export/import

**Key Components**:
```python
@dataclass
class MaterialPropertyValue:
    """Property with comprehensive citations"""
    value: Optional[float]
    unit: str
    source: str           # scientific_literature | materials_database
    source_type: str      # reference_handbook | journal_article
    source_name: str      # Full source name
    citation: str         # Complete citation with ISBN/DOI
    context: str          # Measurement methodology
    confidence: int       # 0-100 scale
    researched_date: str
    needs_validation: bool
    needs_research: bool = False  # If value is None

@dataclass
class MaterialContent(ContentSchema):
    """Material-specific content schema"""
    materialProperties: Dict[str, Dict]
    machineSettings: Dict[str, Dict]
    applications: List[str]
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate completeness with detailed error messages"""
        pass
    
    def get_researchable_fields(self) -> Dict[str, FieldResearchSpec]:
        """Define how to AI-research missing data"""
        pass
```

**Usefulness for Contaminants**: ⭐⭐⭐⭐⭐ (5/5)

**Why Contaminants Needs This**:
1. **Type Safety**: Current `models.py` uses basic dataclasses, missing validation
2. **Citation Tracking**: Laser properties research needs source attribution (already in LaserPropertiesResearcher!)
3. **Research Integration**: `FieldResearchSpec` defines how to discover missing pattern data
4. **Validation**: Enforce structure for optical_properties, thermal_properties, removal_characteristics
5. **AI Research Coordination**: Automatic discovery of gaps with research specifications

**Adaptation for Contaminants**:
```python
# domains/contaminants/schema.py

@dataclass
class LaserPropertyValue:
    """
    Laser-specific property with citations (extends MaterialPropertyValue pattern).
    
    Used for optical, thermal, removal properties.
    """
    value: Optional[float]
    unit: str
    wavelength: Optional[str] = None  # For wavelength-dependent properties
    material_context: Optional[str] = None  # Substrate material if applicable
    
    # Citation fields (REQUIRED for non-null values)
    source: str
    source_type: str
    source_name: str
    citation: str
    context: str
    confidence: int
    
    researched_date: str
    needs_validation: bool
    needs_research: bool = False


@dataclass
class ContaminationPattern(ContentSchema):
    """
    Contamination pattern schema with laser properties.
    
    Extends ContentSchema with pattern-specific fields.
    """
    pattern_id: str
    description: str
    removal_mechanism: str
    severity_levels: List[str]
    
    # Laser properties (from LaserPropertiesResearcher)
    optical_properties: Dict[str, Dict] = field(default_factory=dict)
    thermal_properties: Dict[str, Dict] = field(default_factory=dict)
    removal_characteristics: Dict[str, Dict] = field(default_factory=dict)
    layer_properties: Dict[str, Dict] = field(default_factory=dict)
    laser_parameters: Dict[str, Dict] = field(default_factory=dict)
    safety_data: Dict[str, Dict] = field(default_factory=dict)
    
    # Applicability data
    valid_materials: List[str] = field(default_factory=list)
    prohibited_materials: List[str] = field(default_factory=list)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate pattern completeness"""
        errors = []
        
        # Check required fields
        if not self.pattern_id:
            errors.append("Missing pattern_id")
        
        # Validate optical properties structure
        if self.optical_properties:
            for wavelength, data in self.optical_properties.items():
                if 'absorption_coefficient' not in data:
                    errors.append(f"Missing absorption_coefficient for {wavelength}")
        
        # Validate laser parameters structure
        if self.laser_parameters:
            required = {'recommended_wavelength', 'fluence_range', 'scan_speed_range'}
            missing = required - set(self.laser_parameters.keys())
            if missing:
                errors.append(f"Missing laser parameters: {missing}")
        
        return (len(errors) == 0, errors)
    
    def get_researchable_fields(self) -> Dict[str, FieldResearchSpec]:
        """Define AI research specifications for laser properties"""
        return {
            'optical_properties': FieldResearchSpec(
                field_name='optical_properties',
                field_type=FieldType.PROPERTY,
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/optical_properties.txt',
                validation_rules={
                    'required_wavelengths': ['1064nm', '532nm'],
                    'required_fields': ['absorption_coefficient', 'reflectivity']
                },
                priority=1  # Critical
            ),
            'thermal_properties': FieldResearchSpec(...),
            'removal_characteristics': FieldResearchSpec(...),
            # etc.
        }
```

**Implementation Priority**: 🔥 **HIGH** (enables type-safe operations + research coordination)

---

### 3. ✅ Services Layer (RECOMMENDED)

**Materials Implementation**: `domains/materials/services/`
- `property_manager.py` (991 lines) - Unified property lifecycle management
- `validation_service.py` - Data validation orchestration
- `template_service.py` - Template loading/rendering
- `pipeline_process_service.py` - Processing pipeline coordination

**Purpose**:
- **PropertyManager**: Discovery → Research → Categorization → Validation → Normalization
- Consolidates scattered logic into cohesive services
- Fail-fast principles with explicit error handling
- Materials.yaml writeback for AI research results
- Research coordination with UnifiedMaterialResearch

**Key Features of PropertyManager**:
```python
class PropertyManager:
    """Unified property management service"""
    
    def discover_gaps(self, material_data: Dict) -> Dict[str, Set[str]]:
        """Identify missing properties per category"""
        pass
    
    def research_properties(
        self, 
        material_name: str,
        missing_properties: Set[str],
        category: str
    ) -> PropertyResearchResult:
        """AI research missing properties with categorization"""
        pass
    
    def validate_and_normalize(
        self,
        properties: Dict,
        category: str
    ) -> Dict:
        """Validate values against category ranges and normalize units"""
        pass
    
    def save_to_materials_yaml(
        self,
        material_name: str,
        research_result: PropertyResearchResult
    ):
        """Write research results back to Materials.yaml"""
        pass
```

**Usefulness for Contaminants**: ⭐⭐⭐⭐ (4/5)

**Why Contaminants Needs This**:
1. **Research Coordination**: PropertyManager pattern perfect for LaserPropertiesResearcher orchestration
2. **Gap Discovery**: Identify which patterns missing optical_properties, thermal_properties, etc.
3. **Validation**: Ensure laser parameters within physical constraints (absorption + reflection + transmission = 1.0)
4. **Writeback**: Save LaserPropertiesResearcher results to Contaminants.yaml automatically
5. **Pipeline**: Coordinate multi-step research (optical → thermal → removal → safety)

**Adaptation for Contaminants**:
```python
# domains/contaminants/services/pattern_manager.py

class PatternManager:
    """
    Unified pattern property management.
    
    Mirrors PropertyManager architecture for contamination patterns.
    Discovery → Research → Validation → Normalization → Persistence
    """
    
    def __init__(
        self,
        laser_researcher: LaserPropertiesResearcher,
        pattern_loader: PatternDataLoader
    ):
        self.laser_researcher = laser_researcher
        self.pattern_loader = pattern_loader
    
    def discover_laser_property_gaps(
        self,
        pattern_id: str
    ) -> Dict[str, bool]:
        """
        Identify missing laser properties for pattern.
        
        Returns:
            {
                'optical_properties': False,  # Missing
                'thermal_properties': True,   # Present
                'removal_characteristics': False,
                'laser_parameters': False,
                'safety_data': True
            }
        """
        pattern_data = self.pattern_loader.get_pattern_metadata()[pattern_id]
        laser_props = pattern_data.get('laser_properties', {})
        
        return {
            'optical_properties': 'optical_properties' in laser_props,
            'thermal_properties': 'thermal_properties' in laser_props,
            'removal_characteristics': 'removal_characteristics' in laser_props,
            'layer_properties': 'layer_properties' in laser_props,
            'laser_parameters': 'laser_parameters' in laser_props,
            'safety_data': 'safety_data' in laser_props,
            'selectivity_ratios': 'selectivity_ratios' in laser_props
        }
    
    def research_laser_properties(
        self,
        pattern_id: str,
        research_types: List[str],
        material_context: Optional[str] = None
    ) -> Dict[str, Dict]:
        """
        Research laser properties using LaserPropertiesResearcher.
        
        Returns combined results from all research types.
        """
        results = {}
        
        for research_type in research_types:
            try:
                result = self.laser_researcher.research(
                    pattern_id=pattern_id,
                    research_type=research_type,
                    material_context=material_context
                )
                
                if result['confidence'] >= 0.70:  # ACCEPTABLE threshold
                    results[research_type] = result['data']
                else:
                    logger.warning(
                        f"Low confidence ({result['confidence']:.2f}) for "
                        f"{pattern_id}.{research_type} - skipping"
                    )
            
            except Exception as e:
                logger.error(f"Research failed for {research_type}: {e}")
        
        return results
    
    def validate_laser_properties(
        self,
        properties: Dict[str, Dict]
    ) -> Tuple[bool, List[str]]:
        """
        Validate laser properties meet physical constraints.
        
        Checks:
        - Absorption + reflection + transmission ≈ 1.0 (optical properties)
        - Fluence range within ablation thresholds (laser parameters)
        - Wavelength-specific values consistent
        """
        errors = []
        
        # Validate optical properties
        if 'optical_properties' in properties:
            for wavelength, data in properties['optical_properties'].items():
                absorption = data.get('absorption_coefficient', 0)
                reflection = data.get('reflectivity', 0)
                
                # Basic sanity check (simplified - real implementation needs transmission)
                if absorption > 1.0 or reflection > 1.0:
                    errors.append(
                        f"{wavelength}: absorption or reflection > 1.0 (impossible)"
                    )
        
        # Validate laser parameters
        if 'laser_parameters' in properties:
            params = properties['laser_parameters']
            
            if 'fluence_range' in params:
                fluence = params['fluence_range']
                if fluence.get('min', 0) > fluence.get('max', 0):
                    errors.append("Fluence min > max")
        
        return (len(errors) == 0, errors)
    
    def save_to_contaminants_yaml(
        self,
        pattern_id: str,
        laser_properties: Dict[str, Dict]
    ):
        """
        Write laser properties to Contaminants.yaml.
        
        Updates pattern_id.laser_properties with researched data.
        Backs up original file before modification.
        """
        contaminants_file = self.pattern_loader.contaminants_file
        
        # Backup original
        backup_file = contaminants_file.parent / f"{contaminants_file.stem}_backup.yaml"
        shutil.copy(contaminants_file, backup_file)
        
        # Load current data
        with open(contaminants_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Update pattern
        if 'patterns' not in data or pattern_id not in data['patterns']:
            raise ValueError(f"Pattern {pattern_id} not found in Contaminants.yaml")
        
        data['patterns'][pattern_id]['laser_properties'] = laser_properties
        data['patterns'][pattern_id]['last_updated'] = datetime.utcnow().isoformat() + 'Z'
        
        # Write updated data
        with open(contaminants_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"✅ Saved laser properties for {pattern_id} to Contaminants.yaml")
```

**Implementation Priority**: 🔥 **MEDIUM-HIGH** (orchestration layer, useful but not foundational)

---

### 4. ✅ Utils Library (RECOMMENDED)

**Materials Implementation**: `domains/materials/utils/`
- `property_helpers.py` - Property manipulation utilities
- `property_taxonomy.py` - Property classification (quantitative/qualitative)
- `unit_extractor.py` - Unit parsing and normalization
- `category_property_cache.py` - LRU caching for property lookups
- `property_enhancer.py` - Description enrichment

**Purpose**:
- Reusable utility functions for property operations
- Unit conversion and normalization
- Property type classification (quantitative/qualitative)
- Performance optimization (caching)
- Description enhancement with context

**Key Utilities**:
```python
# property_helpers.py
def extract_numeric_value(value_str: str) -> Tuple[float, str]:
    """Extract numeric value and unit from string"""
    pass

def normalize_property_name(prop: str) -> str:
    """Convert to canonical property name"""
    pass

# property_taxonomy.py
def classify_property(prop_name: str, value: Any) -> str:
    """Classify as 'quantitative' or 'qualitative'"""
    pass

def get_property_category(prop_name: str) -> str:
    """Get category: thermal, mechanical, optical, etc."""
    pass

# unit_extractor.py
class UnitExtractor:
    """Extract and normalize units from values"""
    
    def extract_unit(self, value_str: str) -> str:
        """Extract unit from value string"""
        pass
    
    def normalize_unit(self, unit: str, quantity_type: str) -> str:
        """Convert to standard unit"""
        pass
```

**Usefulness for Contaminants**: ⭐⭐⭐⭐ (4/5)

**Why Contaminants Needs This**:
1. **Unit Normalization**: Laser properties use various units (J/cm², W, μm, nm, etc.)
2. **Property Classification**: Distinguish quantitative (absorption coefficient) vs qualitative (removal mechanism)
3. **Value Extraction**: Parse AI responses like "0.85 ± 0.05 at 1064nm" → value=0.85, unit=dimensionless, wavelength=1064nm
4. **Caching**: LRU cache for pattern lookups (especially with 11 patterns × 8 research types)
5. **Consistency**: Shared utilities ensure consistent data handling

**Adaptation for Contaminants**:
```python
# domains/contaminants/utils/laser_property_helpers.py

def extract_wavelength_value(value_str: str) -> Tuple[float, str, Optional[str]]:
    """
    Extract value, unit, and wavelength from laser property string.
    
    Examples:
        "0.85 at 1064nm" → (0.85, "dimensionless", "1064nm")
        "5.2 J/cm² (532nm)" → (5.2, "J/cm²", "532nm")
        "2500 W" → (2500, "W", None)
    """
    pass

def normalize_laser_unit(unit: str, property_type: str) -> str:
    """
    Normalize laser-specific units.
    
    Property types: optical, thermal, energy, power, speed
    
    Examples:
        unit="mJ/cm2", property_type="energy" → "J/cm²"
        unit="watts", property_type="power" → "W"
        unit="microns", property_type="length" → "μm"
    """
    pass

def classify_laser_property(prop_name: str) -> str:
    """
    Classify laser property type.
    
    Returns: optical | thermal | removal | layer | parameter | safety
    
    Examples:
        "absorption_coefficient" → "optical"
        "ablation_threshold" → "thermal"
        "removal_efficiency" → "removal"
        "fluence_range" → "parameter"
    """
    PROPERTY_CATEGORIES = {
        'optical': {
            'absorption_coefficient', 'reflectivity', 'transmittance',
            'refractive_index', 'extinction_coefficient'
        },
        'thermal': {
            'ablation_threshold', 'decomposition_temperature',
            'thermal_conductivity', 'specific_heat_capacity',
            'vaporization_temperature'
        },
        'removal': {
            'removal_mechanism', 'removal_efficiency', 'surface_quality',
            'byproducts', 'removal_rate'
        },
        'layer': {
            'typical_thickness', 'thickness_range', 'penetration_depth',
            'adhesion_strength', 'layer_composition'
        },
        'parameter': {
            'recommended_wavelength', 'fluence_range', 'scan_speed_range',
            'pulse_duration', 'spot_size', 'overlap_percentage'
        },
        'safety': {
            'fume_composition', 'exposure_limits', 'ventilation_requirements',
            'ppe_requirements', 'hazard_classification'
        }
    }
    
    for category, properties in PROPERTY_CATEGORIES.items():
        if prop_name in properties:
            return category
    
    return 'unknown'

# domains/contaminants/utils/pattern_cache.py

class PatternPropertyCache:
    """
    LRU cache for contamination pattern property lookups.
    
    Mirrors CategoryPropertyCache for Materials domain.
    """
    
    def __init__(self, max_size: int = 128):
        from functools import lru_cache
        
        self._get_pattern_properties = lru_cache(maxsize=max_size)(
            self._get_pattern_properties_impl
        )
    
    def _get_pattern_properties_impl(
        self,
        pattern_id: str,
        property_type: str
    ) -> Dict:
        """
        Load pattern properties with caching.
        
        Args:
            pattern_id: Contamination pattern ID
            property_type: optical_properties | thermal_properties | removal_characteristics | etc.
        """
        from domains.contaminants.pattern_loader import PatternDataLoader
        
        loader = PatternDataLoader()
        pattern_data = loader.get_pattern_metadata()[pattern_id]
        
        return pattern_data.get('laser_properties', {}).get(property_type, {})
    
    def get_optical_properties(
        self,
        pattern_id: str,
        wavelength: Optional[str] = None
    ) -> Dict:
        """Get optical properties (cached) with optional wavelength filter"""
        props = self._get_pattern_properties(pattern_id, 'optical_properties')
        
        if wavelength:
            return props.get(wavelength, {})
        
        return props
    
    def clear_cache(self):
        """Clear LRU cache"""
        self._get_pattern_properties.cache_clear()
```

**Implementation Priority**: 🔥 **MEDIUM** (quality-of-life improvements, not foundational)

---

### 5. ✅ Modules Pattern (RECOMMENDED)

**Materials Implementation**: `domains/materials/modules/`
- `author_module.py` - Extract author metadata
- `properties_module.py` - Property data extraction
- `settings_module.py` - Machine settings extraction
- `metadata_module.py` - Metadata extraction
- `simple_modules.py` - Title, category, other simple fields

**Purpose**:
- Modular frontmatter generation pipeline
- Each module handles one aspect of frontmatter (author, properties, settings, etc.)
- Pure extraction from Materials.yaml → frontmatter structure
- Fail-fast validation (missing required fields → ValueError)
- Composable architecture (mix and match modules)

**Architecture Pattern**:
```python
class AuthorModule:
    """Extract author metadata for frontmatter"""
    
    REQUIRED_FIELDS = ['id', 'name', 'country']
    
    def generate(self, material_data: Dict) -> Dict:
        """Extract and validate author from material data"""
        if 'author' not in material_data:
            raise ValueError("Author field missing")
        
        author = material_data['author']
        self._validate_author(author)
        
        return author  # Pure extraction

class PropertiesModule:
    """Extract and transform material properties for frontmatter"""
    
    def generate(self, material_data: Dict) -> Dict:
        """Extract properties with category grouping"""
        props = material_data.get('materialProperties', {})
        
        # Transform to frontmatter structure
        return self._transform_properties(props)
```

**Usefulness for Contaminants**: ⭐⭐⭐ (3/5)

**Why Contaminants Might Need This**:
1. **Page Generation**: When generating contamination pattern pages (future feature)
2. **Frontmatter Structure**: Consistent field extraction for pattern pages
3. **Composability**: Mix pattern metadata, laser properties, safety data modules
4. **Validation**: Ensure pattern pages have required fields before publishing

**Adaptation for Contaminants**:
```python
# domains/contaminants/modules/pattern_metadata_module.py

class PatternMetadataModule:
    """Extract pattern metadata for pattern page frontmatter"""
    
    REQUIRED_FIELDS = ['pattern_id', 'name', 'description', 'removal_mechanism']
    
    def generate(self, pattern_data: Dict) -> Dict:
        """
        Extract pattern metadata from Contaminants.yaml.
        
        Returns:
            {
                'pattern_id': 'rust_oxidation',
                'name': 'Rust & Oxidation',
                'description': '...',
                'removal_mechanism': 'ablation',
                'severity_levels': ['light', 'moderate', 'heavy'],
                'typical_environments': ['outdoor', 'marine', 'industrial']
            }
        """
        self._validate_pattern(pattern_data)
        
        return {
            'pattern_id': pattern_data['pattern_id'],
            'name': pattern_data['name'],
            'description': pattern_data['description'],
            'removal_mechanism': pattern_data['removal_mechanism'],
            'severity_levels': pattern_data.get('severity_levels', []),
            'typical_environments': pattern_data.get('typical_environments', [])
        }

# domains/contaminants/modules/laser_properties_module.py

class LaserPropertiesModule:
    """Extract laser properties for pattern page frontmatter"""
    
    def generate(self, pattern_data: Dict) -> Dict:
        """
        Extract laser properties from pattern data.
        
        Returns structured laser properties for frontmatter:
        - optical_properties (by wavelength)
        - thermal_properties
        - recommended_parameters
        - safety_data
        """
        laser_props = pattern_data.get('laser_properties', {})
        
        return {
            'optical': self._extract_optical(laser_props),
            'thermal': self._extract_thermal(laser_props),
            'parameters': self._extract_parameters(laser_props),
            'safety': self._extract_safety(laser_props)
        }

# domains/contaminants/modules/applicability_module.py

class ApplicabilityModule:
    """Extract material applicability for pattern pages"""
    
    def generate(self, pattern_data: Dict) -> Dict:
        """
        Extract valid/prohibited materials with applicability metadata.
        
        Returns:
            {
                'valid_materials': ['Steel', 'Iron', 'Aluminum'],
                'prohibited_materials': ['Plastic', 'Wood'],
                'applicability_details': {
                    'Steel': {
                        'likelihood': 'high',
                        'typical_environments': ['outdoor', 'marine'],
                        'layer_thickness_range': [5, 500]  # μm
                    }
                }
            }
        """
        pass
```

**Implementation Priority**: 🟡 **LOW-MEDIUM** (useful for future pattern pages, but not immediate need)

---

### 6. ⚠️ Prompts Directory (ALREADY EXISTS)

**Materials Implementation**: `domains/materials/prompts/`
- `caption.txt` - Caption generation template
- `faq.txt` - FAQ generation template
- `material_description.txt` - Description generation template
- `settings_description.txt` - Settings description template
- `personas/` - Author voice personas

**Status**: ⚠️ **Root `prompts/` directory already handles this**

**Current Contaminants Approach**:
- Uses root `prompts/components/` for component generation
- Uses root `prompts/personas/` for author voices
- Domain-specific prompts not needed (contaminants use same generation infrastructure)

**Recommendation**: ❌ **DO NOT DUPLICATE** - Current architecture is correct

**Rationale**:
1. Component generation is domain-agnostic (caption, description, FAQ work for both materials and contaminants)
2. Author personas are shared across domains
3. Duplication would violate DRY principle
4. Root `prompts/` provides centralized prompt management

**Future Consideration**:
IF contaminants need pattern-specific prompts (e.g., "generate laser safety warnings"), THEN:
- Create `domains/contaminants/prompts/` for contamination-specific templates
- Keep component prompts in root `prompts/components/`
- Use domain-specific prompts only when truly specialized

---

### 7. ❌ Image Directory (NOT APPLICABLE)

**Materials Implementation**: `domains/materials/image/`
- Image generation for material visualization
- Material appearance rendering
- Surface texture generation

**Usefulness for Contaminants**: ⭐ (1/5) - Not applicable

**Why Contaminants Doesn't Need This**:
1. **Visual Representation**: Contamination patterns don't need dedicated images (handled by material+pattern combination)
2. **Complexity**: Image generation is material-specific feature
3. **Scope**: Contaminants domain focuses on metadata, not visualization

**Recommendation**: ❌ **SKIP** - Not relevant to contamination pattern management

---

## Implementation Priority Matrix

| Component | Usefulness | Implementation Priority | Effort | Impact |
|-----------|------------|------------------------|--------|--------|
| **CategoryDataLoader → PatternDataLoader** | ⭐⭐⭐⭐⭐ (5/5) | 🔥 HIGH | Medium (2-3 days) | Foundational architecture, enables caching + taxonomy |
| **Schema.py → pattern schema** | ⭐⭐⭐⭐⭐ (5/5) | 🔥 HIGH | Medium (2-3 days) | Type safety, validation, research coordination |
| **Services Layer → PatternManager** | ⭐⭐⭐⭐ (4/5) | 🔥 MEDIUM-HIGH | High (3-4 days) | Research orchestration, writeback, pipeline |
| **Utils Library → laser helpers** | ⭐⭐⭐⭐ (4/5) | 🔥 MEDIUM | Low (1-2 days) | Quality-of-life, consistency, performance |
| **Modules Pattern → pattern modules** | ⭐⭐⭐ (3/5) | 🟡 LOW-MEDIUM | Low (1-2 days) | Future pattern pages, not immediate |
| **Prompts Directory** | N/A | ❌ SKIP | N/A | Already exists in root |
| **Image Directory** | ⭐ (1/5) | ❌ SKIP | N/A | Not applicable |

**Recommended Implementation Order**:
1. **Phase 1**: PatternDataLoader + Schema.py (foundational, ~4-6 days)
2. **Phase 2**: Utils Library (support for Phase 3, ~1-2 days)
3. **Phase 3**: PatternManager service (orchestration, ~3-4 days)
4. **Phase 4**: Modules pattern (future enhancement, ~1-2 days)

**Total Effort**: ~9-14 days for complete feature parity

---

## Detailed Recommendations

### ✅ IMPLEMENT: PatternDataLoader

**What**: Contamination-specific data loader mirroring CategoryDataLoader

**Why**:
- 11 contamination patterns need centralized data access
- Laser properties research generates large datasets (8 research types × 11 patterns = 88 potential data blobs)
- Performance: LRU caching prevents repeated YAML parsing
- Consistency: Unified API for pattern metadata, laser parameters, safety data

**Architecture**:
```python
# domains/contaminants/pattern_loader.py

class PatternDataLoader:
    """
    Unified pattern data loader with caching.
    
    Single source of truth for contamination pattern data from Contaminants.yaml.
    Mirrors CategoryDataLoader architecture for Materials domain.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.contaminants_file = self._find_contaminants_yaml(project_root)
        self._cache = {}
        self._cache_lock = threading.Lock()
    
    # Metadata loaders
    def get_pattern_metadata(self) -> Dict[str, Any]:
        """Get all pattern descriptions, mechanisms, characteristics"""
        pass
    
    def get_pattern(self, pattern_id: str) -> Dict[str, Any]:
        """Get single pattern data"""
        pass
    
    # Laser property loaders
    def get_optical_properties(
        self,
        pattern_id: Optional[str] = None,
        wavelength: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get optical properties (all patterns or specific)"""
        pass
    
    def get_laser_parameters(
        self,
        pattern_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get recommended laser parameters"""
        pass
    
    def get_safety_data(
        self,
        pattern_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get safety requirements and fume data"""
        pass
    
    # Applicability loaders
    def get_pattern_materials(
        self,
        pattern_id: str
    ) -> Dict[str, List[str]]:
        """Get valid_materials and prohibited_materials for pattern"""
        pass
    
    # Cache management
    def clear_cache(self):
        """Clear internal cache (useful for testing)"""
        pass

# Convenience function
def load_pattern_data(pattern_id: Optional[str] = None) -> Dict[str, Any]:
    """Quick access to pattern data"""
    loader = PatternDataLoader()
    
    if pattern_id is None:
        return loader.get_pattern_metadata()
    
    return loader.get_pattern(pattern_id)
```

**Integration Points**:
- ✅ LaserPropertiesResearcher: Load existing properties before research
- ✅ PatternManager: Gap discovery, validation
- ✅ CLI tools: research_laser_properties.py can use loader instead of direct YAML
- ✅ Validation: Access pattern metadata for completeness checks

**Files to Create**:
1. `domains/contaminants/pattern_loader.py` (300-350 lines)
2. `tests/test_pattern_loader.py` (200-250 lines)

**Estimated Effort**: 2-3 days

---

### ✅ IMPLEMENT: Pattern Schema (schema.py)

**What**: Python dataclasses for contamination patterns with validation

**Why**:
- Type safety: Enforce structure for laser_properties, applicability, pattern metadata
- Validation: Catch missing fields, invalid values, structural errors before data corruption
- Research Integration: `FieldResearchSpec` defines how to AI-research missing data
- Citation Tracking: LaserPropertiesResearcher already generates citations - schema enforces them
- Zero-Fallback Enforcement: Null values MUST have needs_research flag

**Architecture**:
```python
# domains/contaminants/schema.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from shared.schemas.base import ContentSchema, FieldResearchSpec, ResearchMethod, FieldType

@dataclass
class LaserPropertyValue:
    """
    Laser-specific property with comprehensive citations.
    
    Mirrors MaterialPropertyValue architecture for contamination domain.
    """
    # Primary value (None only if needs_research=True)
    value: Optional[float]
    unit: str
    
    # Context
    wavelength: Optional[str] = None  # For wavelength-dependent properties
    material_context: Optional[str] = None  # Substrate material if applicable
    
    # Citation fields (REQUIRED for non-null values)
    source: str  # scientific_literature | materials_database | physics_handbook
    source_type: str  # research_paper | reference_book | physics_database
    source_name: str  # Full source name
    citation: str  # Complete citation with DOI/ISBN/URL
    context: str  # Measurement methodology, conditions
    confidence: int  # 0-100 scale
    
    # Metadata
    researched_date: str  # ISO8601 format
    needs_validation: bool  # True if AI-generated
    
    # NULL handling
    needs_research: bool = False
    research_priority: Optional[str] = None  # high | medium | low
    last_research_attempt: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class OpticalProperties:
    """Optical properties at specific wavelength"""
    wavelength: str  # "1064nm", "532nm", etc.
    absorption_coefficient: LaserPropertyValue
    reflectivity: LaserPropertyValue
    transmittance: Optional[LaserPropertyValue] = None
    refractive_index: Optional[LaserPropertyValue] = None
    extinction_coefficient: Optional[LaserPropertyValue] = None
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate optical properties (absorption + reflection + transmission ≈ 1.0)"""
        errors = []
        
        # Check required fields
        if not self.wavelength:
            errors.append("Missing wavelength")
        
        if self.absorption_coefficient.value is None:
            errors.append("Missing absorption_coefficient value")
        
        if self.reflectivity.value is None:
            errors.append("Missing reflectivity value")
        
        # Physics constraint (if transmission available)
        if (
            self.absorption_coefficient.value is not None and
            self.reflectivity.value is not None and
            self.transmittance and
            self.transmittance.value is not None
        ):
            total = (
                self.absorption_coefficient.value +
                self.reflectivity.value +
                self.transmittance.value
            )
            
            if not (0.95 <= total <= 1.05):  # Allow 5% error
                errors.append(
                    f"Optical properties sum to {total:.3f} (should be ≈1.0)"
                )
        
        return (len(errors) == 0, errors)


@dataclass
class ContaminationPattern(ContentSchema):
    """
    Contamination pattern schema with laser properties.
    
    Extends ContentSchema with pattern-specific fields and validation.
    """
    # Pattern identification
    pattern_id: str
    name: str
    description: str
    removal_mechanism: str  # ablation | vaporization | chemical_decomposition | thermal_shock
    
    # Classification
    severity_levels: List[str] = field(default_factory=list)
    typical_environments: List[str] = field(default_factory=list)
    
    # Laser properties (from LaserPropertiesResearcher)
    optical_properties: Dict[str, OpticalProperties] = field(default_factory=dict)  # wavelength → properties
    thermal_properties: Dict[str, Dict] = field(default_factory=dict)
    removal_characteristics: Dict[str, Dict] = field(default_factory=dict)
    layer_properties: Dict[str, Dict] = field(default_factory=dict)
    laser_parameters: Dict[str, Dict] = field(default_factory=dict)
    safety_data: Dict[str, Dict] = field(default_factory=dict)
    selectivity_ratios: Dict[str, Dict] = field(default_factory=dict)  # material → ratio
    
    # Applicability
    valid_materials: List[str] = field(default_factory=list)
    prohibited_materials: List[str] = field(default_factory=list)
    
    # Metadata
    last_updated: Optional[str] = None
    version: Optional[str] = None
    
    def get_required_fields(self) -> List[str]:
        """Required fields for valid pattern"""
        return [
            'pattern_id',
            'name',
            'description',
            'removal_mechanism',
            'valid_materials'
        ]
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Validate pattern completeness and correctness"""
        errors = []
        
        # Check required fields
        for field_name in self.get_required_fields():
            value = getattr(self, field_name, None)
            
            if value is None or (isinstance(value, (list, dict, str)) and not value):
                errors.append(f"Missing required field: {field_name}")
        
        # Validate removal mechanism
        VALID_MECHANISMS = {
            'ablation', 'vaporization', 'chemical_decomposition',
            'thermal_shock', 'photochemical', 'plasma_formation'
        }
        if self.removal_mechanism not in VALID_MECHANISMS:
            errors.append(f"Invalid removal_mechanism: {self.removal_mechanism}")
        
        # Validate optical properties structure
        for wavelength, opt_props in self.optical_properties.items():
            is_valid, opt_errors = opt_props.validate()
            if not is_valid:
                errors.extend([f"optical_properties.{wavelength}: {e}" for e in opt_errors])
        
        # Validate laser parameters
        if self.laser_parameters:
            required_params = {'recommended_wavelength', 'fluence_range'}
            missing = required_params - set(self.laser_parameters.keys())
            if missing:
                errors.append(f"Missing laser_parameters: {missing}")
        
        # Validate material applicability
        overlap = set(self.valid_materials) & set(self.prohibited_materials)
        if overlap:
            errors.append(f"Materials in both valid and prohibited: {overlap}")
        
        return (len(errors) == 0, errors)
    
    def get_researchable_fields(self) -> Dict[str, FieldResearchSpec]:
        """Define AI research specifications for laser properties"""
        return {
            'optical_properties': FieldResearchSpec(
                field_name='optical_properties',
                field_type=FieldType.PROPERTY,
                data_type='dict',
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/optical_properties.txt',
                validation_rules={
                    'required_wavelengths': ['1064nm', '532nm'],
                    'required_fields': ['absorption_coefficient', 'reflectivity'],
                    'physics_constraint': 'absorption + reflection + transmission ≈ 1.0'
                },
                priority=1  # Critical
            ),
            'thermal_properties': FieldResearchSpec(
                field_name='thermal_properties',
                field_type=FieldType.PROPERTY,
                data_type='dict',
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/thermal_properties.txt',
                validation_rules={
                    'required_fields': [
                        'ablation_threshold',
                        'decomposition_temperature',
                        'thermal_conductivity'
                    ]
                },
                priority=1  # Critical
            ),
            'removal_characteristics': FieldResearchSpec(
                field_name='removal_characteristics',
                field_type=FieldType.PROPERTY,
                data_type='dict',
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/removal_characteristics.txt',
                validation_rules={
                    'required_fields': [
                        'removal_mechanism',
                        'typical_efficiency',
                        'surface_quality'
                    ]
                },
                priority=1  # Critical
            ),
            'laser_parameters': FieldResearchSpec(
                field_name='laser_parameters',
                field_type=FieldType.SPECIFICATION,
                data_type='dict',
                research_method=ResearchMethod.WEB_SEARCH,
                prompt_template='research/prompts/laser_parameters.txt',
                validation_rules={
                    'required_fields': [
                        'recommended_wavelength',
                        'fluence_range',
                        'scan_speed_range'
                    ]
                },
                priority=1  # Critical
            ),
            'safety_data': FieldResearchSpec(
                field_name='safety_data',
                field_type=FieldType.STANDARD,
                data_type='dict',
                research_method=ResearchMethod.DATABASE_LOOKUP,
                prompt_template='research/prompts/safety_data.txt',
                validation_rules={
                    'required_fields': [
                        'fume_composition',
                        'exposure_limits',
                        'ppe_requirements'
                    ]
                },
                priority=2  # Important
            )
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary for YAML export"""
        data = {
            'pattern_id': self.pattern_id,
            'name': self.name,
            'description': self.description,
            'removal_mechanism': self.removal_mechanism,
            'severity_levels': self.severity_levels,
            'typical_environments': self.typical_environments,
            'valid_materials': self.valid_materials,
            'prohibited_materials': self.prohibited_materials
        }
        
        # Add laser properties if present
        if self.optical_properties:
            data['laser_properties'] = {
                'optical_properties': {
                    wl: {
                        'absorption_coefficient': props.absorption_coefficient.__dict__,
                        'reflectivity': props.reflectivity.__dict__
                    }
                    for wl, props in self.optical_properties.items()
                },
                'thermal_properties': self.thermal_properties,
                'removal_characteristics': self.removal_characteristics,
                'layer_properties': self.layer_properties,
                'laser_parameters': self.laser_parameters,
                'safety_data': self.safety_data,
                'selectivity_ratios': self.selectivity_ratios
            }
        
        # Add metadata
        if self.last_updated:
            data['last_updated'] = self.last_updated
        if self.version:
            data['version'] = self.version
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContaminationPattern':
        """Create ContaminationPattern from dictionary (load from Contaminants.yaml)"""
        # Extract laser properties
        laser_props = data.get('laser_properties', {})
        
        return cls(
            content_type='contamination_pattern',
            pattern_id=data.get('pattern_id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            removal_mechanism=data.get('removal_mechanism', ''),
            severity_levels=data.get('severity_levels', []),
            typical_environments=data.get('typical_environments', []),
            optical_properties=laser_props.get('optical_properties', {}),
            thermal_properties=laser_props.get('thermal_properties', {}),
            removal_characteristics=laser_props.get('removal_characteristics', {}),
            layer_properties=laser_props.get('layer_properties', {}),
            laser_parameters=laser_props.get('laser_parameters', {}),
            safety_data=laser_props.get('safety_data', {}),
            selectivity_ratios=laser_props.get('selectivity_ratios', {}),
            valid_materials=data.get('valid_materials', []),
            prohibited_materials=data.get('prohibited_materials', []),
            last_updated=data.get('last_updated'),
            version=data.get('version')
        )
```

**Integration Points**:
- ✅ LaserPropertiesResearcher: Use `get_researchable_fields()` to know what to research
- ✅ PatternManager: Use `validate()` for data quality checks
- ✅ CLI tools: Use `from_dict()`/`to_dict()` for YAML I/O
- ✅ Contaminants.yaml: Structured persistence with type safety

**Files to Create**:
1. `domains/contaminants/schema.py` (500-600 lines)
2. `tests/test_contaminants_schema.py` (300-400 lines)

**Estimated Effort**: 2-3 days

---

### ✅ IMPLEMENT: PatternManager Service (Optional - High Value)

**What**: Service layer for pattern research orchestration

**Why**:
- Gap Discovery: Automatically identify missing laser properties across all patterns
- Research Coordination: Orchestrate LaserPropertiesResearcher for batch operations
- Validation: Ensure researched data meets physical constraints
- Writeback: Persist results to Contaminants.yaml with backup
- Pipeline: Multi-step research (optical → thermal → removal → safety)

**Architecture**: See "Services Layer" section above for full implementation

**Files to Create**:
1. `domains/contaminants/services/pattern_manager.py` (600-700 lines)
2. `tests/test_pattern_manager.py` (400-500 lines)

**Estimated Effort**: 3-4 days

---

### ✅ IMPLEMENT: Utils Library

**What**: Reusable utilities for laser property operations

**Why**: Consistency, performance, code reuse

**Files to Create**:
1. `domains/contaminants/utils/laser_property_helpers.py` (200-250 lines)
2. `domains/contaminants/utils/pattern_cache.py` (150-200 lines)
3. `tests/test_laser_property_helpers.py` (200-250 lines)

**Estimated Effort**: 1-2 days

---

### 🟡 CONSIDER: Modules Pattern (Future)

**What**: Modular pattern page generation

**When**: When generating contamination pattern pages (not yet implemented)

**Files to Create**:
1. `domains/contaminants/modules/pattern_metadata_module.py`
2. `domains/contaminants/modules/laser_properties_module.py`
3. `domains/contaminants/modules/applicability_module.py`

**Estimated Effort**: 1-2 days (when needed)

---

## Summary of Recommendations

### ✅ IMPLEMENTED (Phase 1 - COMPLETE)

1. **PatternDataLoader** ✅ COMPLETE (466 lines, ~2 hours)
   - Centralizes pattern data access
   - LRU caching for performance
   - Unified API for laser properties
   - **Benefit**: Foundation for all other components
   - **Status**: All tests passing (11 patterns detected)

2. **Utils Library** ✅ COMPLETE (652 lines, ~2 hours)
   - Laser property helpers (424 lines)
   - Unit normalization (6 utility functions)
   - Pattern caching (228 lines)
   - **Benefit**: Consistency, code reuse
   - **Status**: All tests passing (17/17 test cases)

**Phase 1 Total**: 1,352 lines (production + tests), ~2 hours implementation  
**Test Results**: 4/4 test suites passing ✅  
**Documentation**: `PHASE1_COMPLETE_NOV25_2025.md`

### 🔄 PENDING (Phase 2 - Optional)

3. **Schema.py** (2-3 days)
   - Type-safe pattern structure
   - Comprehensive validation
   - Research coordination
   - **Benefit**: Data quality, fail-fast architecture
   - **Note**: Can be implemented later if type safety becomes priority

### ✅ IMPLEMENT NEXT (Medium Priority)

4. **PatternManager Service** (3-4 days)
   - Research orchestration
   - Gap discovery
   - Validation pipeline
   - YAML writeback
   - **Benefit**: Complete research automation

### 🟡 CONSIDER LATER (Low Priority)

5. **Modules Pattern** (1-2 days)
   - Pattern page generation
   - Frontmatter extraction
   - **When**: When implementing pattern page publishing

### ❌ SKIP

6. **Prompts Directory** - Already handled by root `prompts/`
7. **Image Directory** - Not applicable to contamination patterns

---

## Total Implementation Estimate

**Phase 1 (High Priority)**: 5-7 days
- PatternDataLoader (2-3 days)
- Schema.py (2-3 days)
- Utils Library (1-2 days)

**Phase 2 (Medium Priority)**: 3-4 days
- PatternManager Service (3-4 days)

**Phase 3 (Future)**: 1-2 days
- Modules Pattern (when pattern pages needed)

**Total**: 9-13 days for complete Materials feature parity in Contaminants domain

---

## Next Steps

**Immediate Action**:
1. Review this analysis with user
2. Get approval for Phase 1 implementation
3. Create implementation plan for PatternDataLoader
4. Begin development of schema.py

**Questions for User**:
1. Approve Phase 1 implementation (PatternDataLoader + Schema + Utils)?
2. Timeline preference (all at once vs incremental)?
3. Any specific features to prioritize or skip?
4. Should PatternManager be part of Phase 1 (increase to 8-11 days)?

---

## Conclusion

Materials domain has **7 architectural components** that enhance functionality, code quality, and maintainability. Of these, **4 are highly recommended** for Contaminants domain:

1. ✅ **PatternDataLoader** - Foundational data access layer
2. ✅ **Schema.py** - Type safety and validation
3. ✅ **Services Layer** - Research orchestration
4. ✅ **Utils Library** - Reusable utilities

Implementing these components will bring Contaminants domain to **feature parity** with Materials, enabling:
- Efficient laser property data management
- Automated research with validation
- Type-safe operations
- Performance optimization through caching
- Consistent architecture across domains

**Recommendation**: Implement Phase 1 (5-7 days) to establish foundation, then evaluate need for PatternManager service.
