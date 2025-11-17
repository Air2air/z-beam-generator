# Research Pipeline API Reference

## Overview

This document provides comprehensive API documentation for all classes, methods, and interfaces in the Research Pipeline system. The API is designed for extensibility, reliability, and ease of integration with existing Z-Beam Generator components.

## Core Classes

### ResearchPipelineManager

**Location**: `components/frontmatter/research/research_pipeline.py`

The primary orchestrator for the research pipeline workflow.

#### Constructor
```python
class ResearchPipelineManager:
    def __init__(self, 
                 min_confidence_threshold: int = 40,
                 enable_caching: bool = True,
                 api_timeout: int = 30):
        """
        Initialize the research pipeline manager.
        
        Args:
            min_confidence_threshold: Minimum confidence score to accept results (default: 40)
            enable_caching: Enable result caching to reduce API calls (default: True)
            api_timeout: Timeout in seconds for API calls (default: 30)
        """
```

#### Primary Methods

##### `execute_complete_pipeline()`
```python
def execute_complete_pipeline(self, 
                            material_name: str, 
                            material_category: str) -> Dict[str, Dict]:
    """
    Execute the complete research pipeline for a material.
    
    Args:
        material_name: Name of the material to research (e.g., "Zirconia")
        material_category: Material category ("ceramic", "metal", "plastic")
    
    Returns:
        Dict containing:
        {
            "materialProperties": {
                "density": {"value": 5.68, "unit": "g/cm³", "confidence": 95},
                "meltingPoint": {"value": 2715, "unit": "°C", "confidence": 90},
                ...
            },
            "machineSettings": {
                "powerRange": {"value": 120, "unit": "W", "min": 120.0, "max": 420.0, "confidence": 85},
                "wavelength": {"value": 1064, "unit": "nm", "confidence": 95},
                ...
            }
        }
    
    Raises:
        ResearchPipelineError: If pipeline execution fails completely
        PropertyDiscoveryError: If property discovery fails
        ValidationError: If result validation fails
    
    Example:
        pipeline = ResearchPipelineManager()
        results = pipeline.execute_complete_pipeline("Zirconia", "ceramic")
        density = results["materialProperties"]["density"]["value"]
    """
```

##### `research_material_properties()`
```python
def research_material_properties(self, 
                               material_name: str, 
                               applicable_properties: List[str]) -> Dict[str, Dict]:
    """
    Research material properties from a list of applicable property names.
    
    Args:
        material_name: Name of the material to research
        applicable_properties: List of property names to research
    
    Returns:
        Dict mapping property names to PropertyDataMetric structures
    
    Example:
        properties = ["density", "meltingPoint", "thermalConductivity"]
        results = pipeline.research_material_properties("Aluminum", properties)
    """
```

##### `research_machine_settings()`
```python
def research_machine_settings(self, 
                            material_name: str, 
                            material_properties: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Research laser machine settings based on material properties.
    
    Args:
        material_name: Name of the material
        material_properties: Previously researched material properties
    
    Returns:
        Dict mapping setting names to PropertyDataMetric structures
    
    Example:
        mat_props = {"density": {"value": 2.7, "unit": "g/cm³"}}
        settings = pipeline.research_machine_settings("Aluminum", mat_props)
    """
```

#### Utility Methods

##### `validate_complete_dataset()`
```python
def validate_complete_dataset(self, dataset: Dict[str, Dict]) -> bool:
    """
    Validate complete dataset for consistency and completeness.
    
    Args:
        dataset: Complete dataset with materialProperties and machineSettings
    
    Returns:
        bool: True if dataset is valid
    
    Raises:
        ValidationError: If validation fails with detailed error message
    """
```

##### `get_pipeline_statistics()`
```python
def get_pipeline_statistics(self) -> Dict[str, Any]:
    """
    Get statistics about pipeline execution performance.
    
    Returns:
        Dict with execution metrics:
        {
            "total_executions": int,
            "successful_executions": int, 
            "average_execution_time": float,
            "cache_hit_rate": float,
            "api_call_count": int
        }
    """
```

### MaterialPropertyDiscoverer

**Location**: `components/frontmatter/research/research_pipeline.py`

Discovers applicable properties for materials based on category and characteristics.

#### Constructor
```python
class MaterialPropertyDiscoverer:
    def __init__(self, 
                 property_database_path: Optional[str] = None,
                 custom_property_maps: Optional[Dict[str, List[str]]] = None):
        """
        Initialize property discoverer.
        
        Args:
            property_database_path: Path to external property database (optional)
            custom_property_maps: Custom property mappings for categories (optional)
        """
```

