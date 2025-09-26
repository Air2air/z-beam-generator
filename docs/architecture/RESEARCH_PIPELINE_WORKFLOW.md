# Research Pipeline Workflow Documentation

## Overview

The Research Pipeline Workflow represents the systematic process by which the Z-Beam Generator discovers, researches, validates, and populates material properties and machine settings. This workflow transforms the user's request for material-specific laser cleaning parameters into a comprehensive, research-backed dataset.

## Complete Workflow Sequence

### Phase 1: Material Analysis and Categorization

#### Input Processing
```python
# Workflow initiation
material_name = "Zirconia"
existing_data = load_existing_material_data(material_name)  # Optional
```

#### Material Categorization
```python
def determine_material_category(material_name: str, existing_data: Optional[Dict]) -> str:
    """
    Categorize material for targeted property discovery
    
    Categories:
    - ceramic: Zirconia, Alumina, Silicon Carbide, etc.
    - metal: Aluminum, Steel, Titanium, etc. 
    - plastic: Polyethylene, Polypropylene, ABS, etc.
    """
    
    # Priority 1: Explicit category from existing data
    if existing_data and existing_data.get("category"):
        return existing_data["category"]
    
    # Priority 2: Material name pattern matching
    material_lower = material_name.lower()
    
    ceramic_indicators = ["zirconia", "alumina", "ceramic", "oxide"]
    metal_indicators = ["aluminum", "steel", "titanium", "alloy"]
    plastic_indicators = ["poly", "plastic", "polymer", "pvc"]
    
    for indicator in ceramic_indicators:
        if indicator in material_lower:
            return "ceramic"
    # ... similar logic for other categories
    
    return "ceramic"  # Conservative default
```

### Phase 2: Property Discovery

#### Discover Applicable Properties
```python
class MaterialPropertyDiscoverer:
    def discover_applicable_properties(self, material_name: str, material_category: str) -> List[str]:
        """
        Discover properties relevant to the material category
        
        Discovery Process:
        1. Load category-specific property templates
        2. Apply material-specific filters
        3. Prioritize by importance for laser processing
        4. Return ordered property list
        """
        
        # Category-specific property sets
        property_maps = {
            "ceramic": [
                "density", "meltingPoint", "thermalConductivity",
                "hardness", "thermalShockResistance", "compressiveStrength",
                "thermalExpansionCoefficient", "specificHeat"
            ],
            "metal": [
                "density", "meltingPoint", "thermalConductivity", 
                "yieldStrength", "ultimateTensileStrength", "elasticModulus",
                "thermalExpansionCoefficient", "electricalConductivity"
            ],
            "plastic": [
                "density", "glassTradition", "thermalConductivity",
                "tensileStrength", "flexuralModulus", "impactStrength",
                "thermalExpansionCoefficient", "meltingPoint"
            ]
        }
        
        base_properties = property_maps.get(material_category, property_maps["ceramic"])
        
        # Apply material-specific filters
        applicable_properties = self._filter_properties_for_material(
            material_name, base_properties
        )
        
        return applicable_properties
```

#### Property Prioritization
```python
def prioritize_properties_for_laser_processing(properties: List[str]) -> List[str]:
    """
    Prioritize properties by importance for laser cleaning applications
    
    Priority Levels:
    1. Critical: Essential for laser parameter calculation
    2. Important: Significantly affects processing
    3. Useful: Provides additional context
    """
    
    priority_map = {
        # Critical properties
        "density": 1,
        "meltingPoint": 1,
        "thermalConductivity": 1,
        
        # Important properties
        "hardness": 2,
        "thermalShockResistance": 2,
        "absorptionCoefficient": 2,
        
        # Useful properties
        "compressiveStrength": 3,
        "electricalConductivity": 3,
        "specificHeat": 3
    }
    
    return sorted(properties, key=lambda p: priority_map.get(p, 4))
```

### Phase 3: Property Research

#### Individual Property Research
```python
class PropertyResearcher:
    def research_property(self, material_name: str, property_name: str) -> PropertyResult:
        """
        Research individual property using multiple sources
        
        Research Strategy:
        1. AI-powered research with contextual prompting
        2. Web API database lookup
        3. Fallback to estimated values
        4. Confidence scoring and validation
        """
        
        # Research attempt sequence
        research_methods = [
            self._research_with_ai,
            self._research_with_web_api,  
            self._research_with_database_lookup,
            self._generate_estimated_value
        ]
        
        for method in research_methods:
            try:
                result = method(material_name, property_name)
                if result and result.confidence >= self.min_confidence_threshold:
                    return result
            except Exception as e:
                self._log_research_failure(method.__name__, e)
                continue
        
        # If all methods fail, return low-confidence placeholder
        return PropertyResult(
            value=None,
            unit=self._get_standard_unit(property_name),
            confidence=10,
            source="placeholder"
        )
```

