#!/usr/bin/env python3
"""
Material Prompts - Specialized prompts for material articles
"""

class MaterialPrompts:
    """Material-specific prompts for metadata and tag generation"""
    
    @staticmethod
    def get_prompts() -> dict:
        """Get all material-specific prompts"""
        return {
            "material_properties": """
Generate comprehensive material properties for {material} in JSON format.

Focus on laser cleaning applications with these required fields:
- atomicNumber, chemicalSymbol, generalClassifier, materialClass
- crystalStructure, density, meltingPoint, thermalConductivity
- reflectivityIr, reflectivityWavelength, hardnessMohs, youngsModulus
- specificHeatCapacity, materialPurity, materialType
- applications (array), safetyConsiderations (array)
- laserCleaningParameters (object), performanceMetrics (object)

Return ONLY valid JSON. No markdown, no explanations.
""",
            
            "material_applications": """
Generate industrial applications for {material} laser cleaning.

Focus on:
- Primary industries using {material}
- Specific components and parts
- Quality requirements
- Performance benefits

Return structured data for industrial applications.
""",
            
            "material_tags": """
Generate 12-15 SEO-optimized hashtags for {material} laser cleaning.

Include:
- Material name: #{material_title}
- Material classification tags
- Industry application tags
- Process technology tags
- Quality and performance tags

Return hashtags separated by commas.
"""
        }