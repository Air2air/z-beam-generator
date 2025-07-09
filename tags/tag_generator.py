#!/usr/bin/env python3
"""
Tag Generator - Discrete module for generating optimized tags from material data
"""
import logging
import json

logger = logging.getLogger(__name__)

class TagGenerator:
    """Generates and processes tags for laser cleaning articles"""
    
    def __init__(self, config, api_client):
        self.config = config
        self.api_client = api_client
        self.static_shortenings_map = self._load_static_shortenings_map()
    
    def generate_tags(self, material, material_data):
        """Generate high-quality tags with proper formatting - Main public interface"""
        logger.info(f"🏷️ Starting tag generation for {material}")
        
        # START with material property-derived tags (highest value)
        property_tags = self._derive_property_tags(material, material_data)
        
        # Collect from material data and shorten immediately
        collected_tags = []
        source_fields = [
            "safetyConsiderations", "processingChallenges", "applications", 
            "industryStandards", "relatedMaterials", "regulatoryCompliance"
        ]
        
        # Collect all raw tags first
        raw_tags = []
        for field in source_fields:
            values = material_data.get(field, [])
            
            if isinstance(values, str):
                logger.warning(f"⚠️ Field {field} is string, should be array: {values}")
                continue
            elif isinstance(values, list):
                for value in values:
                    raw_tags.append(str(value))
        
        # Use AI to shorten all tags at once
        if raw_tags and self.api_client:
            shortened_tags = self._ai_shorten_tags(raw_tags, material)
            collected_tags.extend(shortened_tags)
        else:
            # Fallback to static shortening
            for raw_tag in raw_tags:
                shortened = self._static_shorten_tag(raw_tag)
                if shortened and shortened not in collected_tags and len(shortened) > 2:
                    collected_tags.append(shortened)
        
        # Add essential laser cleaning context (minimal, specific)
        essential_tags = ["Laser Cleaning"]  # Only the core process tag
        
        # Combine: Property tags first (highest value), then collected, then essential
        all_tags = property_tags + collected_tags + essential_tags
        unique_tags = []
        for tag in all_tags:
            if tag and tag not in unique_tags and len(tag.strip()) > 2:
                unique_tags.append(tag.strip())
        
        # Validate we have enough tags
        if len(unique_tags) < 3:  # Reduced minimum since we're more selective
            raise ValueError(f"Insufficient tags generated for {material}: only {len(unique_tags)} tags")
        
        # Limit to reasonable number
        final_tags = unique_tags[:12]  # Reduced from 15 to focus on quality
        
        logger.info(f"✅ Generated {len(final_tags)} high-value tags for {material}")
        logger.debug(f"Final tags: {final_tags}")
        return final_tags
    
    def _derive_property_tags(self, material, material_data):
        """Analyze material properties and derive relevant tags"""
        logger.info(f"🔬 Deriving property tags from material data for {material}")
        
        property_tags = []
        
        # Get general classifier to determine analysis approach
        general_classifier = material_data.get("generalClassifier", "").lower()
        
        if general_classifier == "metal":
            property_tags.extend(self._analyze_metal_properties(material_data))
        elif general_classifier == "polymer" or "plastic" in material.lower():
            property_tags.extend(self._analyze_polymer_properties(material_data))
        elif general_classifier == "wood" or any(wood_type in material.lower() for wood_type in ["oak", "maple", "pine", "cedar", "walnut", "cherry", "birch"]):
            property_tags.extend(self._analyze_wood_properties(material_data))
        elif general_classifier == "ceramic":
            property_tags.extend(self._analyze_ceramic_properties(material_data))
        else:
            # Generic analysis for unknown materials
            property_tags.extend(self._analyze_generic_properties(material_data))
    
        logger.info(f"✅ Derived {len(property_tags)} property tags: {property_tags}")
        return property_tags

    def _analyze_metal_properties(self, material_data):
        """Analyze metal-specific properties"""
        tags = []
        
        # Existing metal analysis
        density_tag = self._analyze_density(material_data.get("density", ""))
        if density_tag: tags.append(density_tag)
        
        melting_point_tag = self._analyze_melting_point(material_data.get("meltingPoint", ""))
        if melting_point_tag: tags.append(melting_point_tag)
        
        thermal_tag = self._analyze_thermal_conductivity(material_data.get("thermalConductivity", ""))
        if thermal_tag: tags.append(thermal_tag)
        
        hardness_tag = self._analyze_hardness(material_data.get("hardnessMohs", ""))
        if hardness_tag: tags.append(hardness_tag)
        
        reflectivity_tag = self._analyze_reflectivity(material_data.get("reflectivityIr", ""))
        if reflectivity_tag: tags.append(reflectivity_tag)
        
        class_tags = self._analyze_material_class(material_data.get("materialClass", ""), material_data.get("generalClassifier", ""))
        tags.extend(class_tags)
        
        structure_tag = self._analyze_crystal_structure(material_data.get("crystalStructure", ""))
        if structure_tag: tags.append(structure_tag)
        
        purity_tag = self._analyze_purity(material_data.get("materialPurity", ""))
        if purity_tag: tags.append(purity_tag)
        
        return tags

    def _analyze_polymer_properties(self, material_data):
        """Analyze polymer/plastic-specific properties"""
        tags = []
        
        # Polymer class analysis
        material_class = material_data.get("materialClass", "").lower()
        if "thermoplastic" in material_class:
            tags.append("Thermoplastic")
        elif "thermoset" in material_class:
            tags.append("Thermoset")
        elif "elastomer" in material_class:
            tags.append("Elastomer")
        
        # Glass transition temperature analysis
        glass_transition = material_data.get("glassTransitionTemp", "")
        if glass_transition:
            tg_tag = self._analyze_glass_transition(glass_transition)
            if tg_tag: tags.append(tg_tag)
        
        # Melting point for thermoplastics
        melting_point = material_data.get("meltingPoint", "")
        if melting_point:
            mp_tag = self._analyze_polymer_melting_point(melting_point)
            if mp_tag: tags.append(mp_tag)
        
        # Density analysis (different thresholds for polymers)
        density_tag = self._analyze_polymer_density(material_data.get("density", ""))
        if density_tag: tags.append(density_tag)
        
        # Chemical resistance
        chemical_resistance = material_data.get("chemicalResistance", "")
        if "excellent" in chemical_resistance.lower():
            tags.append("Chemical Resistant")
        elif "poor" in chemical_resistance.lower():
            tags.append("Chemical Sensitive")
        
        # UV resistance
        uv_resistance = material_data.get("uvResistance", "")
        if "excellent" in uv_resistance.lower() or "good" in uv_resistance.lower():
            tags.append("UV Resistant")
        
        # Flexibility analysis
        flexibility = material_data.get("flexibility", "")
        if "flexible" in flexibility.lower():
            tags.append("Flexible Material")
        elif "rigid" in flexibility.lower():
            tags.append("Rigid Material")
        
        # Food safety
        food_grade = material_data.get("foodGrade", "")
        if food_grade and "yes" in food_grade.lower():
            tags.append("Food Grade")
        
        return tags

    def _analyze_wood_properties(self, material_data):
        """Analyze wood-specific properties"""
        tags = []
        
        # Wood type classification
        material_class = material_data.get("materialClass", "").lower()
        if "hardwood" in material_class:
            tags.append("Hardwood")
        elif "softwood" in material_class:
            tags.append("Softwood")
        
        # Density analysis (wood-specific thresholds)
        density_tag = self._analyze_wood_density(material_data.get("density", ""))
        if density_tag: tags.append(density_tag)
        
        # Hardness analysis (Janka hardness for wood)
        janka_hardness = material_data.get("jankaHardness", "") or material_data.get("hardness", "")
        if janka_hardness:
            hardness_tag = self._analyze_janka_hardness(janka_hardness)
            if hardness_tag: tags.append(hardness_tag)
        
        # Grain analysis
        grain = material_data.get("grainPattern", "")
        if "straight" in grain.lower():
            tags.append("Straight Grain")
        elif "interlocked" in grain.lower():
            tags.append("Interlocked Grain")
        elif "irregular" in grain.lower():
            tags.append("Irregular Grain")
        
        # Durability/rot resistance
        durability = material_data.get("durability", "") or material_data.get("rotResistance", "")
        if "excellent" in durability.lower() or "high" in durability.lower():
            tags.append("Durable Wood")
        elif "poor" in durability.lower() or "low" in durability.lower():
            tags.append("Treatment Required")
        
        # Workability
        workability = material_data.get("workability", "")
        if "excellent" in workability.lower() or "good" in workability.lower():
            tags.append("Easy Machining")
        elif "difficult" in workability.lower() or "poor" in workability.lower():
            tags.append("Difficult Machining")
        
        # Moisture content
        moisture = material_data.get("moistureContent", "")
        if moisture:
            moisture_tag = self._analyze_moisture_content(moisture)
            if moisture_tag: tags.append(moisture_tag)
        
        return tags

    def _analyze_ceramic_properties(self, material_data):
        """Analyze ceramic-specific properties"""
        tags = []
        
        # High temperature resistance (ceramics typically excel here)
        melting_point_tag = self._analyze_melting_point(material_data.get("meltingPoint", ""))
        if melting_point_tag: tags.append(melting_point_tag)
        
        # Hardness (ceramics are typically very hard)
        hardness_tag = self._analyze_hardness(material_data.get("hardnessMohs", ""))
        if hardness_tag: tags.append(hardness_tag)
        
        # Brittleness is common in ceramics
        tags.append("Brittle Material")
        
        # Thermal shock resistance
        thermal_shock = material_data.get("thermalShockResistance", "")
        if "excellent" in thermal_shock.lower():
            tags.append("Thermal Shock Resistant")
        
        # Electrical properties
        dielectric = material_data.get("dielectricConstant", "")
        if dielectric:
            tags.append("Dielectric Material")
        
        return tags

    def _analyze_generic_properties(self, material_data):
        """Generic analysis for unknown material types"""
        tags = []
        
        # Basic physical properties that apply to most materials
        density_tag = self._analyze_density(material_data.get("density", ""))
        if density_tag: tags.append(density_tag)
        
        melting_point_tag = self._analyze_melting_point(material_data.get("meltingPoint", ""))
        if melting_point_tag: tags.append(melting_point_tag)
        
        thermal_tag = self._analyze_thermal_conductivity(material_data.get("thermalConductivity", ""))
        if thermal_tag: tags.append(thermal_tag)
        
        return tags

    def _ai_shorten_tags(self, raw_tags, material):
        """Use AI to intelligently shorten tags with proper grammar"""
        logger.info(f"🤖 Using AI to shorten {len(raw_tags)} tags for {material}")
        
        # Create prompt for AI tag shortening
        raw_tags_text = "\n".join([f"- {tag}" for tag in raw_tags])
        
        prompt = f"""Convert these long technical phrases into short, SEO-friendly tags for a laser cleaning article about {material}.

Rules:
- Maximum 3 words per tag
- Use proper grammar and capitalization
- Make tags searchable and professional
- Convert incomplete sentences to complete concepts
- Focus on the key concept, not the full sentence

Long phrases to shorten:
{raw_tags_text}

Examples of good conversions:
- "Avoid inhalation of fine particles during processing" → "Dust Protection"
- "High melting point requires specialized equipment" → "High Temperature"
- "Nuclear reactor control rods" → "Nuclear Applications"
- "Use protective equipment when handling" → "Protective Equipment"
- "Difficult to machine due to hardness" → "Machining Challenges"

Output format: Return ONLY a JSON array of shortened tags, nothing else.
Example: ["Dust Protection", "High Temperature", "Nuclear Applications"]

Shortened tags:"""

        try:
            response = self.api_client.call(prompt, "tag-shortening")
            
            # Clean response
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:-3]
            elif response.startswith('```'):
                response = response[3:-3]
            elif response.startswith('[') and response.endswith(']'):
                pass  # Already clean JSON
            else:
                # Try to extract JSON array from response
                start = response.find('[')
                end = response.rfind(']') + 1
                if start != -1 and end != -1:
                    response = response[start:end]
            
            shortened_tags = json.loads(response)
            
            if not isinstance(shortened_tags, list):
                raise ValueError("AI response is not a list")
            
            # Validate and clean tags
            clean_tags = []
            for tag in shortened_tags:
                if isinstance(tag, str) and len(tag.strip()) > 2 and len(tag.strip()) <= 25:
                    clean_tags.append(tag.strip())
            
            logger.info(f"✅ AI shortened {len(raw_tags)} tags to {len(clean_tags)} clean tags")
            return clean_tags
            
        except Exception as e:
            logger.warning(f"⚠️ AI tag shortening failed: {e}. Using static fallback.")
            # Fall back to static shortening
            return [self._static_shorten_tag(tag) for tag in raw_tags if self._static_shorten_tag(tag)]
    
    def _static_shorten_tag(self, tag):
        """Static shortening as fallback when AI is not available"""
        
        # Remove quotes and extra whitespace
        tag = tag.strip().strip("'\"")
        
        if not tag:
            return None
        
        # Check for exact matches first
        if tag in self.static_shortenings_map:
            return self.static_shortenings_map[tag]
        
        # Check for partial matches on incomplete fragments
        for full_phrase, shortened in self.static_shortenings_map.items():
            if tag in full_phrase and len(tag) < len(full_phrase):
                logger.debug(f"Partial match: '{tag}' -> '{shortened}'")
                return shortened
        
        # Apply general rules for unknown tags
        shortened = self._apply_general_shortening_rules(tag)
        
        # Skip if still incomplete fragment
        incomplete_patterns = ["avoid", "use proper", "wear", "ensure", "handle with", "store in"]
        if any(pattern in shortened.lower() for pattern in incomplete_patterns) and len(shortened) < 15:
            logger.debug(f"Skipping incomplete fragment: '{shortened}'")
            return None
        
        return shortened.strip() if shortened.strip() else None
    
    def _apply_general_shortening_rules(self, tag):
        """Apply general shortening rules for unknown tags"""
        shortened = tag
        
        # Remove common long phrases
        phrases_to_remove = [
            " during processing",
            " and UV radiation", 
            " require careful control of laser parameters",
            " complicates efficient laser energy absorption",
            " at high temperatures",
            " during laser cleaning",
            " for laser cleaning",
            " in laser cleaning",
            " when handling",
            " due to hardness",
            " requires specialized equipment"
        ]
        
        for phrase in phrases_to_remove:
            shortened = shortened.replace(phrase, "")
        
        # Limit length
        if len(shortened) > 25:
            # Try to get first meaningful words
            words = shortened.split()
            if len(words) > 2:
                shortened = " ".join(words[:2])
            else:
                shortened = shortened[:25].strip()
        
        return shortened
    
    def _load_static_shortenings_map(self):
        """Load comprehensive shortening map with enhanced material properties"""
        return {
            # Common safety considerations
            "Avoid inhalation of dust during processing": "Dust Protection",
            "Avoid inhalation": "Dust Protection",
            "Use protective equipment when handling": "Protective Equipment",
            "Use protective": "Protective Equipment",
            "Ensure proper ventilation": "Ventilation",
            "Wear safety glasses": "Eye Protection",
            "Handle with care": "Safety Protocols",
            "Handle with": "Safety Protocols",
            "Store in dry conditions": "Storage Requirements",
            "Store in": "Storage Requirements",
            
            # Common processing challenges
            "High melting point requires specialized equipment": "High Temperature",
            "High melting": "High Temperature",
            "Difficult to machine due to hardness": "Machining Challenges",
            "Difficult to": "Machining Challenges",
            "Sensitive to contaminants during processing": "Contamination Sensitive",
            "Sensitive to": "Contamination Sensitive",
            "High oxidation rate": "High Oxidation",
            "Oxidation risk": "Oxidation Risk",
            "Thermal conductivity": "Thermal Management",
            "High reflectivity": "High Reflectivity",
            
            # Common applications
            "Nuclear reactor control rods": "Nuclear Applications",
            "Nuclear reactors": "Nuclear Applications",
            "Aerospace components": "Aerospace",
            "Medical implants": "Medical",
            "Automotive components": "Automotive",
            "Chemical processing equipment": "Chemical Processing",
            "High-temperature superalloys": "High-temp Alloys",
            "High-temperature alloys": "High-temp Alloys",
            
            # Standards
            "ASTM B6 (Zinc)": "ASTM B6",
            "ASTM B348": "ASTM B348",
            "ISO 5832": "ISO 5832",
            "ISO 752": "ISO 752",
            
            # Regulatory
            "REACH (Registration, Evaluation, Authorization and Restriction of Chemicals)": "REACH",
            "RoHS (Restriction of Hazardous Substances)": "RoHS",
            
            # Physical Properties
            "High thermal conductivity": "Heat Conductive",
            "Low thermal conductivity": "Heat Insulating", 
            "Corrosion resistance": "Corrosion Resistant",
            "High density material": "High Density",
            "Lightweight properties": "Lightweight",
            "Magnetic permeability": "Magnetic Properties",
            "Electrical conductivity": "Electrically Conductive",
            "Thermal expansion coefficient": "Thermal Expansion",
            
            # Mechanical Properties  
            "High tensile strength": "High Strength",
            "Impact resistance": "Impact Resistant",
            "Fatigue resistance": "Fatigue Resistant",
            "Wear resistance": "Wear Resistant",
            "Ductility properties": "Ductile Material",
            "Brittleness characteristics": "Brittle Material",
            "Creep resistance": "Creep Resistant",
            
            # Manufacturing Applications
            "Investment casting": "Casting Applications",
            "Hot forging applications": "Forging Process", 
            "Welding compatibility": "Welding Compatible",
            "Additive manufacturing": "3D Printing",
            "Powder metallurgy processes": "Powder Metallurgy",
            "Sheet metal forming": "Sheet Metal",
            "Extrusion processing": "Extrusion Process",
            
            # Quality/Grade Classifications
            "Food contact applications": "Food Grade",
            "Biomedical applications": "Medical Grade", 
            "Aerospace specifications": "Aerospace Grade",
            "Military standards": "Military Spec",
            "Commercial applications": "Commercial Grade",
            "High purity material": "High Purity",
            
            # Environmental Applications
            "Marine environments": "Marine Environment",
            "High temperature service": "High Temperature",
            "Cryogenic temperatures": "Cryogenic Applications",
            "Vacuum applications": "Vacuum Compatible",
            "Radiation exposure": "Radiation Resistant",
            "Chemical exposure": "Chemical Resistant",
            
            # Structural Applications
            "Load-bearing components": "Structural Components",
            "Electronic packaging": "Electronic Components",
            "Heat transfer equipment": "Heat Exchangers",
            "Gas turbine components": "Turbine Components",
            "Fastening applications": "Fasteners",
            "Piping systems": "Pipes and Tubing",
            "Surface coating": "Coating Substrate",
            
            # Processing Characteristics
            "Machinability rating": "Machining Properties",
            "Surface finish quality": "Surface Quality",
            "Dimensional stability": "Dimensional Stable",
            "Thermal cycling": "Thermal Cycling",
            "Oxidation resistance": "Oxidation Resistant",
            
            # Cost/Economic Factors
            "Material cost": "Cost Effective",
            "Processing cost": "Processing Cost",
            "Lifecycle cost": "Lifecycle Cost",
            "Raw material availability": "Material Availability",
        }
    
    def _analyze_density(self, density_str):
        """Analyze density and return appropriate tag"""
        if not density_str:
            return None
        
        try:
            import re
            match = re.search(r'(\d+\.?\d*)', density_str)
            if match:
                density = float(match.group(1))
                
                # Density thresholds (g/cm³)
                if density >= 8.0:
                    return "High Density"
                elif density <= 2.5:
                    return "Lightweight"
        except (ValueError, AttributeError):
            pass
        
        return None

    def _analyze_melting_point(self, melting_point_str):
        """Analyze melting point and return appropriate tag"""
        if not melting_point_str:
            return None
        
        try:
            import re
            match = re.search(r'(\d+)', melting_point_str)
            if match:
                temp = int(match.group(1))
                
                # Temperature thresholds (°C)
                if temp >= 1500:
                    return "High Temperature"
                elif temp <= 300:
                    return "Low Melting Point"
        except (ValueError, AttributeError):
            pass
        
        return None

    def _analyze_thermal_conductivity(self, thermal_str):
        """Analyze thermal conductivity and return appropriate tag"""
        if not thermal_str:
            return None
        
        try:
            import re
            match = re.search(r'(\d+\.?\d*)', thermal_str)
            if match:
                conductivity = float(match.group(1))
                
                # Thermal conductivity thresholds (W/m·K)
                if conductivity >= 100:
                    return "Heat Conductive"
                elif conductivity <= 5:
                    return "Heat Insulating"
        except (ValueError, AttributeError):
            pass
        
        return None

    def _analyze_hardness(self, hardness_str):
        """Analyze hardness and return appropriate tag"""
        if not hardness_str:
            return None
        
        try:
            hardness = float(str(hardness_str))
            
            # Mohs hardness scale
            if hardness >= 7:
                return "Hard Material"
            elif hardness <= 3:
                return "Soft Material"
        except (ValueError, TypeError):
            pass
        
        return None

    def _analyze_reflectivity(self, reflectivity_str):
        """Analyze IR reflectivity and return appropriate tag"""
        if not reflectivity_str:
            return None
        
        try:
            import re
            match = re.search(r'(\d+)', reflectivity_str)
            if match:
                reflectivity = int(match.group(1))
                
                if reflectivity >= 70:
                    return "High Reflectivity"
                elif reflectivity <= 30:
                    return "Low Reflectivity"
        except (ValueError, AttributeError):
            pass
        
        return None

    def _analyze_material_class(self, material_class, general_classifier):
        """Analyze material class and return appropriate tags"""
        tags = []
        
        # Specific material class tags (more valuable than general)
        if material_class:
            class_map = {
                "transition metal": "Transition Metal",
                "refractory metal": "Refractory Metal",
                "noble metal": "Noble Metal",
                "rare earth metal": "Rare Earth",
                "alkaline earth metal": "Alkaline Metal"
            }
            
            tag = class_map.get(material_class.lower())
            if tag:
                tags.append(tag)
        
        return tags

    def _analyze_crystal_structure(self, structure_str):
        """Analyze crystal structure and return appropriate tag"""
        if not structure_str:
            return None
        
        # Only tag distinctive structures
        structure_map = {
            "hexagonal": "Hexagonal Structure",
            "face-centered cubic": "FCC Structure",
            "body-centered cubic": "BCC Structure",
            "amorphous": "Amorphous"
        }
        
        structure_lower = structure_str.lower()
        for key, tag in structure_map.items():
            if key in structure_lower:
                return tag
        
        return None

    def _analyze_purity(self, purity_str):
        """Analyze material purity and return appropriate tag"""
        if not purity_str:
            return None
        
        try:
            import re
            match = re.search(r'(\d+\.?\d*)', purity_str)
            if match:
                purity = float(match.group(1))
                
                if purity >= 99.9:
                    return "High Purity"
                elif purity <= 95.0:
                    return "Industrial Grade"
        except (ValueError, AttributeError):
            pass
        
        return None

    # New analysis methods for polymers and wood

    def _analyze_glass_transition(self, tg_str):
        """Analyze glass transition temperature"""
        try:
            import re
            match = re.search(r'(-?\d+)', tg_str)
            if match:
                tg = int(match.group(1))
                if tg >= 100:
                    return "High Tg"
                elif tg <= 0:
                    return "Low Tg"
        except (ValueError, AttributeError):
            pass
        return None

    def _analyze_polymer_melting_point(self, mp_str):
        """Analyze polymer melting point (different thresholds than metals)"""
        try:
            import re
            match = re.search(r'(\d+)', mp_str)
            if match:
                temp = int(match.group(1))
                if temp >= 250:
                    return "High Temperature Polymer"
                elif temp <= 120:
                    return "Low Temperature Polymer"
        except (ValueError, AttributeError):
            pass
        return None

    def _analyze_polymer_density(self, density_str):
        """Analyze polymer density (different thresholds)"""
        try:
            import re
            match = re.search(r'(\d+\.?\d*)', density_str)
            if match:
                density = float(match.group(1))
                # Polymer density thresholds (g/cm³)
                if density >= 1.4:
                    return "High Density Polymer"
                elif density <= 0.9:
                    return "Low Density Polymer"
        except (ValueError, AttributeError):
            pass
        return None

    def _analyze_wood_density(self, density_str):
        """Analyze wood density (wood-specific thresholds)"""
        try:
            import re
            match = re.search(r'(\d+\.?\d*)', density_str)
            if match:
                density = float(match.group(1))
                # Wood density thresholds (g/cm³)
                if density >= 0.8:
                    return "Dense Wood"
                elif density <= 0.4:
                    return "Light Wood"
        except (ValueError, AttributeError):
            pass
        return None

    def _analyze_janka_hardness(self, hardness_str):
        """Analyze Janka hardness for wood"""
        try:
            import re
            match = re.search(r'(\d+)', hardness_str)
            if match:
                hardness = int(match.group(1))
                # Janka hardness thresholds (lbf)
                if hardness >= 1500:
                    return "Very Hard Wood"
                elif hardness >= 1000:
                    return "Hard Wood"
                elif hardness <= 500:
                    return "Soft Wood"
        except (ValueError, AttributeError):
            pass
        return None

    def _analyze_moisture_content(self, moisture_str):
        """Analyze wood moisture content"""
        try:
            import re
            match = re.search(r'(\d+)', moisture_str)
            if match:
                moisture = int(match.group(1))
                if moisture <= 12:
                    return "Kiln Dried"
                elif moisture >= 20:
                    return "Green Wood"
        except (ValueError, AttributeError):
            pass
        return None