#### AI-Powered Research
```python
def _research_with_ai(self, material_name: str, property_name: str) -> PropertyResult:
    """
    Use AI to research property with contextual prompting
    
    Prompt Engineering:
    - Material-specific context
    - Property definition and measurement methods
    - Request for sources and confidence assessment
    """
    
    research_prompt = f"""
    Research the {property_name} of {material_name} for laser cleaning applications.
    
    Requirements:
    1. Provide the most accurate value with measurement unit
    2. Include typical range (min-max) if applicable
    3. Cite authoritative sources (standards, publications, manufacturers)
    4. Assess confidence level (0-100) based on source reliability
    
    Focus on properties relevant to laser processing at 1064nm wavelength.
    """
    
    ai_response = self.ai_client.research(research_prompt)
    
    # Parse AI response and extract structured data
    parsed_result = self._parse_ai_research_response(ai_response)
    
    # Validate and score result
    return self._validate_and_score_result(parsed_result, source="ai_research")
```

#### Web API Research
```python
def _research_with_web_api(self, material_name: str, property_name: str) -> PropertyResult:
    """
    Research using materials databases and web APIs
    
    API Sources:
    - Materials Project API
    - NIST Chemistry WebBook
    - MatWeb Database
    - Manufacturer databases
    """
    
    # Try multiple API sources
    api_sources = [
        ("materials_project", self._query_materials_project),
        ("nist_webbook", self._query_nist_webbook),
        ("matweb", self._query_matweb_database)
    ]
    
    for source_name, api_method in api_sources:
        try:
            result = api_method(material_name, property_name)
            if result and result.confidence >= 60:
                result.source = source_name
                return result
        except Exception as e:
            self._log_api_failure(source_name, e)
            continue
    
    return None
```

### Phase 4: Property Validation and Structuring

#### Result Validation
```python
def validate_property_result(self, result: PropertyResult, property_name: str) -> PropertyResult:
    """
    Validate property result for physical and logical consistency
    
    Validation Checks:
    1. Physical reasonableness (positive values, realistic ranges)
    2. Unit compatibility and conversion
    3. Cross-property consistency
    4. Source reliability assessment
    """
    
    # Physical validation
    if property_name == "density" and result.value <= 0:
        raise ValidationError("Density must be positive")
    
    if property_name == "meltingPoint" and result.unit == "°C" and result.value < -273:
        raise ValidationError("Temperature below absolute zero")
    
    # Range validation
    if result.min_range and result.max_range:
        if result.min_range >= result.max_range:
            raise ValidationError("Invalid range: min >= max")
        
        if not (result.min_range <= result.value <= result.max_range):
            result.confidence *= 0.8  # Reduce confidence for out-of-range values
    
    return result
```

#### Structured Data Creation
```python
def create_structured_property(self, result: PropertyResult) -> Dict:
    """
    Convert research result to PropertyDataMetric format
    
    Output Structure:
    {
        "value": <number or string>,
        "unit": <string>,          # optional
        "min": <number>,           # optional  
        "max": <number>,           # optional
        "confidence": <integer>    # optional
    }
    """
    
    structured_property = {
        "value": result.value
    }
    
    if result.unit:
        structured_property["unit"] = result.unit
    
    if result.min_range is not None:
        structured_property["min"] = result.min_range
    
    if result.max_range is not None:
        structured_property["max"] = result.max_range
    
    if result.confidence is not None:
        structured_property["confidence"] = result.confidence
    
    return structured_property
```

### Phase 5: Machine Settings Research

