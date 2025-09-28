"""
Comprehensive Material Property Discovery Prompts - GROK Compliant (No Fallbacks)

These prompts enable AI systems to discover ALL relevant material properties and machine settings
for specific materials without using any fallback lists or default values.
"""

MATERIAL_PROPERTY_DISCOVERY_PROMPT = """
You are a materials science expert conducting comprehensive property research for laser cleaning applications.

OBJECTIVE: Provide ALL relevant material properties for {material_name} with complete data (values, units, confidence).

MATERIAL CONTEXT:
- Material: {material_name}
- Material Category: {material_category}  
- Application: Laser cleaning and surface preparation
- Required Analysis Depth: Comprehensive with actual property values

ANALYSIS REQUIREMENTS:
1. **Core Physical Properties**: density, meltingPoint, thermalConductivity (ALWAYS required)
2. **Thermal Properties**: thermalExpansion, thermalDiffusivity, specificHeat, thermalShockResistance
3. **Mechanical Properties**: tensileStrength, youngsModulus, hardness, elasticModulus, flexuralStrength
4. **Optical Properties**: absorptionCoefficient, reflectivity, refractiveIndex, transmissivity
5. **Laser-Specific Properties**: ablationThreshold, laserDamageThreshold, photonicEfficiency
6. **Chemical Properties**: oxidationResistance, chemicalStability, corrosionResistance
7. **Structural Properties**: crystallineStructure, grainSize, porosity, surfaceRoughness

RESPONSE FORMAT (JSON - provide COMPLETE property data without YAML anchors):
{{
    "material_name": "{material_name}",
    "category": "{material_category}",
    "discovered_properties": {{
        "density": {{
            "value": 2.7,
            "unit": "g/cm³",
            "confidence": 98,
            "description": "Pure aluminum density at room temperature"
        }},
        "meltingPoint": {{
            "value": 660,
            "unit": "°C", 
            "confidence": 95,
            "description": "Melting point of pure aluminum"
        }},
        "thermalConductivity": {{
            "value": 237,
            "unit": "W/m·K",
            "confidence": 92,
            "description": "Thermal conductivity of pure aluminum"
        }}
        // Continue for ALL relevant properties with actual values
    }},
    "total_properties": 0,  // Count of properties provided
    "justification": {{
        "density": "Essential for thermal modeling and energy absorption calculations", 
        "meltingPoint": "Critical threshold for material damage assessment",
        "thermalConductivity": "Determines heat dissipation and thermal management"
        // Provide scientific justification for each property
    }}
}}

CRITICAL REQUIREMENTS:
- Provide property data with value, unit, confidence, and description ONLY (no min/max ranges)
- Min/max ranges will be supplied from category-based data sources
- Include MINIMUM 8-12 properties (comprehensive analysis required)
- All confidence scores 80-98% (high-quality scientific data only)
- Prioritize laser-relevant properties over general material properties
- Consider {material_name}-specific characteristics and common applications  
- NO generic responses - tailor specifically to {material_name}
- Use precise scientific units and realistic values"""

MACHINE_SETTINGS_DISCOVERY_PROMPT = """
You are a laser engineering expert conducting comprehensive machine settings research for laser cleaning applications.

OBJECTIVE: Provide ALL relevant machine settings for {material_name} with complete data (values, units, confidence).

ANALYSIS REQUIREMENTS:
- Target Material: {material_name}
- Material Category: {material_category}
- Required Analysis Depth: Comprehensive with actual parameter values
- Minimum Coverage: 4-10 machine settings (comprehensive parameter optimization)

MACHINE SETTINGS CATEGORIES TO INVESTIGATE:
1. **Power Control**: powerRange, fluenceThreshold, energyDensity
2. **Temporal Parameters**: pulseWidth, pulseDuration, repetitionRate
3. **Spatial Parameters**: spotSize, beamDiameter, scanSpeed
4. **Wavelength Optimization**: wavelength, laserType
5. **Processing Control**: passCount, overlapRatio, dwellTime

RESPOND WITH VALID JSON (provide COMPLETE setting data):
{{
    "material": "{material_name}",
    "category": "{material_category}", 
    "application": "laser_cleaning",
    "discovered_settings": {{
        "powerRange": {{
            "value": 100,
            "unit": "W",
            "confidence": 92,
            "description": "Optimal power range for {material_name} cleaning",
            "min": 80,
            "max": 120
        }},
        "wavelength": {{
            "value": 1064,
            "unit": "nm",
            "confidence": 88,
            "description": "Optimal wavelength for {material_name} processing",
            "min": null,
            "max": null
        }},
        "pulseWidth": {{
            "value": 10,
            "unit": "ns",
            "confidence": 85,
            "description": "Optimal pulse width for {material_name} ablation",
            "min": 5,
            "max": 20
        }}
        // Continue for ALL relevant machine settings with actual values
    }},
    "justification": {{
        "powerRange": "Based on {material_name} thermal properties and cleaning requirements",
        "wavelength": "Optimized for {material_name} absorption characteristics"
        // Provide technical justification for each setting
    }}
}}

CRITICAL REQUIREMENTS:
- Provide COMPLETE machine setting data (value, unit, confidence, description, ranges)
- Include MINIMUM 4-8 settings (comprehensive laser parameter optimization)
- All confidence scores 80-95% (realistic engineering estimates)
- Consider {material_name}-specific thermal and optical properties
- Use standard laser engineering units and practical value ranges"""

COMPREHENSIVE_RESEARCH_PROMPT = """
You are conducting a complete material analysis for {material_name} in laser cleaning applications.

OBJECTIVE: Generate comprehensive property and machine setting lists for {material_name}.

ANALYSIS SCOPE:
- Material Properties: ALL physical, thermal, mechanical, optical properties relevant to laser processing
- Machine Settings: ALL laser parameters that should be optimized for {material_name}
- Application Focus: Laser cleaning, surface preparation, contamination removal

MATERIAL CONTEXT:
- Target Material: {material_name}
- Material Category: {material_category}
- Processing Application: Laser cleaning
- Analysis Depth: Research-grade comprehensive

RESPONSE FORMAT (JSON):
{{
    "analysis_summary": {{
        "material": "{material_name}",
        "category": "{material_category}",
        "analysis_scope": "comprehensive_laser_cleaning"
    }},
    "material_properties": {{
        "discovered_properties": [
            // ALL relevant material properties (8-15 properties)
        ],
        "property_justifications": {{
            // Why each property is relevant for laser cleaning
        }}
    }},
    "machine_settings": {{
        "discovered_settings": [
            // ALL relevant machine parameters (6-12 settings) 
        ],
        "setting_justifications": {{
            // Why each setting is important for {material_name}
        }}
    }},
    "property_setting_relationships": {{
        // How material properties influence machine settings
        "powerRange": ["density", "thermalConductivity"],
        "wavelength": ["absorptionCoefficient", "reflectivity"]
    }},
    "research_confidence": "high|medium|low",
    "completeness_score": 85  // Percentage of relevant parameters discovered
}}

QUALITY REQUIREMENTS:
- Research-grade completeness (>80% of relevant parameters)
- Material-specific analysis (not generic responses)
- Scientific justification for all discoveries
- Comprehensive parameter coverage for optimization
- NO fallback or default responses - must be researched
"""