#### Primary Methods

##### `discover_applicable_properties()`
```python
def discover_applicable_properties(self, 
                                 material_name: str, 
                                 material_category: str,
                                 include_optional: bool = True) -> List[str]:
    """
    Discover properties applicable to the material.
    
    Args:
        material_name: Name of the material
        material_category: Category ("ceramic", "metal", "plastic")
        include_optional: Include optional/less critical properties (default: True)
    
    Returns:
        List of property names ordered by importance for laser processing
    
    Example:
        discoverer = MaterialPropertyDiscoverer()
        properties = discoverer.discover_applicable_properties("Zirconia", "ceramic")
        # Returns: ["density", "meltingPoint", "thermalConductivity", "hardness", ...]
    """
```

##### `get_property_importance_score()`
```python
def get_property_importance_score(self, 
                                property_name: str, 
                                material_category: str) -> int:
    """
    Get importance score for a property in laser processing context.
    
    Args:
        property_name: Name of the property
        material_category: Material category
    
    Returns:
        int: Importance score (1=critical, 2=important, 3=useful, 4=optional)
    
    Example:
        score = discoverer.get_property_importance_score("density", "ceramic")
        # Returns: 1 (critical for laser processing calculations)
    """
```

##### `get_category_property_map()`
```python
def get_category_property_map(self, material_category: str) -> List[str]:
    """
    Get complete property list for a material category.
    
    Args:
        material_category: Material category
    
    Returns:
        List of all properties defined for the category
    
    Example:
        ceramic_props = discoverer.get_category_property_map("ceramic")
    """
```

#### Utility Methods

##### `filter_properties_for_material()`
```python
def filter_properties_for_material(self, 
                                 material_name: str, 
                                 base_properties: List[str]) -> List[str]:
    """
    Apply material-specific filters to base property list.
    
    Args:
        material_name: Specific material name
        base_properties: Base property list from category
    
    Returns:
        Filtered property list
    """
```

##### `add_custom_property_mapping()`
```python
def add_custom_property_mapping(self, 
                              category: str, 
                              properties: List[str]) -> None:
    """
    Add custom property mapping for a category.
    
    Args:
        category: Material category
        properties: List of properties for the category
    """
```

### PropertyResearcher

**Location**: `components/frontmatter/research/research_pipeline.py`

Handles individual property research using multiple sources and validation.

#### Constructor
```python
class PropertyResearcher:
    def __init__(self, 
                 api_client: Optional[Any] = None,
                 enable_web_research: bool = True,
                 enable_ai_research: bool = True,
                 min_confidence_threshold: int = 40):
        """
        Initialize property researcher.
        
        Args:
            api_client: External API client for research (optional)
            enable_web_research: Enable web API research (default: True)
            enable_ai_research: Enable AI-powered research (default: True)
            min_confidence_threshold: Minimum confidence to accept results (default: 40)
        """
```

#### Primary Methods

##### `research_property()`
```python
def research_property(self, 
                    material_name: str, 
                    property_name: str,
                    context: Optional[Dict] = None) -> Optional[PropertyResult]:
    """
    Research a specific property for a material.
    
    Args:
        material_name: Name of the material
        property_name: Name of the property to research
        context: Additional context for research (optional)
    
    Returns:
        PropertyResult object or None if research fails
    
    Example:
        researcher = PropertyResearcher()
        result = researcher.research_property("Zirconia", "density")
        if result:
            print(f"Density: {result.value} {result.unit}")
    """
```

##### `research_property_batch()`
```python
def research_property_batch(self, 
                          material_name: str, 
                          property_names: List[str],
                          parallel: bool = False) -> Dict[str, Optional[PropertyResult]]:
    """
    Research multiple properties for a material.
    
    Args:
        material_name: Name of the material
        property_names: List of property names to research
        parallel: Enable parallel processing (default: False, respects API limits)
    
    Returns:
        Dict mapping property names to PropertyResult objects
    
    Example:
        results = researcher.research_property_batch("Steel", ["density", "meltingPoint"])
    """
```

##### `validate_property_result()`
```python
def validate_property_result(self, 
                           result: PropertyResult, 
                           property_name: str,
                           material_category: str = None) -> PropertyResult:
    """
    Validate property result for physical and logical consistency.
    
    Args:
        result: Property research result
        property_name: Name of the property
        material_category: Material category for context (optional)
    
    Returns:
        Validated PropertyResult (may have adjusted confidence)
    
    Raises:
        ValidationError: If result fails validation
    """
```