#### Laser Parameter Discovery
```python
def research_machine_settings(self, material_name: str, material_properties: Dict) -> Dict:
    """
    Research laser processing parameters based on material properties
    
    Parameter Categories:
    1. Laser characteristics (wavelength, type)
    2. Power and energy settings (power, fluence, threshold)
    3. Timing parameters (pulse duration, repetition rate)
    4. Geometric parameters (spot size, scan speed)
    5. Process parameters (passes, overlap, atmosphere)
    """
    
    # Define laser parameter research priorities
    laser_parameters = [
        "powerRange", "wavelength", "pulseDuration", "spotSize",
        "repetitionRate", "fluenceRange", "ablationThreshold", 
        "laserType", "processingSpeed", "thermalDamageThreshold"
    ]
    
    machine_settings = {}
    
    for parameter in laser_parameters:
        try:
            # Research parameter based on material properties
            result = self._research_laser_parameter(
                material_name, parameter, material_properties
            )
            
            if result:
                machine_settings[parameter] = self.create_structured_property(result)
                
        except Exception as e:
            self._log_parameter_research_failure(parameter, e)
    
    return machine_settings
```

#### Parameter Correlation Analysis
```python
def _research_laser_parameter(self, material_name: str, parameter: str, material_props: Dict) -> PropertyResult:
    """
    Research specific laser parameter with material property correlation
    
    Correlation Logic:
    - High thermal conductivity → Lower fluence requirements
    - High melting point → Higher power requirements  
    - High hardness → Shorter pulse durations
    - High density → Adjusted spot sizes
    """
    
    # Extract relevant material properties
    density = self._extract_property_value(material_props, "density")
    melting_point = self._extract_property_value(material_props, "meltingPoint")
    thermal_conductivity = self._extract_property_value(material_props, "thermalConductivity")
    
    # Parameter-specific research logic
    if parameter == "powerRange":
        return self._research_power_requirements(
            material_name, density, melting_point, thermal_conductivity
        )
    
    elif parameter == "wavelength":
        return self._research_optimal_wavelength(material_name, material_props)
    
    elif parameter == "pulseDuration":
        return self._research_pulse_duration(
            material_name, thermal_conductivity, melting_point
        )
    
    # Default research approach
    return self._research_generic_parameter(material_name, parameter)
```

### Phase 6: Complete Pipeline Orchestration

#### Pipeline Manager Execution
```python
class ResearchPipelineManager:
    def execute_complete_pipeline(self, material_name: str, material_category: str) -> Dict:
        """
        Execute the complete research pipeline workflow
        
        Workflow Steps:
        1. Discover applicable material properties
        2. Research each property systematically  
        3. Validate and structure property data
        4. Research corresponding machine settings
        5. Validate complete dataset
        6. Return structured results
        """
        
        try:
            # Step 1: Property Discovery
            applicable_properties = self.property_discoverer.discover_applicable_properties(
                material_name, material_category
            )
            
            print(f"📋 Discovered {len(applicable_properties)} applicable properties")
            
            # Step 2: Material Properties Research
            material_properties = self.research_material_properties(
                material_name, applicable_properties
            )
            
            print(f"🔬 Researched {len(material_properties)} material properties")
            
            # Step 3: Machine Settings Research  
            machine_settings = self.research_machine_settings(
                material_name, material_properties
            )
            
            print(f"⚙️ Researched {len(machine_settings)} machine settings")
            
            # Step 4: Final Validation
            complete_dataset = {
                "materialProperties": material_properties,
                "machineSettings": machine_settings
            }
            
            self._validate_complete_dataset(complete_dataset)
            
            print(f"✅ Pipeline completed successfully for {material_name}")
            return complete_dataset
            
        except Exception as e:
            print(f"❌ Pipeline failed for {material_name}: {str(e)}")
            raise ResearchPipelineError(f"Complete pipeline execution failed: {str(e)}")
```

