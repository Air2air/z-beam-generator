"""
Material Data Context Provider

Provides real-world facts about materials to ground AI generation in reality.
Reduces generic, AI-like descriptions by injecting specific, verifiable data.
"""

import logging
import random
from pathlib import Path
from typing import Any, Dict, Optional

from shared.utils.file_io import read_yaml_file
from shared.text.utils.prompt_registry_service import PromptRegistryService

logger = logging.getLogger(__name__)


class DataProvider:
    """
    Provides material context data from Materials.yaml.
    
    Uses existing material database instead of web search to ensure
    accuracy and avoid external API dependencies.
    """
    
    def __init__(self, materials_path: Optional[Path] = None):
        """
        Initialize data provider.
        
        Args:
            materials_path: Path to Materials.yaml (default: data/materials/Materials.yaml)
        """
        if materials_path is None:
            materials_path = Path(__file__).parent.parent.parent / "data" / "materials" / "Materials.yaml"
        
        self.materials_path = Path(materials_path)
        self.settings_path = Path(__file__).parent.parent.parent / "data" / "settings" / "Settings.yaml"
        self.applications_path = Path(__file__).parent.parent.parent / "data" / "applications" / "Applications.yaml"
        self._materials = None
        self._settings = None
        self._applications = None
        self._schema_cache = None  # Cache for section_display_schema.yaml
    
    def _load_materials(self):
        """Lazy load materials database"""
        if self._materials is None:
            data = read_yaml_file(self.materials_path)
            if not isinstance(data, dict):
                raise TypeError("Materials.yaml must parse to a dictionary")
            if 'materials' not in data:
                raise KeyError("Materials.yaml missing required top-level key: 'materials'")
            if not isinstance(data['materials'], dict):
                raise TypeError("Materials.yaml key 'materials' must be a dictionary")

            self._materials = data['materials']
            logger.info(f"Loaded {len(self._materials)} materials")

    def _load_settings(self):
        """Lazy load settings database"""
        if self._settings is None:
            data = read_yaml_file(self.settings_path)
            if not isinstance(data, dict):
                raise TypeError("Settings.yaml must parse to a dictionary")
            if 'settings' not in data:
                raise KeyError("Settings.yaml missing required top-level key: 'settings'")
            if not isinstance(data['settings'], dict):
                raise TypeError("Settings.yaml key 'settings' must be a dictionary")

            self._settings = data['settings']
            logger.info(f"Loaded {len(self._settings)} settings entries")

    def _load_applications(self):
        """Lazy load applications database"""
        if self._applications is None:
            data = read_yaml_file(self.applications_path)
            if not isinstance(data, dict):
                raise TypeError("Applications.yaml must parse to a dictionary")
            if 'applications' not in data:
                raise KeyError("Applications.yaml missing required top-level key: 'applications'")
            if not isinstance(data['applications'], dict):
                raise TypeError("Applications.yaml key 'applications' must be a dictionary")

            self._applications = data['applications']
            logger.info(f"Loaded {len(self._applications)} applications")

    def _extract_applications(self, material: str, material_data: Dict[str, Any]) -> str:
        """Extract applications text from current or legacy material schema."""
        if 'applications' in material_data:
            applications = material_data['applications']
            if not isinstance(applications, str):
                raise TypeError(f"Material '{material}' key 'applications' must be a string")
            return applications

        relationships = material_data.get('relationships')
        if not isinstance(relationships, dict):
            raise KeyError(f"Material '{material}' missing required key: 'relationships'")

        operational = relationships.get('operational')
        if not isinstance(operational, dict):
            raise KeyError(f"Material '{material}' relationships missing required key: 'operational'")

        industry_applications = operational.get('industryApplications')
        if not isinstance(industry_applications, dict):
            raise KeyError(
                f"Material '{material}' relationships.operational missing required key: 'industryApplications'"
            )

        items = industry_applications.get('items')
        if not isinstance(items, list):
            raise TypeError(
                f"Material '{material}' relationships.operational.industryApplications.items must be a list"
            )

        application_names = []
        for item in items:
            if isinstance(item, dict):
                name = item.get('name')
                if name and isinstance(name, str):
                    application_names.append(name)
            elif isinstance(item, str):
                application_names.append(item)

        if not application_names:
            raise ValueError(f"Material '{material}' has no valid industry application names")

        return ', '.join(application_names)

    def _extract_machine_settings_data(self, material: str, material_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract machine settings payload from material data or linked settings record."""
        if 'machine_settings' in material_data:
            machine_settings = material_data['machine_settings']
            if not isinstance(machine_settings, dict):
                raise TypeError(f"Material '{material}' key 'machine_settings' must be a dictionary")
            return machine_settings

        self._load_settings()

        base_slug = material[:-len('-laser-cleaning')] if material.endswith('-laser-cleaning') else material
        settings_key = f"{base_slug}-settings"

        if settings_key not in self._settings:
            raise KeyError(
                f"Material '{material}' missing machine settings and no settings entry found for key '{settings_key}'"
            )

        settings_entry = self._settings[settings_key]
        if not isinstance(settings_entry, dict):
            raise TypeError(f"Settings entry '{settings_key}' must be a dictionary")

        if 'machineSettings' not in settings_entry:
            raise KeyError(f"Settings entry '{settings_key}' missing required key: 'machineSettings'")

        machine_settings = settings_entry['machineSettings']
        if not isinstance(machine_settings, dict):
            raise TypeError(f"Settings entry '{settings_key}' key 'machineSettings' must be a dictionary")

        return machine_settings
    
    def _load_schema(self):
        """Lazy load section display schema"""
        if self._schema_cache is None:
            self._schema_cache = PromptRegistryService.get_schema()
            if not isinstance(self._schema_cache, dict):
                raise TypeError("Section display schema must be a dictionary")
            logger.debug("Loaded section display schema")
    
    def get_structural_pattern(self, component_type: str) -> Optional[str]:
        """
        Select a random structural pattern for the given component type.
        
        Provides variety in opening structures to prevent repetitive "Property X, Y, and Z..." patterns.
        Uses weighted random selection based on pattern weights in schema.
        
        Args:
            component_type: Component type (e.g., 'materialCharacteristics_description')
            
        Returns:
            Structural pattern instruction string, or None if no patterns defined
        """
        self._load_schema()

        # Get property pool for this component type
        if 'property_pools' not in self._schema_cache:
            raise KeyError("Section display schema missing required key: 'property_pools'")

        property_pools = self._schema_cache['property_pools']
        if not isinstance(property_pools, dict):
            raise TypeError("Schema key 'property_pools' must be a dictionary")

        if component_type not in property_pools:
            logger.debug(f"No structural patterns defined for {component_type}")
            return None

        pool_config = property_pools[component_type]
        if not isinstance(pool_config, dict):
            raise TypeError(f"Schema property pool '{component_type}' must be a dictionary")

        if 'structural_patterns' not in pool_config:
            logger.debug(f"No structural patterns defined for {component_type}")
            return None

        patterns = pool_config['structural_patterns']
        if not isinstance(patterns, list):
            raise TypeError(f"Schema structural_patterns for '{component_type}' must be a list")
        
        if not patterns:
            logger.debug(f"No structural patterns defined for {component_type}")
            return None
        
        # Weighted random selection
        weights = []
        for pattern in patterns:
            if not isinstance(pattern, dict):
                raise TypeError(f"Schema pattern for '{component_type}' must be a dictionary")
            if 'weight' not in pattern:
                raise KeyError(
                    f"Schema pattern for '{component_type}' missing required key: 'weight'"
                )
            weights.append(pattern['weight'])
        selected = random.choices(patterns, weights=weights, k=1)[0]
        
        logger.info(f"Selected structural pattern '{selected['id']}' for {component_type}")
        return selected['instruction']
    
    def fetch_real_facts(self, material: str, component_type: str = None) -> Dict[str, Any]:
        """
        Fetch real facts about material from database.
        
        READS pre-populated distinctive properties from source data.
        DOES NOT calculate them on-the-fly (Core Principle 0.6 compliance).
        
        Args:
            material: Material name
            component_type: Component type for section-specific property reading (optional)
            
        Returns:
            Dict with properties, applications, machine settings, etc.
        """
        self._load_materials()

        if material in self._materials:
            material_data = self._materials[material]
            if not isinstance(material_data, dict):
                raise TypeError(f"Material data for '{material}' must be a dictionary")

            # Extract key facts
            required_material_keys = ['category', 'subcategory', 'properties']
            missing_material_keys = [key for key in required_material_keys if key not in material_data]
            if missing_material_keys:
                raise KeyError(
                    f"Material '{material}' missing required keys: {', '.join(missing_material_keys)}"
                )

            applications_text = self._extract_applications(material, material_data)
            machine_settings_payload = self._extract_machine_settings_data(material, material_data)

            facts = {
                'category': material_data['category'],
                'subcategory': material_data['subcategory'],
                'properties': {},
                'distinctive_properties': [],  # Read from source data, not calculated
                'applications': applications_text,
                'machine_settings': {},
                'key_challenges': '',
                'structural_pattern': None  # Structural variety instruction
            }
        else:
            self._load_applications()
            if material not in self._applications:
                raise KeyError(f"No data found for identifier: {material}")

            application_data = self._applications[material]
            if not isinstance(application_data, dict):
                raise TypeError(f"Application data for '{material}' must be a dictionary")

            required_application_keys = ['category', 'subcategory']
            missing_application_keys = [key for key in required_application_keys if key not in application_data]
            if missing_application_keys:
                raise KeyError(
                    f"Application '{material}' missing required keys: {', '.join(missing_application_keys)}"
                )

            facts = {
                'category': application_data['category'],
                'subcategory': application_data['subcategory'],
                'properties': {},
                'distinctive_properties': [],
                'applications': application_data.get('name', ''),
                'machine_settings': {},
                'key_challenges': '',
                'structural_pattern': None
            }
        
        is_material = material in self._materials

        # Select structural pattern for variety (if component_type provided)
        if component_type:
            facts['structural_pattern'] = self.get_structural_pattern(component_type)
        
        if is_material:
            # Extract property values from nested structure
            material_props = material_data['properties']
            if not isinstance(material_props, dict):
                raise TypeError(f"Material '{material}' key 'properties' must be a dictionary")

            if 'materialCharacteristics' not in material_props:
                raise KeyError(
                    f"Material '{material}' properties missing required key: 'materialCharacteristics'"
                )

            material_chars = material_props['materialCharacteristics']

            # COMPATIBILITY: Handle both old string format and new dict format (Jan 14, 2026)
            if isinstance(material_chars, dict):
                # New structured format with title/description
                if 'title' in material_chars or 'description' in material_chars:
                    # Schema-based format - skip property extraction
                    logger.debug(f"Skipping property extraction for {material} - materialCharacteristics is schema-formatted")
                else:
                    # Dict with actual properties
                    for prop_name, prop_data in material_chars.items():
                        if isinstance(prop_data, dict) and 'value' in prop_data:
                            value = prop_data.get('value')
                            unit = prop_data['unit'] if 'unit' in prop_data else ''
                            if value is not None:
                                facts['properties'][prop_name] = f"{value} {unit}".strip()
            else:
                # Old embedded markdown string format - skip property extraction
                logger.debug(f"Skipping property extraction for {material} - materialCharacteristics is old string format")

            # READ pre-populated distinctive properties from source data (if available)
            # These should be written by backfill/research scripts, NOT calculated here
            if component_type:
                # Check for section-specific distinctive properties in source data
                section_key = f"_distinctive_{component_type}"
                if section_key in material_data:
                    facts['distinctive_properties'] = material_data[section_key]
                    logger.info(f"Read {len(facts['distinctive_properties'])} pre-populated distinctive properties for {material}.{component_type}")
                else:
                    logger.debug(f"No pre-populated distinctive properties found for {material}.{component_type} (run backfill to populate)")

            # Extract machine settings from nested structure
            laser_settings = machine_settings_payload['laser_settings'] if 'laser_settings' in machine_settings_payload else {}
            settings = laser_settings if laser_settings else machine_settings_payload

            # COMPATIBILITY: Handle both dict and string formats (Jan 14, 2026)
            if isinstance(settings, dict):
                for setting_name, setting_data in settings.items():
                    if isinstance(setting_data, dict):
                        value = setting_data.get('value')
                        unit = setting_data['unit'] if 'unit' in setting_data else ''
                        if value:
                            facts['machine_settings'][setting_name] = f"{value} {unit}".strip()
            else:
                logger.debug(f"Skipping settings extraction for {material} - machine_settings is non-dict format")

            logger.info(
                f"Enriched {material} with {len(facts['properties'])} properties, "
                f"{len(facts['machine_settings'])} settings"
            )
        
        return facts
    
    def format_facts_for_prompt(self, facts: Dict, enrichment_params: Optional[Dict] = None, technical_intensity: int = 50, voice_params: Optional[Dict] = None) -> str:
        """
        Format facts as prompt-friendly string with density and style controlled by enrichment_params.
        
        Args:
            facts: Facts dict from fetch_real_facts()
            enrichment_params: Dict from DynamicConfig.calculate_enrichment_params() with:
                - technical_intensity: 0-100 (spec density)
                - context_detail_level: 0-100 (description verbosity)
                - fact_formatting_style: 'formal'|'balanced'|'conversational'
                - engagement_level: 0-100 (informal language)
            technical_intensity: Backward compatibility (used if enrichment_params is None)
            voice_params: Dict from DynamicConfig.calculate_voice_parameters() with:
                - jargon_removal: 0.0-1.0 (high = remove jargon)
            
        Returns:
            Formatted string for injection into prompts
        """
        # Phase 3A: Extract params from enrichment_params or fall back to technical_intensity
        if enrichment_params:
            required_keys = [
                'technical_intensity',
                'context_detail_level',
                'fact_formatting_style',
                'engagement_level',
            ]
            missing = [key for key in required_keys if key not in enrichment_params]
            if missing:
                raise KeyError(
                    f"enrichment_params missing required keys: {', '.join(missing)}"
                )

            tech_intensity = enrichment_params['technical_intensity']
            context_detail = enrichment_params['context_detail_level']
            fact_style = enrichment_params['fact_formatting_style']
            engagement = enrichment_params['engagement_level']
        else:
            # Backward compatibility
            tech_intensity = technical_intensity
            context_detail = 0.22  # 0.0-1.0 normalized (slider 3 on 1-10 scale)
            fact_style = 'balanced'
            engagement = 0.22  # 0.0-1.0 normalized (slider 3 on 1-10 scale)
        lines = []
        
        # NEW: Include structural pattern instruction first (drives opening variety)
        if facts.get('structural_pattern'):
            lines.append("STRUCTURAL APPROACH:")
            lines.append(f"  {facts['structural_pattern']}")
            lines.append("")  # Blank line for separation
        
        # Always include category with context detail
        if facts.get('category'):
            category_line = f"Category: {facts['category']}"
            # Add subcategory based on context_detail_level
            if context_detail >= 2 and facts.get('subcategory'):
                category_line += f" ({facts['subcategory']})"
            lines.append(category_line)
        
        # NEW: Include distinctive properties first (most important for variation)
        if facts.get('distinctive_properties'):
            lines.append("\nDISTINCTIVE PROPERTIES (most unique to this material):")
            for prop in facts['distinctive_properties']:
                name_display = prop['name'].replace('_', ' ').title()
                value_str = f"{prop['value']} {prop['unit']}".strip()
                
                # Add comparison if highly distinctive (z-score > 1.5)
                if 'distinctiveness_score' not in prop:
                    raise KeyError("Distinctive property missing required key: 'distinctiveness_score'")
                if prop['distinctiveness_score'] > 1.5:
                    if 'category_mean' not in prop:
                        raise KeyError("Distinctive property missing required key: 'category_mean'")
                    comparison = 'significantly higher' if float(prop['value']) > prop['category_mean'] else 'significantly lower'
                    lines.append(f"  • {name_display}: {value_str} ({comparison} than category average)")
                else:
                    lines.append(f"  • {name_display}: {value_str}")
        
        # Check jargon_removal level - if high, exclude ALL technical specs
        jargon_removal = None
        if voice_params is not None:
            if 'jargon_removal' not in voice_params:
                raise KeyError("voice_params missing required key: 'jargon_removal'")
            jargon_removal = voice_params['jargon_removal']

        if jargon_removal is not None and jargon_removal > 0.7:
            # High jargon removal: NO technical specs at all
            logger.info(f"High jargon removal ({jargon_removal:.3f}) - excluding all technical specs")
            max_props = 0
            max_settings = 0
            include_apps = True  # Applications are usually plain language
        else:
            # Calculate how many specs to include based on technical_intensity (0.0-1.0 normalized)
            # Linear mapping: 0.0 (slider 1) → 0 specs, 0.5 (slider 5-6) → 2-3 specs, 1.0 (slider 10) → 5 specs
            if tech_intensity < 0.15:  # Very low (slider 1-2)
                # Conceptual only, NO technical specs
                max_props = 0
                max_settings = 0
                include_apps = False
            elif tech_intensity < 0.50:  # Low to moderate (slider 3-5)
                # Minimal specs - 1-2 key properties
                max_props = 2
                max_settings = 1
                include_apps = False
            else:  # tech_intensity >= 0.50 (slider 6-10)
                # Full technical detail
                max_props = 5
                max_settings = 3
                include_apps = True
        
        if facts.get('properties') and max_props > 0:
            lines.append("Properties:")
            for prop, value in list(facts['properties'].items())[:max_props]:
                # Phase 3A: Format value based on fact_formatting_style
                formatted_value = self._format_fact_value(value, fact_style, engagement)
                lines.append(f"  - {prop}: {formatted_value}")
        
        if facts.get('machine_settings') and max_settings > 0:
            lines.append("Laser cleaning settings:")
            for setting, value in list(facts['machine_settings'].items())[:max_settings]:
                lines.append(f"  - {setting}: {value}")
        
        if include_apps and facts.get('applications'):
            # Truncate based on context_detail_level (0.0-1.0 normalized)
            # Linear mapping: 0.0 → 100 chars, 0.5 → 200 chars, 1.0 → 300 chars
            if context_detail < 0.30:  # Low (slider 1-3)
                max_chars = 100  # Brief
            elif context_detail < 0.70:  # Moderate (slider 4-7)
                max_chars = 200  # Moderate
            else:  # context_detail >= 0.70 (slider 8-10)
                max_chars = 300  # Full
            lines.append(f"Applications: {facts['applications'][:max_chars]}")
        
        return "\n".join(lines)
    
    def _format_fact_value(self, value: str, style: str, engagement: int) -> str:
        """
        Format fact value based on style preference.
        
        Args:
            value: Original value (e.g., "2.7 g/cm³")
            style: 'formal', 'balanced', or 'conversational'
            engagement: 1-3 engagement level
            
        Returns:
            Formatted value string
        """
        if style == 'formal':
            return value
        elif style == 'balanced':
            # Add "roughly" or "approximately" for numeric values
            if any(char.isdigit() for char in value):
                return f"roughly {value}"
            return value
        else:  # conversational
            # Add "around" and contextual comment for high engagement
            if any(char.isdigit() for char in value):
                base = f"around {value}"
                # Add contextual comments for high engagement
                if engagement > 60:
                    # Add casual parenthetical based on property type
                    if 'g/cm³' in value or 'kg/m³' in value:
                        return f"{base} (pretty dense!)"
                    elif 'W/m' in value or 'thermal' in value.lower():
                        return f"{base} (good conductor)"
                    elif 'GPa' in value or 'MPa' in value:
                        return f"{base} (quite strong)"
                return base
            return value