#### Research Strategy Methods

##### `research_with_ai()`
```python
def research_with_ai(self, 
                   material_name: str, 
                   property_name: str) -> Optional[PropertyResult]:
    """
    Research property using AI with contextual prompting.
    
    Args:
        material_name: Name of the material
        property_name: Name of the property
    
    Returns:
        PropertyResult from AI research or None
    """
```

##### `research_with_web_api()`
```python
def research_with_web_api(self, 
                        material_name: str, 
                        property_name: str) -> Optional[PropertyResult]:
    """
    Research property using web APIs and databases.
    
    Args:
        material_name: Name of the material  
        property_name: Name of the property
    
    Returns:
        PropertyResult from web research or None
    """
```

##### `generate_estimated_value()`
```python
def generate_estimated_value(self, 
                           material_name: str, 
                           property_name: str) -> PropertyResult:
    """
    Generate estimated value when other research methods fail.
    
    Args:
        material_name: Name of the material
        property_name: Name of the property
    
    Returns:
        PropertyResult with estimated value and low confidence
    """
```

## Data Structures

### PropertyResult

Primary data structure for individual property research results.

```python
@dataclass
class PropertyResult:
    """Result of property research operation."""
    
    value: Union[float, int, str]
    unit: Optional[str] = None
    min_range: Optional[float] = None
    max_range: Optional[float] = None
    confidence: Optional[int] = None
    source: Optional[str] = None
    research_notes: Optional[str] = None
    cached_at: Optional[datetime] = None
    
    def to_property_data_metric(self) -> Dict[str, Any]:
        """Convert to PropertyDataMetric format."""
        result = {"value": self.value}
        
        if self.unit:
            result["unit"] = self.unit
        if self.min_range is not None:
            result["min"] = self.min_range
        if self.max_range is not None:
            result["max"] = self.max_range
        if self.confidence is not None:
            result["confidence"] = self.confidence
            
        return result
    
    def is_valid(self) -> bool:
        """Check if result has valid data."""
        return (self.value is not None and 
                self.confidence is not None and 
                self.confidence > 0)
```

### ResearchContext

Context object for providing additional information to research methods.

```python
@dataclass 
class ResearchContext:
    """Context information for property research."""
    
    material_category: str
    existing_properties: Dict[str, Any]
    laser_application: str = "cleaning"
    wavelength: Optional[str] = "1064nm"
    priority_level: int = 1  # 1=critical, 2=important, 3=useful
    custom_requirements: Optional[Dict[str, Any]] = None
```

### PipelineConfiguration

Configuration object for pipeline behavior customization.

```python
@dataclass
class PipelineConfiguration:
    """Configuration for research pipeline behavior."""
    
    # Research settings
    min_confidence_threshold: int = 40
    enable_ai_research: bool = True
    enable_web_research: bool = True
    enable_caching: bool = True
    
    # Timeout settings
    api_timeout: int = 30
    total_pipeline_timeout: int = 300
    
    # Retry settings
    max_retries_per_property: int = 3
    retry_backoff_factor: float = 2.0
    
    # Quality settings
    require_units: bool = True
    require_sources: bool = False
    validate_physical_constraints: bool = True
```

## Exception Hierarchy

### Base Exceptions

```python
class ResearchPipelineError(Exception):
    """Base exception for all pipeline-related errors."""
    pass

class ConfigurationError(ResearchPipelineError):
    """Configuration or setup related errors."""
    pass

class PropertyDiscoveryError(ResearchPipelineError):
    """Errors during property discovery phase."""
    pass

class PropertyResearchError(ResearchPipelineError):
    """Errors during individual property research."""
    pass

class ValidationError(ResearchPipelineError):
    """Data validation errors."""
    pass

class APIError(ResearchPipelineError):
    """External API communication errors."""
    pass

class TimeoutError(ResearchPipelineError):
    """Operation timeout errors."""
    pass
```

### Specific Exceptions

```python
class InsufficientDataError(PropertyResearchError):
    """Raised when insufficient data is found for a property."""
    pass

class ConflictingDataError(ValidationError):
    """Raised when research sources provide conflicting data."""
    pass

class PhysicalConstraintViolationError(ValidationError):
    """Raised when property values violate physical constraints."""
    pass

class APIQuotaExceededError(APIError):
    """Raised when API usage quota is exceeded."""
    pass

class UnsupportedMaterialError(PropertyDiscoveryError):
    """Raised when material category is not supported."""
    pass
```

## Integration Interfaces

### Generator Integration Interface

Interface for integrating with existing property generators.

