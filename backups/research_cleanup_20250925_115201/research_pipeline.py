#!/usr/bin/env python3
"""
Research-Driven Property Generation Pipeline

This module implements a systematic approach to researching, validating, and populating 
material properties and machine settings through online research and verification.

Pipeline Flow:
1. Discover applicable properties for material
2. Create working property list in memory
3. Research, verify, and populate each property
4. Save structured property data
5. Repeat process for machine settings
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import time
from functools import lru_cache


class ResearchStatus(Enum):
    """Status of property research"""
    PENDING = "pending"
    RESEARCHING = "researching"
    VERIFIED = "verified"
    FAILED = "failed"
    COMPLETED = "completed"


class PropertyCategory(Enum):
    """Categories of properties for research prioritization"""
    CORE_PHYSICAL = "core_physical"
    THERMAL = "thermal"
    MECHANICAL = "mechanical"
    OPTICAL = "optical"
    CHEMICAL = "chemical"
    SPECIALIZED = "specialized"


@dataclass
class PropertyResearchItem:
    """Individual property research item"""
    name: str
    category: PropertyCategory
    description: str
    typical_units: List[str]
    research_queries: List[str]
    priority: int = 5  # 1-10, higher is more important
    status: ResearchStatus = ResearchStatus.PENDING
    research_attempts: int = 0
    max_attempts: int = 3
    
    # Research results
    researched_value: Optional[float] = None
    researched_unit: Optional[str] = None
    researched_min: Optional[float] = None
    researched_max: Optional[float] = None
    confidence_score: Optional[int] = None
    sources: List[str] = field(default_factory=list)
    research_notes: str = ""
    
    def to_structured_format(self) -> Dict[str, Any]:
        """Convert to structured property format"""
        if self.status != ResearchStatus.COMPLETED:
            return None
            
        result = {
            'value': self.researched_value,
            'confidence': self.confidence_score or 70
        }
        
        if self.researched_unit:
            result['unit'] = self.researched_unit
        if self.researched_min is not None:
            result['min'] = self.researched_min
        if self.researched_max is not None:
            result['max'] = self.researched_max
            
        return result


@dataclass 
class MachineSettingResearchItem:
    """Individual machine setting research item"""
    name: str
    setting_type: str  # power, duration, wavelength, etc.
    description: str
    typical_units: List[str]
    research_queries: List[str]
    priority: int = 5
    status: ResearchStatus = ResearchStatus.PENDING
    research_attempts: int = 0
    max_attempts: int = 3
    
    # Research results
    researched_value: Optional[Any] = None
    researched_unit: Optional[str] = None
    researched_min: Optional[float] = None
    researched_max: Optional[float] = None
    confidence_score: Optional[int] = None
    sources: List[str] = field(default_factory=list)
    research_notes: str = ""
    
    def to_structured_format(self) -> Dict[str, Any]:
        """Convert to structured machine setting format"""
        if self.status != ResearchStatus.COMPLETED:
            return None
            
        result = {
            'value': self.researched_value,
            'confidence': self.confidence_score or 75
        }
        
        if self.researched_unit:
            result['unit'] = self.researched_unit
        if self.researched_min is not None:
            result['min'] = self.researched_min
        if self.researched_max is not None:
            result['max'] = self.researched_max
            
        return result


class MaterialPropertyDiscoverer:
    """Discovers applicable properties for a given material"""
    
    def __init__(self):
        self.material_property_map = self._load_material_property_mappings()
    
    def discover_applicable_properties(self, material_name: str, material_category: str) -> List[PropertyResearchItem]:
        """Discover what properties are applicable for this material"""
        print(f"🔍 Discovering applicable properties for {material_name} ({material_category})")
        
        properties = []
        
        # Core physical properties (always applicable)
        properties.extend(self._get_core_physical_properties(material_name, material_category))
        
        # Category-specific properties
        if material_category == "ceramic":
            properties.extend(self._get_ceramic_properties(material_name))
        elif material_category == "metal": 
            properties.extend(self._get_metal_properties(material_name))
        elif material_category == "plastic":
            properties.extend(self._get_plastic_properties(material_name))
            
        # Material-specific properties
        properties.extend(self._get_material_specific_properties(material_name))
        
        # Sort by priority
        properties.sort(key=lambda x: x.priority, reverse=True)
        
        print(f"📋 Found {len(properties)} applicable properties for research")
        return properties
    
    def _get_core_physical_properties(self, material_name: str, category: str) -> List[PropertyResearchItem]:
        """Get core physical properties applicable to all materials"""
        return [
            PropertyResearchItem(
                name="density",
                category=PropertyCategory.CORE_PHYSICAL,
                description="Material density",
                typical_units=["g/cm³", "kg/m³"],
                research_queries=[
                    f"{material_name} density",
                    f"{material_name} specific gravity",
                    f"density of {material_name}"
                ],
                priority=10
            ),
            PropertyResearchItem(
                name="meltingPoint",
                category=PropertyCategory.THERMAL,
                description="Melting temperature",
                typical_units=["°C", "K", "°F"],
                research_queries=[
                    f"{material_name} melting point",
                    f"{material_name} melting temperature",
                    f"melting point {material_name}"
                ],
                priority=9
            )
        ]
    
    def _get_ceramic_properties(self, material_name: str) -> List[PropertyResearchItem]:
        """Get properties specific to ceramic materials"""
        return [
            PropertyResearchItem(
                name="thermalConductivity",
                category=PropertyCategory.THERMAL,
                description="Thermal conductivity",
                typical_units=["W/m·K", "W/mK"],
                research_queries=[
                    f"{material_name} thermal conductivity",
                    f"thermal conductivity of {material_name} ceramic",
                    f"{material_name} heat conduction"
                ],
                priority=9
            ),
            PropertyResearchItem(
                name="hardness",
                category=PropertyCategory.MECHANICAL,
                description="Material hardness",
                typical_units=["Mohs", "Vickers HV", "GPa"],
                research_queries=[
                    f"{material_name} hardness Mohs",
                    f"{material_name} Vickers hardness",
                    f"hardness of {material_name}"
                ],
                priority=8
            ),
            PropertyResearchItem(
                name="thermalShockResistance",
                category=PropertyCategory.THERMAL,
                description="Thermal shock resistance",
                typical_units=["°C", "K"],
                research_queries=[
                    f"{material_name} thermal shock resistance",
                    f"{material_name} thermal cycling",
                    f"thermal shock {material_name} ceramic"
                ],
                priority=7
            )
        ]
    
    def _get_metal_properties(self, material_name: str) -> List[PropertyResearchItem]:
        """Get properties specific to metallic materials"""
        return [
            PropertyResearchItem(
                name="thermalConductivity",
                category=PropertyCategory.THERMAL,
                description="Thermal conductivity",
                typical_units=["W/m·K", "W/mK"],
                research_queries=[
                    f"{material_name} thermal conductivity",
                    f"thermal conductivity {material_name} metal",
                    f"{material_name} heat conduction"
                ],
                priority=9
            ),
            PropertyResearchItem(
                name="tensileStrength",
                category=PropertyCategory.MECHANICAL,
                description="Tensile strength",
                typical_units=["MPa", "GPa", "psi"],
                research_queries=[
                    f"{material_name} tensile strength",
                    f"ultimate tensile strength {material_name}",
                    f"{material_name} UTS"
                ],
                priority=8
            )
        ]
    
    def _get_plastic_properties(self, material_name: str) -> List[PropertyResearchItem]:
        """Get properties specific to plastic materials"""
        return [
            PropertyResearchItem(
                name="glassTempearture",
                category=PropertyCategory.THERMAL,
                description="Glass transition temperature",
                typical_units=["°C", "K"],
                research_queries=[
                    f"{material_name} glass transition temperature",
                    f"{material_name} Tg temperature",
                    f"glass transition {material_name}"
                ],
                priority=8
            )
        ]
    
    def _get_material_specific_properties(self, material_name: str) -> List[PropertyResearchItem]:
        """Get properties specific to the particular material"""
        material_specific = {
            "zirconia": [
                PropertyResearchItem(
                    name="ionicConductivity", 
                    category=PropertyCategory.SPECIALIZED,
                    description="Ionic conductivity (for stabilized zirconia)",
                    typical_units=["S/m", "S/cm"],
                    research_queries=[
                        "zirconia ionic conductivity",
                        "yttria stabilized zirconia conductivity",
                        "YSZ ionic conductivity"
                    ],
                    priority=6
                )
            ]
        }
        
        return material_specific.get(material_name.lower(), [])
    
    def _load_material_property_mappings(self) -> Dict:
        """Load material-property mappings"""
        return {}  # Placeholder for future enhancement


class PropertyResearcher:
    """Researches individual properties using online sources"""
    
    def __init__(self):
        self.api_manager = None  # Will be initialized when needed
        self.research_cache = {}
    
    def research_property(self, item: PropertyResearchItem, material_name: str) -> bool:
        """Research a specific property for a material"""
        if item.research_attempts >= item.max_attempts:
            print(f"❌ Max research attempts reached for {item.name}")
            item.status = ResearchStatus.FAILED
            return False
            
        print(f"🔬 Researching {item.name} for {material_name} (attempt {item.research_attempts + 1})")
        item.status = ResearchStatus.RESEARCHING
        item.research_attempts += 1
        
        try:
            # Try web research first
            success = self._perform_web_research(item, material_name)
            
            if not success:
                # Fall back to knowledge base
                success = self._fallback_research(item, material_name)
            
            if success:
                item.status = ResearchStatus.VERIFIED
                print(f"✅ Successfully researched {item.name}: {item.researched_value} {item.researched_unit}")
                return True
            else:
                print(f"⚠️ Research failed for {item.name}")
                return False
                
        except Exception as e:
            print(f"❌ Error researching {item.name}: {str(e)}")
            item.research_notes += f"Error: {str(e)}; "
            return False
    
    def _perform_web_research(self, item: PropertyResearchItem, material_name: str) -> bool:
        """Perform web research using AI API"""
        try:
            # Initialize API manager if needed
            if not self.api_manager:
                from api.client_manager import ClientManager
                self.api_manager = ClientManager()
            
            # Create research prompt
            research_prompt = f"""
            Research the {item.description} of {material_name}.
            
            Please provide:
            1. The typical value with unit
            2. The range (min-max) if applicable  
            3. Confidence in the data (1-100)
            4. Brief source information
            
            Format the response as:
            Value: [number]
            Unit: [unit]
            Range: [min-max] (if applicable)
            Confidence: [1-100]
            Source: [brief source info]
            """
            
            # Try each research query
            for query in item.research_queries:
                try:
                    response = self.api_manager.generate_text(research_prompt, max_tokens=200)
                    if self._parse_research_response(response, item):
                        return True
                except Exception as e:
                    print(f"⚠️ API research failed for query '{query}': {str(e)}")
                    continue
                    
            return False
            
        except Exception as e:
            print(f"⚠️ Web research setup failed: {str(e)}")
            return False
    
    def _parse_research_response(self, response: str, item: PropertyResearchItem) -> bool:
        """Parse AI research response"""
        try:
            # Extract value
            value_match = re.search(r'Value:\s*([0-9.]+)', response, re.IGNORECASE)
            if value_match:
                item.researched_value = float(value_match.group(1))
            else:
                return False
            
            # Extract unit
            unit_match = re.search(r'Unit:\s*([^\n\r]+)', response, re.IGNORECASE)
            if unit_match:
                item.researched_unit = unit_match.group(1).strip()
            
            # Extract range
            range_match = re.search(r'Range:\s*([0-9.]+)\s*[-–—]\s*([0-9.]+)', response, re.IGNORECASE)
            if range_match:
                item.researched_min = float(range_match.group(1))
                item.researched_max = float(range_match.group(2))
            
            # Extract confidence
            conf_match = re.search(r'Confidence:\s*([0-9]+)', response, re.IGNORECASE)
            if conf_match:
                item.confidence_score = int(conf_match.group(1))
            else:
                item.confidence_score = 70  # Default
            
            # Extract source
            source_match = re.search(r'Source:\s*([^\n\r]+)', response, re.IGNORECASE)
            if source_match:
                item.sources.append(source_match.group(1).strip())
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to parse research response: {str(e)}")
            return False
    
    def _fallback_research(self, item: PropertyResearchItem, material_name: str) -> bool:
        """Fallback research using knowledge base"""
        # Implement knowledge-based fallback
        fallback_data = {
            ("zirconia", "density"): {"value": 6.05, "unit": "g/cm³", "confidence": 85},
            ("zirconia", "meltingPoint"): {"value": 2715, "unit": "°C", "confidence": 90},
            ("zirconia", "thermalConductivity"): {"value": 2.5, "unit": "W/m·K", "min": 2.0, "max": 3.0, "confidence": 75},
            ("zirconia", "hardness"): {"value": 8.5, "unit": "Mohs", "confidence": 85},
        }
        
        key = (material_name.lower(), item.name)
        if key in fallback_data:
            data = fallback_data[key]
            item.researched_value = data["value"]
            item.researched_unit = data["unit"]
            item.researched_min = data.get("min")
            item.researched_max = data.get("max")
            item.confidence_score = data["confidence"]
            item.sources.append("Knowledge base fallback")
            print(f"📚 Using fallback data for {item.name}")
            return True
        
        return False


class MachineSettingsDiscoverer:
    """Discovers applicable machine settings for a material and application"""
    
    def discover_applicable_settings(self, material_name: str, material_category: str) -> List[MachineSettingResearchItem]:
        """Discover applicable laser settings for this material"""
        print(f"🔍 Discovering applicable machine settings for {material_name} laser cleaning")
        
        settings = []
        
        # Core laser parameters (always applicable)
        settings.extend(self._get_core_laser_settings(material_name, material_category))
        
        # Material-specific settings
        settings.extend(self._get_material_specific_settings(material_name, material_category))
        
        # Sort by priority
        settings.sort(key=lambda x: x.priority, reverse=True)
        
        print(f"📋 Found {len(settings)} applicable machine settings for research")
        return settings
    
    def _get_core_laser_settings(self, material_name: str, category: str) -> List[MachineSettingResearchItem]:
        """Get core laser settings applicable to all materials"""
        return [
            MachineSettingResearchItem(
                name="powerRange",
                setting_type="power",
                description="Laser power range",
                typical_units=["W", "kW"],
                research_queries=[
                    f"{material_name} laser cleaning power",
                    f"laser power for {material_name} cleaning",
                    f"{material_name} laser ablation power"
                ],
                priority=10
            ),
            MachineSettingResearchItem(
                name="wavelength",
                setting_type="wavelength",
                description="Optimal laser wavelength",
                typical_units=["nm", "μm"],
                research_queries=[
                    f"{material_name} laser cleaning wavelength",
                    f"optimal wavelength {material_name} laser",
                    f"{material_name} absorption wavelength"
                ],
                priority=9
            ),
            MachineSettingResearchItem(
                name="pulseDuration",
                setting_type="temporal",
                description="Pulse duration",
                typical_units=["ns", "ps", "fs"],
                research_queries=[
                    f"{material_name} laser pulse duration",
                    f"pulse width {material_name} cleaning",
                    f"{material_name} laser pulse length"
                ],
                priority=8
            )
        ]
    
    def _get_material_specific_settings(self, material_name: str, category: str) -> List[MachineSettingResearchItem]:
        """Get material-specific laser settings"""
        if category == "ceramic":
            return [
                MachineSettingResearchItem(
                    name="fluenceRange",
                    setting_type="energy",
                    description="Laser fluence range",
                    typical_units=["J/cm²"],
                    research_queries=[
                        f"{material_name} laser fluence",
                        f"fluence threshold {material_name}",
                        f"{material_name} ablation threshold"
                    ],
                    priority=7
                )
            ]
        return []


class ResearchPipelineManager:
    """Orchestrates the complete research pipeline"""
    
    def __init__(self):
        self.property_discoverer = MaterialPropertyDiscoverer()
        self.property_researcher = PropertyResearcher()
        self.settings_discoverer = MachineSettingsDiscoverer()
        self.settings_researcher = PropertyResearcher()  # Reuse for settings
    
    def execute_complete_pipeline(self, material_name: str, material_category: str) -> Dict[str, Any]:
        """Execute the complete research pipeline"""
        print(f"🚀 Starting complete research pipeline for {material_name}")
        
        results = {
            "materialProperties": {},
            "machineSettings": {},
            "research_metadata": {
                "material_name": material_name,
                "material_category": material_category,
                "research_timestamp": time.time(),
                "total_properties_researched": 0,
                "successful_properties": 0,
                "total_settings_researched": 0,
                "successful_settings": 0
            }
        }
        
        # Phase 1: Research Material Properties
        print("\n📊 PHASE 1: Material Properties Research")
        property_results = self._research_material_properties(material_name, material_category)
        results["materialProperties"] = property_results["properties"]
        results["research_metadata"].update(property_results["metadata"])
        
        # Phase 2: Research Machine Settings  
        print("\n⚙️ PHASE 2: Machine Settings Research")
        settings_results = self._research_machine_settings(material_name, material_category)
        results["machineSettings"] = settings_results["settings"]
        results["research_metadata"].update(settings_results["metadata"])
        
        # Summary
        total_success = (results["research_metadata"]["successful_properties"] + 
                        results["research_metadata"]["successful_settings"])
        total_attempted = (results["research_metadata"]["total_properties_researched"] +
                          results["research_metadata"]["total_settings_researched"])
        
        print(f"\n🎯 PIPELINE COMPLETE: {total_success}/{total_attempted} items successfully researched")
        
        return results
    
    def _research_material_properties(self, material_name: str, material_category: str) -> Dict[str, Any]:
        """Phase 1: Research material properties"""
        # Step 1: Discover applicable properties
        properties = self.property_discoverer.discover_applicable_properties(material_name, material_category)
        
        # Step 2: Create working list in memory
        working_properties = {prop.name: prop for prop in properties}
        print(f"📝 Working list created with {len(working_properties)} properties")
        
        # Step 3: Research each property individually
        successful_properties = {}
        successful_count = 0
        
        for prop_name, prop_item in working_properties.items():
            print(f"\n🔬 Researching property: {prop_name}")
            
            success = self.property_researcher.research_property(prop_item, material_name)
            
            if success:
                # Step 4: Validate and populate structured data
                structured_data = prop_item.to_structured_format()
                if structured_data:
                    successful_properties[prop_name] = structured_data
                    successful_count += 1
                    print(f"✅ {prop_name} successfully populated")
                else:
                    print(f"❌ {prop_name} failed validation")
            else:
                print(f"❌ {prop_name} research failed")
            
            # Brief pause between research requests
            time.sleep(0.5)
        
        return {
            "properties": successful_properties,
            "metadata": {
                "total_properties_researched": len(properties),
                "successful_properties": successful_count
            }
        }
    
    def _research_machine_settings(self, material_name: str, material_category: str) -> Dict[str, Any]:
        """Phase 2: Research machine settings"""
        # Step 1: Discover applicable settings
        settings = self.settings_discoverer.discover_applicable_settings(material_name, material_category)
        
        # Step 2: Create working list in memory
        working_settings = {setting.name: setting for setting in settings}
        print(f"📝 Working list created with {len(working_settings)} settings")
        
        # Step 3: Research each setting individually
        successful_settings = {}
        successful_count = 0
        
        for setting_name, setting_item in working_settings.items():
            print(f"\n⚙️ Researching setting: {setting_name}")
            
            # Convert MachineSettingResearchItem to PropertyResearchItem for research
            prop_item = PropertyResearchItem(
                name=setting_item.name,
                category=PropertyCategory.SPECIALIZED,
                description=setting_item.description,
                typical_units=setting_item.typical_units,
                research_queries=setting_item.research_queries,
                priority=setting_item.priority
            )
            
            success = self.settings_researcher.research_property(prop_item, material_name)
            
            if success:
                # Transfer results back
                setting_item.researched_value = prop_item.researched_value
                setting_item.researched_unit = prop_item.researched_unit
                setting_item.researched_min = prop_item.researched_min
                setting_item.researched_max = prop_item.researched_max
                setting_item.confidence_score = prop_item.confidence_score
                setting_item.sources = prop_item.sources
                setting_item.status = ResearchStatus.COMPLETED
                
                # Step 4: Validate and populate structured data
                structured_data = setting_item.to_structured_format()
                if structured_data:
                    successful_settings[setting_name] = structured_data
                    successful_count += 1
                    print(f"✅ {setting_name} successfully populated")
                else:
                    print(f"❌ {setting_name} failed validation")
            else:
                print(f"❌ {setting_name} research failed")
            
            # Brief pause between research requests
            time.sleep(0.5)
        
        return {
            "settings": successful_settings,
            "metadata": {
                "total_settings_researched": len(settings),
                "successful_settings": successful_count
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Test the pipeline
    pipeline = ResearchPipelineManager()
    
    # Test with Zirconia
    results = pipeline.execute_complete_pipeline("Zirconia", "ceramic")
    
    print("\n" + "="*60)
    print("FINAL RESULTS:")
    print(json.dumps(results, indent=2))