#### Working List Management
```python
def research_material_properties(self, material_name: str, applicable_properties: List[str]) -> Dict:
    """
    Research material properties with in-memory working list management
    
    Working List Process:
    1. Create working list of properties to research
    2. Process each property with progress tracking
    3. Update working list with results
    4. Handle failures and retries
    5. Return completed property dataset
    """
    
    # Create working list in memory
    working_list = {
        prop_name: {"status": "pending", "attempts": 0, "result": None}
        for prop_name in applicable_properties
    }
    
    completed_properties = {}
    
    # Process working list sequentially
    for prop_name in applicable_properties:
        print(f"🔍 Researching {prop_name} for {material_name}")
        
        try:
            # Update working list status
            working_list[prop_name]["status"] = "researching"
            working_list[prop_name]["attempts"] += 1
            
            # Research the property
            result = self.property_researcher.research_property(material_name, prop_name)
            
            if result and result.confidence >= self.min_confidence_threshold:
                # Success - structure and store result
                structured_property = self.create_structured_property(result)
                completed_properties[prop_name] = structured_property
                
                working_list[prop_name]["status"] = "completed"
                working_list[prop_name]["result"] = structured_property
                
                print(f"✅ {prop_name}: {result.value} {result.unit or ''} (confidence: {result.confidence}%)")
                
            else:
                # Low confidence or failure
                working_list[prop_name]["status"] = "failed"
                print(f"⚠️ {prop_name}: Low confidence result or research failure")
                
        except Exception as e:
            working_list[prop_name]["status"] = "error"
            print(f"❌ {prop_name}: Research error - {str(e)}")
    
    # Log working list summary
    completed_count = len([w for w in working_list.values() if w["status"] == "completed"])
    print(f"📊 Working list complete: {completed_count}/{len(applicable_properties)} properties researched")
    
    return completed_properties
```

## Workflow Error Handling

### Exception Hierarchy
```python
class ResearchPipelineError(Exception):
    """Base exception for pipeline failures"""
    pass

class PropertyDiscoveryError(ResearchPipelineError):
    """Property discovery phase failure"""
    pass

class PropertyResearchError(ResearchPipelineError):
    """Individual property research failure"""
    pass

class MachineSettingsError(ResearchPipelineError):
    """Machine settings research failure"""
    pass

class ValidationError(ResearchPipelineError):
    """Data validation failure"""
    pass
```

### Recovery Strategies
```python
def handle_research_failure(self, error: Exception, context: Dict) -> Optional[PropertyResult]:
    """
    Handle research failures with graceful degradation
    
    Recovery Strategy:
    1. Retry with different research method
    2. Use cached results if available
    3. Generate estimated values with low confidence
    4. Skip property if all methods fail
    """
    
    if isinstance(error, APITimeoutError):
        # Retry with longer timeout
        return self._retry_with_extended_timeout(context)
    
    elif isinstance(error, APIQuotaExceededError):
        # Switch to alternative research method
        return self._switch_to_fallback_method(context)
    
    elif isinstance(error, ValidationError):
        # Generate conservative estimated value
        return self._generate_conservative_estimate(context)
    
    else:
        # Log and skip property
        self._log_unrecoverable_failure(error, context)
        return None
```

## Performance Optimization

### Caching Strategy
```python
class ResearchCache:
    """Cache research results to minimize API calls and processing time"""
    
    def __init__(self):
        self.property_cache = {}  # Material-property results
        self.material_category_cache = {}  # Material categorizations
        self.api_response_cache = {}  # Raw API responses with TTL
    
    def get_cached_property(self, material_name: str, property_name: str) -> Optional[PropertyResult]:
        """Get cached property result if available and valid"""
        cache_key = f"{material_name}:{property_name}"
        
        cached_result = self.property_cache.get(cache_key)
        if cached_result and not self._is_cache_expired(cached_result):
            return cached_result
        
        return None
    
    def cache_property_result(self, material_name: str, property_name: str, result: PropertyResult):
        """Cache property research result"""
        cache_key = f"{material_name}:{property_name}"
        result.cached_at = datetime.now()
        self.property_cache[cache_key] = result
```

### Parallel Processing
```python
def research_properties_parallel(self, material_name: str, properties: List[str]) -> Dict:
    """
    Research multiple properties in parallel for improved performance
    
    Note: Use with caution for API rate limits
    """
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit research tasks
        future_to_property = {
            executor.submit(self.property_researcher.research_property, material_name, prop): prop
            for prop in properties
        }
        
        results = {}
        
        # Collect results
        for future in as_completed(future_to_property):
            prop_name = future_to_property[future]
            try:
                result = future.result(timeout=30)  # 30 second timeout per property
                if result:
                    results[prop_name] = self.create_structured_property(result)
            except Exception as e:
                print(f"❌ Parallel research failed for {prop_name}: {str(e)}")
        
        return results
```

## Conclusion

The Research Pipeline Workflow provides a systematic, reliable approach to discovering and researching material properties and laser processing parameters. By following this structured workflow, the Z-Beam Generator ensures comprehensive, high-quality data generation that combines multiple research sources with confidence scoring and robust error handling.

The workflow's design emphasizes transparency, reliability, and extensibility, enabling consistent results while accommodating new research methods and data sources as they become available.