```python
class PropertyGeneratorInterface:
    """Interface for property generator integration."""
    
    def generate_properties_for_material(self, 
                                       material_name: str, 
                                       existing_data: Optional[Dict] = None) -> Dict:
        """Generate properties for a material."""
        raise NotImplementedError
    
    def supports_material_category(self, category: str) -> bool:
        """Check if generator supports material category."""
        raise NotImplementedError
    
    def get_supported_properties(self) -> List[str]:
        """Get list of properties this generator can produce."""
        raise NotImplementedError
```

### Cache Interface

Interface for result caching implementations.

```python
class ResearchCacheInterface:
    """Interface for research result caching."""
    
    def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get cached result by key."""
        raise NotImplementedError
    
    def set_cached_result(self, cache_key: str, result: Any, ttl: int = 3600) -> None:
        """Cache result with optional TTL."""
        raise NotImplementedError
    
    def clear_cache(self, pattern: Optional[str] = None) -> None:
        """Clear cache entries matching pattern."""
        raise NotImplementedError
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        raise NotImplementedError
```

## Usage Examples

### Basic Pipeline Usage

```python
# Initialize pipeline
pipeline = ResearchPipelineManager(
    min_confidence_threshold=60,
    enable_caching=True
)

# Execute complete research
results = pipeline.execute_complete_pipeline("Titanium", "metal")

# Access results
material_props = results["materialProperties"]
machine_settings = results["machineSettings"]

# Extract specific values
density = material_props["density"]["value"]
density_unit = material_props["density"]["unit"]
laser_power = machine_settings["powerRange"]["value"]
```

### Custom Property Research

```python
# Initialize components separately
discoverer = MaterialPropertyDiscoverer()
researcher = PropertyResearcher(min_confidence_threshold=70)

# Discover properties
properties = discoverer.discover_applicable_properties("Copper", "metal")

# Research specific properties
results = {}
for prop in properties[:3]:  # Research top 3 properties
    result = researcher.research_property("Copper", prop)
    if result and result.is_valid():
        results[prop] = result.to_property_data_metric()
```

### Error Handling Example

```python
try:
    pipeline = ResearchPipelineManager()
    results = pipeline.execute_complete_pipeline("UnknownMaterial", "unknown")
    
except PropertyDiscoveryError as e:
    print(f"Could not discover properties: {e}")
    # Fallback to basic property set
    
except ValidationError as e:
    print(f"Data validation failed: {e}")
    # Review and correct data
    
except APIError as e:
    print(f"API communication failed: {e}")
    # Retry with different research method
    
except ResearchPipelineError as e:
    print(f"Pipeline failed: {e}")
    # Fallback to legacy generation method
```

### Custom Configuration

```python
# Create custom configuration
config = PipelineConfiguration(
    min_confidence_threshold=80,
    enable_ai_research=True,
    enable_web_research=False,  # Disable web research
    api_timeout=60,
    max_retries_per_property=5
)

# Initialize with custom config
pipeline = ResearchPipelineManager(config=config)

# Custom property mappings
discoverer = MaterialPropertyDiscoverer()
discoverer.add_custom_property_mapping("composite", [
    "fiberVolumeFraction", "matrixMaterial", "reinforcementType"
])
```

## Testing Interface

### Mock Classes for Testing

```python
class MockPropertyResearcher(PropertyResearcher):
    """Mock researcher for testing without API calls."""
    
    def __init__(self, mock_results: Dict[str, PropertyResult]):
        super().__init__(enable_web_research=False, enable_ai_research=False)
        self.mock_results = mock_results
    
    def research_property(self, material_name: str, property_name: str, context=None):
        key = f"{material_name}:{property_name}"
        return self.mock_results.get(key)
```

### Test Utilities

```python
def create_test_property_result(value: Any, 
                              unit: str = None, 
                              confidence: int = 75) -> PropertyResult:
    """Create PropertyResult for testing."""
    return PropertyResult(
        value=value,
        unit=unit,
        confidence=confidence,
        source="test"
    )

def validate_property_data_metric(data: Dict) -> bool:
    """Validate PropertyDataMetric structure for testing."""
    if not isinstance(data, dict):
        return False
    
    if "value" not in data:
        return False
    
    optional_fields = ["unit", "min", "max", "confidence"]
    for field in data:
        if field not in ["value"] + optional_fields:
            return False
    
    return True
```

This API reference provides complete documentation for all public interfaces in the Research Pipeline system. Developers can use this reference to integrate with the pipeline, extend functionality, and build custom research implementations.