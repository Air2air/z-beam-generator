"""
Content formatting utilities for Z-Beam Generator.

This module handles all formatting tasks that were previously done by AI,
ensuring consistent and reliable output formatting.
"""

import re
from typing import Dict, Any, List
from components.base.utils.content_processor import ContentProcessor
from components.base.image_handler import ImageHandler


class ContentFormatter:
    """Handles all content formatting tasks to offload work from AI."""
    
    @staticmethod
    def format_title(subject: str, article_type: str = "material", schema: Dict[str, Any] = None) -> str:
        """Generate title based on schema configuration.
        
        Args:
            subject: The subject material/topic
            article_type: Type of article (material, application, etc.)
            schema: Schema configuration with title patterns
            
        Returns:
            str: Formatted title
        """
        if schema and 'titleFormat' in schema:
            return schema['titleFormat'].format(subject=subject, article_type=article_type)
        
        return f"{subject} - Technical Guide"

    @staticmethod
    def format_headline(subject: str, category: str = None, schema: Dict[str, Any] = None) -> str:
        """Generate headline based on schema configuration.
        
        Args:
            subject: The subject material/topic
            category: Material category (ceramic, metal, etc.)
            schema: Schema configuration with headline patterns
            
        Returns:
            str: Formatted headline
        """
        if schema and 'headlineFormat' in schema:
            return schema['headlineFormat'].format(subject=subject, category=category or '')
        
        category_text = f"{category} " if category else ""
        return f"Technical guide for {category_text}{subject.lower()}"
    
    @staticmethod
    def format_description(subject: str, formula: str = None, properties: Dict = None, schema: Dict[str, Any] = None) -> str:
        """Generate technical description based on schema configuration.
        
        Args:
            subject: The subject material/topic
            formula: Chemical formula if applicable
            properties: Key properties dictionary
            schema: Schema configuration with description patterns
            
        Returns:
            str: Formatted description (150-250 chars)
        """
        if schema and 'descriptionFormat' in schema:
            return schema['descriptionFormat'].format(
                subject=subject, 
                formula=formula or '', 
                properties=properties or {}
            )
        
        desc_parts = [f"Technical overview of {subject.lower()}"]
        
        if formula:
            desc_parts.append(f"({formula})")
        
        desc_parts.append("specifications and applications")
        
        if properties:
            prop_parts = []
            if "density" in properties:
                prop_parts.append(f"{properties['density']} density")
            if "wavelength" in properties:
                prop_parts.append(f"{properties['wavelength']}")
            
            if prop_parts:
                desc_parts.extend(prop_parts)
        
        description = ", ".join(desc_parts) + "."
        
        # Truncate if too long
        if len(description) > 250:
            description = description[:247] + "..."
        
        return description
    
    @staticmethod
    @staticmethod
    def _restructure_yaml_nesting(raw_data: dict, component_type: str = 'frontmatter') -> dict:
        """Restructure flat YAML keys into proper nested sections for any component type.
        
        This method takes any flat data structure and organizes it into the proper
        nested YAML format based on the component type.
        
        Args:
            raw_data: Raw flat data from AI generation
            component_type: Type of component (frontmatter, jsonld, metatags, etc.)
            
        Returns:
            dict: Properly nested data structure with correct YAML hierarchy
        """
        if not isinstance(raw_data, dict):
            return raw_data
            
        # Component-specific nested section configurations
        nested_section_configs = {
            'frontmatter': {
                'properties': {},
                'environmentalImpact': {},
                'technicalSpecifications': {},
                'outcomes': {},
                'images': {}
            },
            'jsonld': {
                # JSON-LD typically doesn't need deep nesting as it follows Schema.org structure
            },
            'metatags': {
                # Metatags are typically flat key-value pairs
            }
        }
        
        # Get configuration for this component type
        nested_sections = nested_section_configs.get(component_type, {})
        
        # For frontmatter specifically, handle the detailed property mappings
        if component_type == 'frontmatter':
            return ContentFormatter._restructure_frontmatter_specific(raw_data, nested_sections)
        
        # For other component types, apply simpler structuring if needed
        return ContentFormatter._apply_generic_yaml_structure(raw_data, nested_sections)
    
    @staticmethod 
    def _restructure_frontmatter_nesting(raw_data: dict) -> dict:
        """Backward compatibility wrapper for frontmatter restructuring.
        
        Args:
            raw_data: Raw flat data from AI generation
            
        Returns:
            dict: Properly nested frontmatter data structure
        """
        return ContentFormatter._restructure_yaml_nesting(raw_data, 'frontmatter')
    
    @staticmethod
    def _restructure_frontmatter_specific(raw_data: dict, nested_sections: dict) -> dict:
        """Handle frontmatter-specific nested section logic."""
        result = {}
        
        # Initialize nested sections for frontmatter
        nested_sections.update({
            'properties': {},
            'environmentalImpact': {},
            'technicalSpecifications': {},
            'outcomes': {},
            'images': {}
        })
        
        # Comprehensive property keys (physical, chemical, mechanical properties)
        property_keys = {
            # Basic physical properties
            'density', 'meltingPoint', 'boilingPoint', 'thermalConductivity', 'hardness',
            'flexuralStrength', 'compressiveStrength', 'tensileStrength', 'elasticModulus',
            'thermalExpansionCoefficient', 'coefficientOfThermalExpansion',
            'dielectricStrength', 'dielectricConstant', 'waterAbsorption',
            'electricalResistivity', 'fractureToughness', 'chemicalStability',
            'glassTransitionTemperature', 'degradationTemperature', 'chemicalResistance',
            'modulusOfElasticity', 'refractiveIndex',
            # Variations in naming
            'melting_point', 'boiling_point', 'thermal_conductivity', 'flexural_strength',
            'compressive_strength', 'tensile_strength', 'elastic_modulus',
            'thermal_expansion_coefficient', 'dielectric_strength', 'dielectric_constant',
            'water_absorption', 'electrical_resistivity', 'fracture_toughness',
            'chemical_stability', 'glass_transition_temperature', 'degradation_temperature',
            'chemical_resistance', 'modulus_of_elasticity', 'refractive_index'
        }
        
        # Environmental impact keys (any variation)
        environmental_keys = {
            'wasteReduction', 'energyEfficiency', 'emissions', 'VOCReduction', 'VOCreduction',
            'energyConsumption', 'chemicalUsage', 'CO2Reduction', 'waterSavings',
            'reducedWaste', 'emissionsReduction', 'energySavings', 'waterConservation',
            'chemicalReduction', 'energyConsumption', 'waterSavings',
            # Variations
            'waste_reduction', 'energy_efficiency', 'voc_reduction', 'energy_consumption',
            'chemical_usage', 'co2_reduction', 'water_savings', 'reduced_waste',
            'emissions_reduction', 'energy_savings', 'water_conservation', 'chemical_reduction'
        }
        
        # Technical specification keys (laser parameters, equipment specs)
        technical_keys = {
            'powerRange', 'pulseDuration', 'wavelength', 'spotSize', 'repetitionRate',
            'fluenceRange', 'safetyClass', 'laserType', 'scanSpeed', 'wavelengthOptions',
            'power_range', 'pulse_duration', 'spot_size', 'repetition_rate',
            'fluence_range', 'safety_class', 'laser_type', 'scan_speed', 'wavelength_options'
        }
        
        # Outcome/result keys (performance metrics)
        outcome_keys = {
            'cleaningEfficiency', 'surfaceRoughness', 'processingSpeed', 'processingRate',
            'colorStability', 'glazePreservation', 'surfaceRoughnessChange', 'thermalAffectedZone',
            'surfaceCleanliness', 'materialRemovalRate', 'adhesionImprovement', 'processEfficiency',
            'surfaceQuality', 'contaminantRemoval', 'cleaningRate', 'bacterialReduction',
            'colorDeltaE', 'substrateDamage', 'depthControl',
            # Variations
            'cleaning_efficiency', 'surface_roughness', 'processing_speed', 'processing_rate',
            'color_stability', 'glaze_preservation', 'surface_roughness_change', 'thermal_affected_zone',
            'surface_cleanliness', 'material_removal_rate', 'adhesion_improvement', 'process_efficiency',
            'surface_quality', 'contaminant_removal', 'cleaning_rate', 'bacterial_reduction',
            'color_delta_e', 'substrate_damage', 'depth_control'
        }
        
        # Image structure keys
        image_keys = {'hero', 'closeup', 'main', 'detail'}
        
        # Process each key-value pair
        for key, value in raw_data.items():
            key_lower = key.lower()
            
            if key in property_keys or key_lower in property_keys:
                nested_sections['properties'][key] = value
            elif key in environmental_keys or key_lower in environmental_keys:
                nested_sections['environmentalImpact'][key] = value
            elif key in technical_keys or key_lower in technical_keys:
                nested_sections['technicalSpecifications'][key] = value
            elif key in outcome_keys or key_lower in outcome_keys:
                nested_sections['outcomes'][key] = value
            elif key in image_keys:
                nested_sections['images'][key] = value
            else:
                # Keep as top-level key (name, title, composition, applications, etc.)
                result[key] = value
        
        # Add non-empty nested sections to result
        for section_name, section_data in nested_sections.items():
            if section_data:  # Only add if not empty
                result[section_name] = section_data
        
        return result
    
    @staticmethod
    def _apply_generic_yaml_structure(raw_data: dict, nested_sections: dict) -> dict:
        """Apply generic YAML structuring for non-frontmatter components.
        
        Args:
            raw_data: Raw data from AI generation
            nested_sections: Component-specific nested section configuration
            
        Returns:
            dict: Structured data with any required nesting
        """
        # For now, most components don't need complex nesting like frontmatter
        # This method can be extended as other components require specific structuring
        result = raw_data.copy()
        
        # Apply any component-specific nested sections if defined
        if nested_sections:
            for section_name, section_config in nested_sections.items():
                if section_name in result:
                    # If this section already exists, ensure it's properly structured
                    if isinstance(result[section_name], dict):
                        result[section_name] = {**section_config, **result[section_name]}
                    else:
                        result[section_name] = section_config
        
        return result
    
    @staticmethod
    def _format_yaml_with_proper_indentation(data, indent_level=0):
        """Format dictionary as YAML with guaranteed proper 2-space indentation.
        
        Args:
            data: Dictionary or list to format
            indent_level: Current indentation level (0 = root level)
            
        Returns:
            str: Properly indented YAML string
        """
        if data is None:
            return ""
            
        lines = []
        indent = "  " * indent_level  # 2 spaces per level
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    # Nested dictionary - add key with colon, then nested content
                    lines.append(f"{indent}{key}:")
                    nested_yaml = ContentFormatter._format_yaml_with_proper_indentation(value, indent_level + 1)
                    lines.append(nested_yaml)
                elif isinstance(value, list):
                    # List - add key with colon, then list items
                    lines.append(f"{indent}{key}:")
                    for item in value:
                        if isinstance(item, dict):
                            # List of dictionaries - each item starts with dash
                            item_lines = []
                            first_key = True
                            for sub_key, sub_value in item.items():
                                if first_key:
                                    # First key gets the dash
                                    formatted_value = ContentFormatter._format_yaml_value(sub_value)
                                    item_lines.append(f"{indent}- {sub_key}: {formatted_value}")
                                    first_key = False
                                else:
                                    # Subsequent keys are indented to align with first key value
                                    formatted_value = ContentFormatter._format_yaml_value(sub_value)
                                    item_lines.append(f"{indent}  {sub_key}: {formatted_value}")
                            lines.extend(item_lines)
                        else:
                            # Simple list item
                            formatted_value = ContentFormatter._format_yaml_value(item)
                            lines.append(f"{indent}- {formatted_value}")
                else:
                    # Simple key-value pair
                    formatted_value = ContentFormatter._format_yaml_value(value)
                    lines.append(f"{indent}{key}: {formatted_value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    # List of dictionaries at root level
                    item_lines = []
                    first_key = True
                    for sub_key, sub_value in item.items():
                        if first_key:
                            formatted_value = ContentFormatter._format_yaml_value(sub_value)
                            item_lines.append(f"{indent}- {sub_key}: {formatted_value}")
                            first_key = False
                        else:
                            formatted_value = ContentFormatter._format_yaml_value(sub_value)
                            item_lines.append(f"{indent}  {sub_key}: {formatted_value}")
                    lines.extend(item_lines)
                else:
                    formatted_value = ContentFormatter._format_yaml_value(item)
                    lines.append(f"{indent}- {formatted_value}")
        
        return "\n".join(lines)
    
    @staticmethod 
    def _format_yaml_value(value):
        """Format a single YAML value with proper quoting if needed."""
        if value is None:
            return ""
        
        value_str = str(value)
        
        # Quote values that contain special characters or start with special chars
        if any(char in value_str for char in [':', '"', "'", '#', '&', '*', '!', '|', '>', '@', '`']):
            # Escape quotes in the value
            escaped = value_str.replace('"', '\\"')
            return f'"{escaped}"'
        elif value_str.startswith(('true', 'false', 'null')) or value_str.isdigit():
            # Quote values that might be interpreted as boolean/null/number when they shouldn't be
            return f'"{value_str}"'
        else:
            return value_str
    
    @staticmethod
    def format_keywords(subject: str, category: str = None, 
                       chemical_formula: str = None, schema: Dict[str, Any] = None) -> List[str]:
        """Generate comprehensive keyword list based on schema configuration.
        
        Args:
            subject: The subject material/topic
            category: Material category
            chemical_formula: Chemical formula if applicable
            schema: Schema configuration with keyword patterns
            
        Returns:
            List[str]: List of 8-12 keywords
        """
        keywords = []
        
        # Get keywords from schema if available
        if schema and 'keywordTemplates' in schema:
            for template in schema['keywordTemplates']:
                keyword = template.format(
                    subject=subject, 
                    category=category or '', 
                    formula=chemical_formula or ''
                ).strip()
                if keyword:
                    keywords.append(keyword)
        else:
            # Fallback to generic keywords
            subject_lower = subject.lower()
            keywords.append(f"{subject_lower}")
            
            if category:
                keywords.append(f"{subject_lower} {category}")
            
            # Technical terms
            keywords.extend([
                "technical specifications",
                "material properties",
                "industrial applications"
            ])
            
            # Chemical formula variations
            if chemical_formula:
                # Clean up formula for keyword use
                formula_clean = re.sub(r'[²³·⁰¹⁴⁵⁶⁷⁸⁹]', '', chemical_formula)
                keywords.append(f"{formula_clean} material")
            
            # Application-specific terms
            keywords.extend([
                "processing parameters",
                "surface treatment",
                "contamination removal"
            ])
        
        # Remove duplicates and limit to reasonable number
        keywords = list(dict.fromkeys(keywords))  # Remove duplicates while preserving order
        return keywords[:12]  # Limit to 12 keywords

    @staticmethod
    def format_images(subject: str) -> Dict[str, Dict[str, str]]:
        """Generate standardized image structure.
        
        Args:
            subject: The subject material/topic
            
        Returns:
            Dict: Standardized image structure with alt text and URLs
        """
        subject_lower = subject.lower()
        
        return {
            "hero": {
                "alt": f"{subject} surface undergoing laser cleaning showing precise contamination removal",
                "url": ImageHandler.format_image_url(subject, "hero")
            },
            "closeup": {
                "alt": f"Microscopic view of {subject_lower} surface after laser treatment showing preserved microstructure",
                "url": ImageHandler.format_image_url(subject, "closeup")
            }
        }
    
    @staticmethod
    def format_technical_specifications(base_specs: Dict = None) -> Dict[str, str]:
        """Generate standardized technical specifications.
        
        Args:
            base_specs: Base specifications to enhance
            
        Returns:
            Dict: Standardized technical specifications
        """
        default_specs = {
            "powerRange": "20-100W",
            "pulseDuration": "10-100ns", 
            "wavelength": "1064nm (primary), 532nm (optional)",
            "spotSize": "0.1-2.0mm",
            "repetitionRate": "10-50kHz",
            "fluenceRange": "0.5-5 J/cm²",
            "safetyClass": "Class 4 (requires full enclosure)"
        }
        
        if base_specs:
            default_specs.update(base_specs)
        
        return default_specs
    
    @staticmethod
    def format_regulatory_standards() -> List[Dict[str, str]]:
        """Generate standard regulatory standards list.
        
        Returns:
            List[Dict]: List of regulatory standards
        """
        return [
            {
                "code": "IEC 60825-1:2014",
                "description": "Safety of laser products - Equipment classification and requirements"
            },
            {
                "code": "ISO 11146:2021", 
                "description": "Lasers and laser-related equipment - Test methods for laser beam widths"
            },
            {
                "code": "EN 15898:2019",
                "description": "Conservation of cultural property - Main general terms and definitions"
            }
        ]
    
    @staticmethod
    def format_environmental_impact(subject: str = None) -> List[Dict[str, str]]:
        """Generate standardized environmental impact list.
        
        Args:
            subject: The subject material (for customization)
            
        Returns:
            List[Dict]: Environmental impact benefits
        """
        return [
            {
                "benefit": "Reduced chemical waste",
                "description": "Eliminates 100% of solvent use compared to traditional cleaning methods, preventing ~200L/year of hazardous waste in medium-scale operations."
            },
            {
                "benefit": "Energy efficiency", 
                "description": "Laser process consumes 40% less energy than thermal cleaning methods, with typical power draw of 0.5-2.5 kWh/m² treated surface."
            },
            {
                "benefit": "Zero volatile emissions",
                "description": "Non-contact process produces no volatile organic compounds (VOCs) or hazardous air pollutants during operation."
            }
        ]
    
    @staticmethod
    def format_outcomes() -> List[Dict[str, str]]:
        """Generate standardized measurement outcomes.
        
        Returns:
            List[Dict]: Measurable outcomes with metrics
        """
        return [
            {
                "result": "Surface cleanliness",
                "metric": "98% contamination removal measured by SEM-EDS analysis (ASTM E1508)"
            },
            {
                "result": "Substrate preservation", 
                "metric": "< 0.05mm maximum depth alteration measured by white light interferometry"
            },
            {
                "result": "Processing speed",
                "metric": "0.5-2.0 m²/hour coverage rate at 50W power"
            }
        ]
    
    @staticmethod
    def format_frontmatter_structure(raw_data: Dict[str, Any], subject: str, 
                                   category: str = None, article_type: str = "material") -> Dict[str, Any]:
        """Apply comprehensive formatting to frontmatter data.
        
        Args:
            raw_data: Raw data from AI generation
            subject: The subject material/topic
            category: Material category
            article_type: Type of article
            
        Returns:
            Dict: Fully formatted frontmatter data
        """
        formatted = raw_data.copy()
        
        # Restructure flat keys into proper nested sections
        formatted = ContentFormatter._restructure_frontmatter_nesting(formatted)
        
        # Debug: Print structure before YAML conversion
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Restructured data structure: {formatted}")
        
        # Apply standardized formatting
        formatted["title"] = ContentFormatter.format_title(subject, article_type)
        formatted["headline"] = ContentFormatter.format_headline(subject, category)
        
        # Format description with available data
        formula = formatted.get("chemicalProperties", {}).get("formula")
        properties = formatted.get("properties", {})
        formatted["description"] = ContentFormatter.format_description(subject, formula, properties)
        
        # Ensure keywords are properly formatted
        if "keywords" not in formatted or not formatted["keywords"]:
            formatted["keywords"] = ContentFormatter.format_keywords(subject, category, formula)
        
        # Ensure standardized image structure
        formatted["images"] = ContentFormatter.format_images(subject)
        
        # Apply standardized technical specifications
        if "technicalSpecifications" not in formatted:
            formatted["technicalSpecifications"] = ContentFormatter.format_technical_specifications()
        else:
            formatted["technicalSpecifications"] = ContentFormatter.format_technical_specifications(
                formatted["technicalSpecifications"]
            )
        
        # Apply standardized regulatory standards
        if "regulatoryStandards" not in formatted:
            formatted["regulatoryStandards"] = ContentFormatter.format_regulatory_standards()
        
        # Apply standardized environmental impact
        if "environmentalImpact" not in formatted:
            formatted["environmentalImpact"] = ContentFormatter.format_environmental_impact(subject)
        
        # Apply standardized outcomes
        if "outcomes" not in formatted:
            formatted["outcomes"] = ContentFormatter.format_outcomes()
        
        # Ensure required fields
        formatted["subject"] = subject
        formatted["article_type"] = article_type
        if category:
            formatted["category"] = category
        
        return formatted
    
    @staticmethod
    def clean_yaml_output(content: str) -> str:
        """Clean YAML output by removing hard returns and unnecessary escaping.
        
        Args:
            content: YAML content string
            
        Returns:
            str: Cleaned YAML content without hard returns and escaping
        """
        # Remove escaped backslashes followed by spaces and newlines within quoted strings
        content = re.sub(r'\\[\s\n]+', ' ', content)
        
        # Remove hard returns within quoted values (indicated by quotes on separate lines)
        lines = content.split('\n')
        cleaned_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this line starts a quoted string that continues on next lines
            if ':' in line and ('"' in line or "'" in line):
                # Find if the string is broken across lines
                if line.count('"') == 1 or line.count("'") == 1:
                    # This is a multi-line quoted string
                    quote_char = '"' if '"' in line else "'"
                    combined_line = line
                    i += 1
                    
                    # Combine lines until we find the closing quote
                    while i < len(lines) and quote_char not in lines[i]:
                        combined_line += ' ' + lines[i].strip()
                        i += 1
                    
                    # Add the final line with closing quote
                    if i < len(lines):
                        combined_line += ' ' + lines[i].strip()
                    
                    cleaned_lines.append(combined_line)
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
            
            i += 1
        
        content = '\n'.join(cleaned_lines)
        
        # Remove backslash escaping at end of lines (YAML line continuation)
        content = re.sub(r'\\\s*\n\s*', ' ', content)
        
        # Clean up extra spaces
        content = re.sub(r'  +', ' ', content)
        
        return content

    @staticmethod
    def extract_yaml_content(content: str) -> str:
        """Extract clean YAML content from various AI response formats."""
        return ContentProcessor.extract_structured_content(content, "yaml")
    
    @staticmethod
    def extract_json_content(content: str) -> str:
        """Extract JSON content from various response formats."""
        return ContentProcessor.extract_structured_content(content, "json")
    
    @staticmethod
    def normalize_yaml_content(content: str) -> str:
        """Normalize YAML content for consistency and proper structure."""
        return ContentProcessor.normalize_structured_content(content, "yaml")
    
    @staticmethod
    def preprocess_ai_content(content: str) -> str:
        """Preprocess AI content to prevent parsing issues."""
        return ContentProcessor.clean_ai_artifacts(content)
    
    @staticmethod
    def _clean_ai_markdown_artifacts(content: str) -> str:
        """Clean markdown artifacts that AI sometimes embeds in YAML values.
        
        Args:
            content: Raw content with potential markdown artifacts
            
        Returns:
            str: Cleaned content with markdown artifacts removed
        """
        # Remove markdown formatting from YAML values (e.g., - **Chemical Formula: "** Al  ")
        content = re.sub(r'^(\s*-\s+)\*\*([^:]+):\s*"\*\*\s*([^"]*?)\s*"\s*$', r'\1\2: "\3"', content, flags=re.MULTILINE)
        
        # Remove markdown bold formatting from YAML values (e.g., **text**)
        content = re.sub(r'(\s*[^:]+:\s*["\']?)\*\*([^*]+)\*\*(["\']?\s*)$', r'\1\2\3', content, flags=re.MULTILINE)
        
        # Remove markdown emphasis from YAML values
        content = re.sub(r'(\s*[^:]+:\s*["\']?)_([^_]+)_(["\']?\s*)$', r'\1\2\3', content, flags=re.MULTILINE)
        
        # Clean up malformed quoted values (e.g., "** text **")
        content = re.sub(r'"\s*\*\*\s*([^*"]+?)\s*\*\*\s*"', r'"\1"', content)
        
        # Remove markdown bold from key names (e.g., **Key**: value)
        content = re.sub(r'^(\s*-?\s*)\*\*([^:*]+)\*\*:\s*(.*)$', r'\1\2: \3', content, flags=re.MULTILINE)
        
        # Clean up any remaining markdown bold markers
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        
        # Remove leftover markdown artifacts in values
        content = re.sub(r'(\s*[^:]+:\s*["\']?)([^"\']*?)\s*"\s*"(["\']?\s*)$', r'\1\2\3', content, flags=re.MULTILINE)
        
        # Fix double quotes issues (e.g., - **Chemical Formula: "** Al  " becomes Chemical Formula: Al)
        content = re.sub(r'^(\s*-?\s*)([^:]+):\s*["\']?\*\*["\']?\s*([^"\']*?)\s*["\']?\s*$', r'\1\2: \3', content, flags=re.MULTILINE)
        
        # Remove trailing quotes and whitespace artifacts from values
        content = re.sub(r'(:\s*[^"\n]*?)\s*["\']?\s*$', r'\1', content, flags=re.MULTILINE)
        
        # Remove incomplete parenthetical content at line endings
        content = re.sub(r'\s*\([^)]*$', '', content, flags=re.MULTILINE)
        
        return content
    
    @staticmethod
    def _fix_malformed_sequences(content: str) -> str:
        """Fix malformed YAML sequences that cause parsing errors.
        
        Args:
            content: YAML content with potential sequence issues
            
        Returns:
            str: Fixed YAML content
        """
        lines = content.split('\n')
        fixed_lines = []
        root_level_is_mapping = False
        
        # First pass: determine if root should be mapping or sequence
        for line in lines:
            if line.strip() and not line.strip().startswith('#'):
                if line.strip().startswith('- ') and ':' in line:
                    # This is a list item with key-value (could be either)
                    continue
                elif ':' in line and not line.strip().startswith('- '):
                    # This is definitely a mapping
                    root_level_is_mapping = True
                    break
        
        for i, line in enumerate(lines):
            # Fix inline sequences with multiple dash-separated items (e.g., "keywords: - item1 - item2 - item3")
            if re.match(r'^(\s*)([^:]+):\s*-\s*.+?\s*-\s*.+', line):
                match = re.match(r'^(\s*)([^:]+):\s*-\s*(.+)$', line)
                if match:
                    indent, key, full_value = match.groups()
                    # Split by ' - ' and create proper YAML list
                    items = [item.strip() for item in full_value.split(' - ') if item.strip()]
                    if len(items) > 1:
                        # Convert to proper YAML list format
                        fixed_lines.append(f'{indent}{key}:')
                        for item in items:
                            # Clean up any incomplete content in parentheses
                            clean_item = re.sub(r'\s*\([^)]*$', '', item.strip())
                            if clean_item:
                                fixed_lines.append(f'{indent}  - "{clean_item}"')
                        continue
            
            # Fix sequences that start inside scalar values (e.g., "useCase: - Text")
            if re.match(r'^(\s*)([^:]+):\s*-\s*(.+)$', line):
                match = re.match(r'^(\s*)([^:]+):\s*-\s*(.+)$', line)
                if match:
                    indent, key, value = match.groups()
                    # Check if this is a single item (not multiple dash-separated items)
                    if ' - ' not in value:
                        # Convert to proper scalar value, removing any trailing incomplete content
                        clean_value = re.sub(r'\s*\([^)]*$', '', value.strip())
                        fixed_lines.append(f'{indent}{key}: "{clean_value}"')
                        continue
            
            # Fix root-level mixed structure by converting list items to mappings if needed
            if root_level_is_mapping and line.strip().startswith('- ') and ':' in line:
                # Convert "- key: value" to "key: value" at root level
                match = re.match(r'^(\s*)-\s+([^:]+):\s*(.*)$', line)
                if match:
                    indent, key, value = match.groups()
                    fixed_lines.append(f'{indent}{key}: {value}')
                    continue
            
            # Fix malformed list items that have broken formatting
            if re.match(r'^(\s*-\s+)([^:]+):\s*(.+?)\s*\($', line):
                match = re.match(r'^(\s*-\s+)([^:]+):\s*(.+?)\s*\($', line)
                if match:
                    indent, key, value = match.groups()
                    # Remove trailing parenthesis and clean up
                    fixed_lines.append(f'{indent}{key}: {value.rstrip()}')
                    continue
                    
            # Fix incomplete sequences or malformed structure
            if re.match(r'^(\s+)([^:]+):\s*(.+?)\s*\([^)]*$', line):
                match = re.match(r'^(\s+)([^:]+):\s*(.+?)\s*\([^)]*$', line)
                if match:
                    indent, key, value = match.groups()
                    # Remove incomplete parenthetical content
                    fixed_lines.append(f'{indent}{key}: {value.rstrip()}')
                    continue
            
            # Fix nested indentation issues
            if line.strip() and not line.startswith(' ') and not line.startswith('-') and ':' in line:
                # This should be properly indented under properties if it looks like a property
                prev_line = fixed_lines[-1] if fixed_lines else ''
                if prev_line.strip() == 'properties:':
                    fixed_lines.append(f'  {line}')
                    continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    @staticmethod
    def _aggressive_yaml_cleanup(content: str) -> str:
        """Perform aggressive cleanup on malformed YAML as last resort.
        
        Args:
            content: Malformed YAML content
            
        Returns:
            str: Aggressively cleaned YAML content
        """
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that would definitely break YAML parsing
            if re.match(r'^\s*Here is|^\s*```|^\s*##|^\s*\*\*[^:]*\*\*\s*$', line):
                continue
                
            # Remove standalone markdown headers
            if re.match(r'^\s*#+\s', line):
                continue
                
            # Fix values that start with markdown and end with quotes
            line = re.sub(r'^(\s*[^:]+):\s*\*\*([^*"]+)\*\*\s*["\']([^"\']*)["\']?\s*$', r'\1: \2 \3', line)
            
            # Remove excessive whitespace and clean up
            line = re.sub(r'\s+', ' ', line)
            line = line.strip()
            
            # Only add non-empty lines
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    @staticmethod
    def _fix_document_structure(content: str) -> str:
        """Fix YAML document structure issues.
        
        Args:
            content: YAML content with potential document structure issues
            
        Returns:
            str: Fixed YAML content with proper document structure
        """
        lines = content.split('\n')
        fixed_lines = []
        in_document = False
        content_lines = []
        
        # Check if content already has frontmatter delimiters
        has_frontmatter_delimiters = any(line.strip() == '---' for line in lines)
        
        # If no frontmatter delimiters, treat as raw YAML and process all content
        if not has_frontmatter_delimiters:
            # For raw YAML content (like AI responses), process all lines
            for line in lines:
                stripped = line.strip()
                
                # Skip completely empty lines at start and end
                if not stripped:
                    continue
                    
                # Skip lines that are just quotes or malformed
                if stripped in ['"', '**', '']:
                    continue
                    
                # Skip lines that look like orphaned values
                if stripped.endswith('"') and ':' not in stripped and not stripped.startswith('-'):
                    continue
                
                content_lines.append(line)
            
        # Fix YAML structure issues before returning
        raw_yaml = '\n'.join(content_lines)
        fixed_yaml = ContentFormatter._fix_yaml_structure(raw_yaml)
        
        # Return the cleaned content without adding frontmatter delimiters
        return fixed_yaml        # Original logic for content that has frontmatter delimiters
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines at the start
            if not stripped and not in_document:
                continue
                
            # Handle document separators
            if stripped == '---':
                if not in_document:
                    # Start of document
                    in_document = True
                    fixed_lines.append(line)
                else:
                    # End of document - ignore additional separators
                    break
                continue
            
            # Skip lines that look like raw markdown or malformed content
            if in_document:
                # Skip lines that are just quotes or malformed
                if stripped in ['"', '**', '']:
                    continue
                    
                # Skip lines that look like orphaned values
                if stripped.endswith('"') and ':' not in stripped and not stripped.startswith('-'):
                    continue
                
                content_lines.append(line)
        
        # If we have content, add it to the document
        if content_lines:
            # Apply YAML structure fixes to the content
            yaml_content = '\n'.join(content_lines)
            fixed_yaml = ContentFormatter._fix_yaml_structure(yaml_content)
            
            # Ensure we have a document start
            if not any(line.strip() == '---' for line in fixed_lines):
                fixed_lines = ['---'] + fixed_yaml.split('\n')
            else:
                fixed_lines.extend(fixed_yaml.split('\n'))
        
        # Clean up the final structure
        result = '\n'.join(fixed_lines)
        
        # Remove any trailing document separators
        result = re.sub(r'\n---\s*$', '', result)
        
        return result

    @staticmethod
    def _fix_yaml_structure(content: str) -> str:
        """Fix major YAML structural issues.
        
        Args:
            content: YAML content string
            
        Returns:
            str: YAML content with fixed structure
        """
        lines = content.split('\n')
        fixed_lines = []
        in_openGraph = False
        in_images = False
        openGraph_indent = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            line_indent = len(line) - len(line.lstrip())
            
            # Track OpenGraph section
            if stripped.startswith('openGraph:'):
                in_openGraph = True
                openGraph_indent = line_indent
                fixed_lines.append(line)
                continue
            
            # End of openGraph section - detect when we're back to root level
            if in_openGraph and stripped and ':' in stripped and line_indent <= openGraph_indent and not stripped.startswith(('title:', 'description:', 'url:', 'siteName:', 'type:', 'locale:', 'images:', 'width:', 'height:', 'alt:')):
                in_openGraph = False
                in_images = False
            
            # Handle content within openGraph
            if in_openGraph:
                # Track images array within OpenGraph
                if stripped.startswith('images:'):
                    in_images = True
                    fixed_lines.append(' ' * (openGraph_indent + 2) + 'images:')
                    continue
                
                # Fix images array items
                elif in_images and stripped.startswith('-'):
                    # Check if this is a standalone image URL
                    image_url = stripped.lstrip('-').strip()
                    if image_url and ':' not in image_url:
                        # Simple URL, keep as array item
                        fixed_lines.append(' ' * (openGraph_indent + 4) + '- ' + image_url)
                        continue
                    else:
                        # Complex image object - end images array and treat as properties
                        in_images = False
                
                # Handle properties that should be nested under openGraph
                elif stripped and ':' in stripped:
                    prop_name = stripped.split(':')[0].strip()
                    if prop_name in ['title', 'description', 'url', 'siteName', 'type', 'locale', 'width', 'height', 'alt']:
                        # Ensure proper indentation under openGraph
                        if line_indent <= openGraph_indent:
                            fixed_lines.append(' ' * (openGraph_indent + 2) + stripped)
                        else:
                            fixed_lines.append(line)
                        continue
            
            # Fix twitter section similar issues
            if stripped.startswith('twitter:') and not stripped.endswith(':'):
                # Ensure twitter section ends with colon
                fixed_lines.append(line.replace('twitter:', 'twitter:'))
                continue
            
            # Fix malformed list items that should be objects
            if stripped.startswith('-') and ':' in stripped and not in_images:
                # This might be a malformed list item that should be an object property
                parts = stripped.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].lstrip('-').strip()
                    value = parts[1].strip()
                    if value:  # Only convert if there's a value
                        fixed_lines.append(' ' * line_indent + key + ': ' + value)
                        continue
            
            # Default: keep the line as is
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    @staticmethod  
    def _escape_yaml_values(content: str) -> str:
        """Escape YAML values that need quoting.
        
        Args:
            content: YAML content string
            
        Returns:
            str: YAML content with properly escaped values
        """
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Only process lines that contain key-value pairs
            if ':' in line and not line.strip().startswith('#'):
                # Split on first colon to separate key and value
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key_part = parts[0]
                    value_part = parts[1].strip()
                    
                    # If value needs escaping (contains special chars but isn't quoted)
                    if value_part and not (value_part.startswith('"') and value_part.endswith('"')):
                        # Enhanced detection for problematic characters
                        needs_quotes = False
                        
                        # Check for colons (main issue causing the error)
                        if ':' in value_part:
                            needs_quotes = True
                        # Check for YAML scalar indicators that break parsing
                        elif value_part.startswith('>') or value_part.startswith('|'):
                            needs_quotes = True
                        # Check for percentage values that start with > (like >95%)
                        elif re.search(r'>\d+%', value_part):
                            needs_quotes = True
                        # Check for other YAML special characters
                        elif any(char in value_part for char in ['[', ']', '{', '}', '!', '&', '*', '#', '?', '<', '=', '%', '@', '`']):
                            needs_quotes = True
                        # Check for parentheses which often contain colons
                        elif '(' in value_part or ')' in value_part:
                            needs_quotes = True
                        # Check for markdown formatting remnants
                        elif '**' in value_part or '__' in value_part:
                            needs_quotes = True
                        
                        if needs_quotes:
                            # Clean and escape the value
                            cleaned_value = ContentFormatter._clean_value_for_yaml(value_part)
                            escaped_value = cleaned_value.replace('"', '\\"')
                            fixed_lines.append(f'{key_part}: "{escaped_value}"')
                            continue
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    @staticmethod
    def _clean_value_for_yaml(value: str) -> str:
        """Clean a YAML value by removing problematic formatting.
        
        Args:
            value: Raw value that may contain formatting issues
            
        Returns:
            str: Cleaned value suitable for YAML
        """
        # Remove markdown bold/emphasis
        value = re.sub(r'\*\*([^*]+)\*\*', r'\1', value)
        value = re.sub(r'__([^_]+)__', r'\1', value)
        value = re.sub(r'_([^_]+)_', r'\1', value)
        
        # Remove standalone asterisks and underscores
        value = re.sub(r'\s*\*+\s*', ' ', value)
        value = re.sub(r'\s*_+\s*', ' ', value)
        
        # Clean up excessive whitespace
        value = re.sub(r'\s+', ' ', value)
        value = value.strip()
        
        return value
    
    @staticmethod
    def _preprocess_malformed_ai_content(content: str) -> str:
        """Preprocess malformed AI content patterns before YAML extraction.
        
        Args:
            content: Raw AI content with potential malformed patterns
            
        Returns:
            str: Preprocessed content with common malformed patterns fixed
        """
        # Remove introductory text that AI sometimes adds
        content = re.sub(r'^Here\s+is.*?:\s*\n', '', content, flags=re.IGNORECASE)
        content = re.sub(r'^Below\s+is.*?:\s*\n', '', content, flags=re.IGNORECASE)
        content = re.sub(r'^The\s+following.*?:\s*\n', '', content, flags=re.IGNORECASE)
        
        # Fix malformed list items with markdown (e.g., "- **Key: "** value")
        content = re.sub(r'^(\s*-\s+)\*\*([^:]+):\s*["\']?\*\*\s*([^"\']*?)\s*["\']?\s*$', 
                        r'\1\2: \3', content, flags=re.MULTILINE)
        
        # Fix malformed key-value pairs with markdown (e.g., "**Key: "** value")
        content = re.sub(r'^(\s*)\*\*([^:]+):\s*["\']?\*\*\s*([^"\']*?)\s*["\']?\s*$', 
                        r'\1\2: \3', content, flags=re.MULTILINE)
        
        # Fix values that end with opening parentheses (incomplete content)
        content = re.sub(r'^(\s*[^:]+):\s*(.+?)\s*\(\s*$', r'\1: \2', content, flags=re.MULTILINE)
        
        # Remove markdown formatting from values
        content = re.sub(r'(\s*[^:]+:\s*)"([^"]*?)\*\*([^*"]*?)\*\*([^"]*?)"', r'\1"\2\3\4"', content)
        
        # Fix broken quoted values
        content = re.sub(r'(\s*[^:]+:\s*)"\s*([^"]*?)\s*"\s*"([^"]*?)"\s*', r'\1"\2 \3"', content)
        
        return content
        
    @staticmethod
    def extract_content_between_markers(content: str, marker: str = '---') -> str:
        """Extract content between YAML frontmatter markers.
        
        Args:
            content: Content with markers
            marker: Marker string (default: '---')
            
        Returns:
            str: Content between first set of markers
        """
        if marker in content:
            parts = content.split(marker)
            if len(parts) >= 3:
                return parts[1].strip()
            elif len(parts) == 2:
                return parts[1].strip()
        
        return content.strip()
    
    @staticmethod
    def clean_string_content(text: str) -> str:
        """Clean string content by removing escape characters and normalizing whitespace.
        
        Args:
            text: Text to clean
            
        Returns:
            str: Cleaned text
        """
        if not isinstance(text, str):
            return text
        
        # Remove escape characters
        text = text.replace("\\n", "\n").replace('\\ ', ' ')
        
        # Normalize whitespace in multiline strings
        if '\n' in text:
            lines = text.split('\n')
            text = '\n'.join(line.strip() for line in lines if line.strip())
        
        return text
    
    @staticmethod
    def normalize_case(text: str, case_type: str = 'lower') -> str:
        """Normalize text case consistently.
        
        Args:
            text: Text to normalize
            case_type: 'lower', 'upper', 'title', or 'sentence'
            
        Returns:
            str: Normalized text
        """
        if not isinstance(text, str):
            return text
        
        if case_type == 'lower':
            return text.lower()
        elif case_type == 'upper':
            return text.upper()
        elif case_type == 'title':
            return text.title()
        elif case_type == 'sentence':
            return text.capitalize()
        
        return text
    
    @staticmethod
    def extract_tags_from_content(content: str) -> List[str]:
        """Extract and normalize tags from various content formats.
        
        Args:
            content: Content containing tags
            
        Returns:
            List[str]: List of normalized tags
        """
        tags = []
        lines = content.strip().split('\n')
        
        # Process each line looking for tags
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Handle comma-separated tags in a single line
            if ',' in line:
                tags.extend([tag.strip() for tag in line.split(',') if tag.strip()])
            else:
                # Single tag per line (possibly with bullet points)
                line = re.sub(r'^[-*•]\s*', '', line)  # Remove bullet points
                if line:
                    tags.append(line)
        
        # Clean and deduplicate
        return list(set([tag.strip() for tag in tags if tag.strip()]))
    
    @staticmethod
    def format_author_info(author_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format author information consistently.
        
        Args:
            author_data: Raw author data
            
        Returns:
            Dict: Formatted author information
        """
        if not author_data:
            # Strict mode: No fallback author data
            raise ValueError("Author data is required but not provided")
        
        formatted = {}
        
        # Map common field variations
        if "author_name" in author_data:
            formatted["name"] = author_data["author_name"]
        elif "name" in author_data:
            formatted["name"] = author_data["name"]
        
        if "author_country" in author_data:
            formatted["country"] = author_data["author_country"]
        elif "country" in author_data:
            formatted["country"] = author_data["country"]
        
        if "author_id" in author_data:
            formatted["id"] = author_data["author_id"]
        elif "id" in author_data:
            formatted["id"] = author_data["id"]
        else:
            # Strict mode: No fallback author ID
            raise ValueError("Author ID is required but not found in author data")
        
        # Add credentials if available
        if "credentials" in author_data:
            formatted["credentials"] = author_data["credentials"]
        
        return formatted
    
    @staticmethod
    def get_author_name(author_data: Dict[str, Any]) -> str:
        """Get the author name from author data using standard field mapping.
        
        Args:
            author_data: Raw author data dictionary
            
        Returns:
            str: Author name
            
        Raises:
            ValueError: If author name cannot be found
        """
        if not author_data:
            raise ValueError("Author data is required but not provided")
        
        # Use the same mapping logic as format_author_info
        if "author_name" in author_data:
            return author_data["author_name"]
        elif "name" in author_data:
            return author_data["name"]
        else:
            raise ValueError("Author name not found in author data (looked for 'author_name' and 'name' fields)")
    
    @staticmethod
    def create_author_tag(author_data: Dict[str, Any]) -> str:
        """Create a standardized author tag from author data.
        
        Args:
            author_data: Raw author data dictionary
            
        Returns:
            str: Author name converted to kebab-case tag format
        """
        author_name = ContentFormatter.get_author_name(author_data)
        
        # Convert to kebab-case using SlugUtils
        from components.base.utils.slug_utils import SlugUtils
        return SlugUtils.create_slug(author_name)
    
    @staticmethod
    def format_metatags_structure(parsed_data: Dict[str, Any], subject: str, category: str = None) -> Dict[str, Any]:
        """Format metatags structure for Next.js compatibility.
        
        This method ensures all metatags follow the expected Next.js structure
        without doing any local formatting - just structural organization.
        
        Args:
            parsed_data: Raw parsed YAML data from AI
            subject: The subject material/topic
            category: Material category if applicable
            
        Returns:
            Dict: Properly structured metatags for Next.js
        """
        from components.base.utils.slug_utils import SlugUtils
        
        # Normalize field names first (handle inconsistent AI output)
        normalized_data = {}
        for key, value in parsed_data.items():
            # Normalize common metatag field name variations
            if key.lower() in ['title', 'meta_title']:
                normalized_data['meta_title'] = value
            elif key.lower() in ['description', 'meta_description']:
                normalized_data['meta_description'] = value
            elif key.lower() in ['keywords', 'meta_keywords']:
                normalized_data['meta_keywords'] = value
            else:
                # Keep other fields as-is
                normalized_data[key] = value
        
        # Use the normalized data for structure formatting
        formatted = {}
        
        # Basic meta fields (use AI content if provided, otherwise use centralized formatting)
        if "meta_title" in normalized_data:
            formatted["meta_title"] = normalized_data["meta_title"]
        elif "title" in normalized_data:
            formatted["meta_title"] = normalized_data["title"]
        else:
            formatted["meta_title"] = ContentFormatter.format_title(subject)
            
        if "meta_description" in normalized_data:
            formatted["meta_description"] = normalized_data["meta_description"]
        elif "description" in normalized_data:
            formatted["meta_description"] = normalized_data["description"]
        else:
            formatted["meta_description"] = ContentFormatter.format_description(subject)
            
        if "meta_keywords" in normalized_data:
            formatted["meta_keywords"] = normalized_data["meta_keywords"]
        elif "keywords" in normalized_data:
            formatted["meta_keywords"] = normalized_data["keywords"]
        else:
            keywords = ContentFormatter.format_keywords(subject, category)
            formatted["meta_keywords"] = ", ".join(keywords)
        
        # Ensure openGraph structure exists
        if "openGraph" not in normalized_data:
            formatted["openGraph"] = {}
        else:
            formatted["openGraph"] = normalized_data["openGraph"].copy()
            
        og = formatted["openGraph"]
        
        # Use subject slug for consistent URLs
        subject_slug = SlugUtils.create_slug(subject)
        
        # Ensure required openGraph fields
        if "title" not in og:
            og["title"] = formatted["meta_title"]
        if "description" not in og:
            og["description"] = formatted["meta_description"]
        if "url" not in og:
            og["url"] = f"https://www.z-beam.com/{subject_slug}-laser-cleaning"
        if "siteName" not in og:
            og["siteName"] = "Z-Beam"
        if "type" not in og:
            og["type"] = "article"
        if "locale" not in og:
            og["locale"] = "en_US"
            
        # Ensure images structure
        if "images" not in og or not og["images"]:
            images_data = ContentFormatter.format_images(subject)
            og["images"] = [
                {
                    "url": images_data["hero"]["url"],
                    "width": 1200,
                    "height": 630,
                    "alt": images_data["hero"]["alt"]
                }
            ]
        
        # Ensure twitter structure exists
        if "twitter" not in parsed_data:
            formatted["twitter"] = {}
        else:
            formatted["twitter"] = parsed_data["twitter"].copy()
            
        twitter = formatted["twitter"]
        
        # Ensure required twitter fields
        if "card" not in twitter:
            twitter["card"] = "summary_large_image"
        if "title" not in twitter:
            twitter["title"] = og.get("title", formatted["meta_title"])
        if "description" not in twitter:
            twitter["description"] = og.get("description", formatted["meta_description"])
        if "images" not in twitter or not twitter["images"]:
            if og.get("images"):
                twitter["images"] = [og["images"][0]["url"]]
        
        # Copy other fields from AI if they exist (exclude normalized fields)
        for key, value in normalized_data.items():
            if key not in ["meta_title", "meta_description", "meta_keywords", "title", "description", "keywords", "openGraph", "twitter"]:
                formatted[key] = value
        
        return formatted
    
    @staticmethod
    def format_created_date() -> str:
        """Generate standardized created date.
        
        Returns:
            str: ISO formatted created date
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def format_updated_date() -> str:
        """Generate standardized updated date.
        
        Returns:
            str: ISO formatted updated date
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def format_publish_date() -> str:
        """Generate standardized publish date.
        
        Returns:
            str: ISO formatted publish date
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    @staticmethod
    def format_iso_date() -> str:
        """Generate standardized ISO date.
        
        Returns:
            str: Full ISO formatted datetime
        """
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def extract_structured_data_from_text(content: str, subject: str) -> Dict[str, Any]:
        """Extract structured data from any text format for frontmatter.
        
        This method can handle raw text, markdown, partial YAML, or any other format
        and extract the technical information needed for frontmatter.
        
        Args:
            content: Raw text content from AI
            subject: The subject being processed
            
        Returns:
            Dict[str, Any]: Structured data extracted from text
        """
        import re
        
        result = {
            'name': subject,  # Use the subject as the base name
        }
        
        # Extract properties (look for numeric values with units)
        properties = {}
        
        # Common property patterns
        property_patterns = [
            (r'density[:\s]*([0-9.,–\-\s]+g/cm³)', 'density'),
            (r'melting\s*point[:\s]*([0-9.,–\-\s]+°?C)', 'meltingPoint'),
            (r'thermal\s*conductivity[:\s]*([0-9.,–\-\s]+W/m[·•]K)', 'thermalConductivity'),
            (r'hardness[:\s]*([0-9.,–\-\s]+Mohs)', 'hardness'),
            (r'flexural\s*strength[:\s]*([0-9.,–\-\s]+MPa)', 'flexuralStrength'),
            (r'tensile\s*strength[:\s]*([0-9.,–\-\s]+MPa)', 'tensileStrength'),
            (r'compressive\s*strength[:\s]*([0-9.,–\-\s]+MPa)', 'compressiveStrength'),
        ]
        
        for pattern, key in property_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                properties[key] = match.group(1).strip()
        
        if properties:
            result['properties'] = properties
        
        # Extract applications (look for industry contexts)
        applications = []
        
        # Look for application patterns
        app_patterns = [
            r'\*\*([^*]+)\*\*:\s*([^*\n]+)',  # **Industry**: Description
            r'([A-Z][a-z]+\s*[A-Z]*[a-z]*):\s*([^:\n]+)',  # Industry: Description
        ]
        
        for pattern in app_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) == 2:
                    industry, description = match
                    if len(industry) > 2 and len(description) > 10:  # Reasonable length check
                        applications.append({
                            'industry': industry.strip(),
                            'useCase': description.strip(),
                        })
        
        if applications:
            result['applications'] = applications[:5]  # Limit to 5 applications
        
        return result

    @staticmethod
    def extract_bullet_points(content: str) -> List[str]:
        """Extract bullet points from AI-generated content.
        
        Args:
            content: Raw generated content with bullet points
            
        Returns:
            List[str]: Extracted bullet points
        """
        lines = content.strip().split('\n')
        bullet_items = []
        
        # Process lines to extract bullet content
        current_bullet = None
        
        for line in lines:
            line = line.strip()
            # Check if this line starts a bullet point
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                # If we have a bullet in progress, save it
                if current_bullet:
                    bullet_items.append(current_bullet)
                
                # Start a new bullet
                current_bullet = line[1:].strip()
            # Check if this is a numbered bullet
            elif re.match(r'^\d+\.', line):
                # If we have a bullet in progress, save it
                if current_bullet:
                    bullet_items.append(current_bullet)
                
                # Start a new bullet (remove the number and period)
                current_bullet = re.sub(r'^\d+\.', '', line).strip()
            # Check if this is a continuation of the current bullet
            elif current_bullet and line:
                # Append to current bullet with a space
                current_bullet += " " + line
        
        # Add the last bullet if there's one in progress
        if current_bullet:
            bullet_items.append(current_bullet)
        
        return [item for item in bullet_items if item.strip()]

    @staticmethod
    def clean_tags_from_content(content: str) -> List[str]:
        """Extract and clean tags from AI-generated content.
        
        Args:
            content: Raw content containing tags
            
        Returns:
            List[str]: Cleaned list of tags
        """
        if not content or not content.strip():
            return []
            
        # Split content into potential tags
        # Support various formats: comma-separated, line-separated, etc.
        potential_tags = []
        
        # Try comma-separated first
        if ',' in content:
            potential_tags = [tag.strip() for tag in content.split(',')]
        # Try line-separated
        elif '\n' in content:
            potential_tags = [tag.strip() for tag in content.split('\n')]
        # Try space-separated
        else:
            potential_tags = [tag.strip() for tag in content.split()]
        
        # Clean and validate tags
        clean_tags = []
        for tag in potential_tags:
            if not tag or not tag.strip():
                continue
                
            # Remove common prefixes/suffixes
            clean_tag = tag.strip().lower()
            
            # Remove bullet points, numbers, quotes, etc.
            clean_tag = re.sub(r'^[-*•\d\.]+\s*', '', clean_tag)
            clean_tag = re.sub(r'^["\']|["\']$', '', clean_tag)
            clean_tag = clean_tag.strip()
            
            # Skip if too short or too long
            if len(clean_tag) < 2 or len(clean_tag) > 50:
                continue
                
            # Skip if it contains suspicious characters
            if re.search(r'[<>{}|\[\]]', clean_tag):
                continue
                
            clean_tags.append(clean_tag)
        
        return clean_tags[:10]  # Limit to 10 tags

    @staticmethod
    def sanitize_frontmatter_content(content: str) -> str:
        """Remove malformed content and standardize URLs in frontmatter.
        
        Args:
            content: Raw frontmatter content
            
        Returns:
            str: Sanitized content
        """
        lines = []
        for line in content.split('\n'):
            # Remove lines with malformed image URLs
            if re.match(r'^-*>*-*laser-cleaning.*\.jpg$', line.strip()):
                continue
            lines.append(line)
        
        content = '\n'.join(lines)
        
        # Fix malformed URL patterns
        content = re.sub(r'-+>+-*', '-', content)
        content = re.sub(r'([^a-z])>+-*', r'\1', content)
        
        # Fix image URL patterns
        content = re.sub(r'(/images/[a-z0-9-]+)laser-cleaning', r'\1-laser-cleaning', content)
        
        # Fix double dashes in image URLs
        content = re.sub(r'(/images/[^"]*?)--+([^"]*?\.jpg)', r'\1-\2', content)
        
        return content

    @staticmethod
    def preprocess_ai_content(content: str) -> str:
        """Preprocess AI content to prevent YAML parsing issues.
        
        This removes common formatting that AI incorrectly adds which causes YAML parsing failures.
        
        Args:
            content: Raw AI response content
            
        Returns:
            str: Cleaned content safe for processing
        """
        # Remove markdown bold/italic formatting that breaks YAML
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)  # Remove **bold**
        content = re.sub(r'\*(.*?)\*', r'\1', content)      # Remove *italic*
        content = re.sub(r'`(.*?)`', r'\1', content)        # Remove `code`
        
        # Remove problematic YAML characters in unexpected places
        content = re.sub(r'(?m)^(\s*)-\s*\*\*([^*]+)\*\*:', r'\1\2:', content)  # Fix "- **Key**:" to "Key:"
        content = re.sub(r'(?m)^(\s*)\*\*([^*]+)\*\*:', r'\1\2:', content)      # Fix "**Key**:" to "Key:"
        
        # Remove code block markers if present
        content = re.sub(r'^```[a-z]*\n?', '', content, flags=re.MULTILINE)
        content = re.sub(r'\n?```$', '', content, flags=re.MULTILINE)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)  # Remove excessive blank lines
        content = content.strip()
        
        return content
