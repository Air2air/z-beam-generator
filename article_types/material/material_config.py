#!/usr/bin/env python3
"""
Material Config - Configuration for material articles
"""

class MaterialConfig:
    """Configuration for material-type articles"""
    
    @staticmethod
    def get_config() -> dict:
        """Get material-specific configuration"""
        return {
            "required_fields": [
                "atomicNumber", "chemicalSymbol", "generalClassifier",
                "materialClass", "density", "meltingPoint"
            ],
            "optional_fields": [
                "crystalStructure", "thermalConductivity", "reflectivityIr",
                "hardnessMohs", "youngsModulus", "specificHeatCapacity"
            ],
            "tag_categories": [
                "material_identity", "material_properties", "applications",
                "industries", "processes", "quality_metrics"
            ],
            "max_tags": 15,
            "technical_depth": "high",
            "target_audience": ["engineers", "technicians", "manufacturers"]
        }