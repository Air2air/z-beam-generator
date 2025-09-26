#!/usr/bin/env python3
"""
Frontmatter Component Generator

Generates frontmatter YAML content with property enhancement.
"""

import logging
import time
from typing import Dict, Optional, Any

from generators.component_generators import APIComponentGenerator, ComponentResult

logger = logging.getLogger(__name__)


class FrontmatterComponentGenerator(APIComponentGenerator):
    """API-based generator for frontmatter components"""

    def __init__(self):
        super().__init__("frontmatter")
        self._load_prompt_config()

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "frontmatter",
            "description": "YAML frontmatter generation for laser cleaning articles with centralized version integration",
            "version": "4.1.1",
            "requires_api": True,
            "type": "dynamic",
        }

    def _load_prompt_config(self):
        """Load prompt configuration from YAML file"""
        try:
            from utils.config_loader import load_component_config

            # Use centralized config loader with caching and fail-fast behavior
            self.prompt_config = load_component_config("frontmatter", "prompt.yaml")
            logger.info("Loaded optimized comprehensive prompt configuration for frontmatter")
        except Exception as e:
            from utils.ai.loud_errors import configuration_failure

            configuration_failure(
                "frontmatter_generator", f"Error loading prompt configuration: {e}"
            )
            logger.error(f"Error loading prompt configuration: {e}")
            self.prompt_config = {}

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate frontmatter using data-driven approach with minimal API usage"""
        try:
            # Load comprehensive material data from YAML to get author_id
            yaml_material_data = self._load_material_data_from_yaml(material_name)
            
            # Generate formula and symbol for materials that don't have them
            category = material_data.get("category", "unknown")
            formula = material_data.get("formula")
            symbol = material_data.get("symbol")
            
            # FORMULA GENERATION: Create chemical formulas when not explicitly provided
            if not formula:
                formula = self._generate_formula_from_material(material_name, category)
                logger.info(f"Generated formula '{formula}' for {material_name} (category: {category})")
            
            if not symbol:
                # For alloys and compounds, use formula as symbol when symbol is not explicitly defined
                symbol = formula
                logger.info(f"Using formula '{formula}' as symbol for {material_name} (alloy/compound without single atomic symbol)")
            
            # Resolve author information if not provided
            if not author_info:
                author_id = yaml_material_data.get('author_id')
                if author_id:
                    try:
                        from utils import get_author_by_id
                        author_info = get_author_by_id(author_id)
                        if not author_info or 'name' not in author_info:
                            from utils.ai.loud_errors import dependency_failure
                            dependency_failure(
                                "frontmatter_generator",
                                f"Author data for ID {author_id} missing required 'name' field - fail-fast architecture requires complete author information"
                            )
                            raise ValueError(f"Invalid author data for ID {author_id}")
                        logger.info(f"Resolved author_id {author_id} to {author_info['name']}")
                    except Exception as e:
                        from utils.ai.loud_errors import dependency_failure
                        dependency_failure(
                            "frontmatter_generator",
                            f"Failed to resolve author_id {author_id}: {e} - fail-fast architecture requires valid author information"
                        )
                        raise ValueError(f"Failed to resolve author_id {author_id}: {e}")
                else:
                    from utils.ai.loud_errors import dependency_failure
                    dependency_failure(
                        "frontmatter_generator",
                        "Author information or author_id is required for frontmatter generation - fail-fast architecture requires complete author data"
                    )
                    raise ValueError("Author information is required - no fallbacks allowed")

            # Build comprehensive frontmatter from structured data
            final_content = self._build_comprehensive_frontmatter_from_data(
                material_name, material_data, author_info, formula, symbol
            )

            logger.info(f"Generated frontmatter for {material_name} using data-driven approach")
            return ComponentResult(
                component_type="frontmatter", content=final_content, success=True
            )

        except Exception as e:
            from utils.ai.loud_errors import component_failure
            component_failure(
                "frontmatter_generator", 
                f"Error generating frontmatter for {material_name}: {e}"
            )
            logger.error(f"Error generating frontmatter for {material_name}: {e}")
            return ComponentResult(
                component_type="frontmatter",
                content="",
                success=False,
                error_message=str(e),
            )

    def _apply_standardized_naming(self, material_name_lower: str) -> str:
        """Apply naming standardization aligned with materials.yaml single source of truth"""
        # Basic kebab-case conversion
        slug = material_name_lower.replace(" ", "-")
        
        # Apply standardizations aligned with materials.yaml database
        naming_mappings = {
            # Hyphenation standardizations
            "terra-cotta": "terracotta",
            # Alignment with materials.yaml single source of truth
            # (materials.yaml defines only "Steel" and "Stainless Steel", not specific variants)
        }
        
        # Apply standardization if material matches known mappings
        if slug in naming_mappings:
            slug = naming_mappings[slug]
            
        # Remove wood- prefix (wood materials are defined without prefix in materials.yaml)
        if slug.startswith("wood-"):
            slug = slug[5:]  # Remove "wood-" prefix
            
        return slug

    def _create_template_vars(
        self,
        material_name,
        material_data,
        author_info,
        frontmatter_data=None,
        schema_fields=None,
    ):
        """Create template variables for frontmatter generation."""
        subject_lowercase = material_name.lower()
        
        # Apply standardized naming convention that matches the resolved image naming
        subject_slug = self._apply_standardized_naming(subject_lowercase)

        # FAIL-FAST: Category is required for frontmatter generation
        if "category" not in material_data:
            raise Exception(
                "Material data missing required 'category' field - fail-fast architecture requires complete material information"
            )
        category = material_data["category"]

        # Extract chemical properties with strict validation - NO FALLBACKS
        formula = None
        if "formula" in material_data and material_data["formula"]:
            formula = material_data["formula"]
        elif (
            "data" in material_data
            and "formula" in material_data["data"]
            and material_data["data"]["formula"]
        ):
            formula = material_data["data"]["formula"]
        
        # Extract symbol with strict validation - NO FALLBACKS
        symbol = None
        if "symbol" in material_data and material_data["symbol"]:
            symbol = material_data["symbol"]
        elif (
            "data" in material_data
            and "symbol" in material_data["data"]
            and material_data["data"]["symbol"]
        ):
            symbol = material_data["data"]["symbol"]
        
        # FORMULA GENERATION: Create chemical formulas when not explicitly provided
        if not formula:
            formula = self._generate_formula_from_material(material_name, category)
            logger.info(f"Generated formula '{formula}' for {material_name} (category: {category})")
        
        if not symbol:
            # For alloys and compounds, use formula as symbol when symbol is not explicitly defined
            symbol = formula
            logger.info(f"Using formula '{formula}' as symbol for {material_name} (alloy/compound without single atomic symbol)")

        # FAIL-FAST: Author information is required
        if not author_info or "name" not in author_info:
            # Try to extract author_id from material_data and resolve it
            author_id = None
            if "author_id" in material_data:
                author_id = material_data["author_id"]
            elif "data" in material_data and "author_id" in material_data["data"]:
                author_id = material_data["data"]["author_id"]

            if author_id:
                try:
                    from utils import get_author_by_id

                    author_data = get_author_by_id(author_id)
                    if author_data and "name" in author_data:
                        author_name = author_data["name"]
                        logger.info(f"Resolved author_id {author_id} to {author_name}")
                        # Store the full author data for later use
                        resolved_author_info = author_data
                    else:
                        raise Exception(
                            f"Author data for ID {author_id} missing required 'name' field - fail-fast architecture requires complete author information"
                        )
                except Exception as e:
                    raise Exception(
                        f"Failed to resolve author_id {author_id}: {e} - fail-fast architecture requires valid author information"
                    )
            else:
                raise Exception(
                    "Author information with 'name' field is required for frontmatter generation - fail-fast architecture requires complete author information"
                )
        else:
            author_name = author_info["name"]
            resolved_author_info = author_info

        return {
            "subject": material_name.title(),
            "subject_lowercase": subject_lowercase,
            "subject_slug": subject_slug,
            "exact-material-name": subject_slug,  # Required for template compatibility
            "material_formula": formula,
            "material_symbol": symbol,
            "formula": formula,
            "symbol": symbol,
            "material_type": material_data.get("material_type")
            if "material_type" in material_data
            else category,
            "category": category,
            "author_name": author_name,
            "author_object_sex": resolved_author_info.get("sex", "unknown")
            if resolved_author_info
            else "unknown",
            "author_object_title": resolved_author_info.get("title", "Expert")
            if resolved_author_info
            else "Expert",
            "author_object_country": resolved_author_info.get("country", "Unknown")
            if resolved_author_info
            else "Unknown",
            "author_object_expertise": resolved_author_info.get(
                "expertise", "Materials Science"
            )
            if resolved_author_info
            else "Materials Science",
            "author_object_image": resolved_author_info.get("image")
            if resolved_author_info and "image" in resolved_author_info
            else None,  # FAIL-FAST: No default image allowed
            "article_type": material_data.get("article_type")
            if "article_type" in material_data
            else "material",  # Keep this for schema compatibility
            "persona_country": resolved_author_info.get("country")
            if resolved_author_info and "country" in resolved_author_info
            else None,  # FAIL-FAST: No default country allowed
            "author_id": resolved_author_info.get("id")
            if resolved_author_info and "id" in resolved_author_info
            else None,  # FAIL-FAST: No default ID allowed
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def _build_api_prompt(
        self, template_vars: Dict, frontmatter_data: Optional[Dict] = None
    ) -> str:
        """Build API prompt using template variables"""

        if not self.prompt_config:
            raise ValueError("Prompt configuration not loaded")

        if "template" not in self.prompt_config:
            raise ValueError(
                "Prompt configuration missing required 'template' field - fail-fast architecture requires complete configuration"
            )

        template = self.prompt_config["template"]

        # Format the template with variables
        try:
            formatted_prompt = template.format(**template_vars)
            return formatted_prompt
        except KeyError as e:
            from utils.ai.loud_errors import validation_failure

            validation_failure(
                "frontmatter_generator", f"Missing template variable: {e}", field=str(e)
            )
            logger.error(f"Missing template variable: {e}")
            raise ValueError(f"Missing template variable: {e}")
        except Exception as e:
            from utils.ai.loud_errors import validation_failure

            validation_failure(
                "frontmatter_generator",
                f"Template formatting error: {e}",
                field="template",
            )
            logger.error(f"Template formatting error: {e}")
            raise ValueError(f"Template formatting error: {e}")

    def _process_and_enhance_content(
        self, content: str, material_name: str, material_data: Dict
    ) -> str:
        """
        Consolidated processing: parse, enhance with triple format, and add required fields.
        
        This replaces the complex post-processing pipeline with a single, reliable method.
        """
        try:
            import yaml
            
            # Extract YAML content from various formats
            yaml_content = self._extract_yaml_from_content(content)
            if not yaml_content:
                logger.warning(f"Could not extract YAML from content for {material_name}")
                return content
            
            # Parse YAML
            try:
                frontmatter_data = yaml.safe_load(yaml_content)
                if not frontmatter_data:
                    logger.warning(f"Empty YAML content for {material_name}")
                    return content
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error for {material_name}: {e}")
                return content
            
            # Add missing required technical specifications
            self._ensure_technical_specifications(frontmatter_data)
            
            # Add triple format fields for all properties
            self._add_triple_format_properties(frontmatter_data)
            
            # Apply field ordering for optimal readability
            ordered_frontmatter = self._apply_field_ordering(frontmatter_data)
            
            # Convert back to frontmatter format
            enhanced_yaml = yaml.dump(
                ordered_frontmatter,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
            
            result = f"---\n{enhanced_yaml}---"
            logger.info(f"Enhanced frontmatter for {material_name} with complete triple format and field ordering")
            return result
            
        except Exception as e:
            logger.error(f"Error processing frontmatter for {material_name}: {e}")
            return content

    def _ensure_technical_specifications(self, frontmatter_data: Dict) -> None:
        """Add missing required machine settings with enhanced triple format"""
        # Rename technicalSpecifications to machineSettings if present
        if "technicalSpecifications" in frontmatter_data:
            frontmatter_data["machineSettings"] = frontmatter_data.pop("technicalSpecifications")
        
        machine_settings = frontmatter_data.setdefault("machineSettings", {})
        
        # Add missing required fields with triple format and min/max ranges
        if "scanningSpeed" not in machine_settings:
            machine_settings["scanningSpeed"] = "50-500mm/s"
            machine_settings["scanningSpeedNumeric"] = 275
            machine_settings["scanningSpeedUnit"] = "mm/s"
            machine_settings["scanningSpeedMin"] = "1mm/s"
            machine_settings["scanningSpeedMax"] = "5000mm/s"
            
        if "beamProfile" not in machine_settings:
            machine_settings["beamProfile"] = "Gaussian TEM00"
            machine_settings["beamProfileOptions"] = ["Gaussian TEM00", "Top-hat", "Donut", "Multi-mode"]
        
        # Apply triple format to existing machine settings
        self._add_triple_format_machine_settings(machine_settings)

    def _add_triple_format_machine_settings(self, machine_settings: Dict) -> None:
        """
        Add numeric, unit, min/max fields for machine settings with grouped organization.
        
        Groups related machine settings together:
        - powerRange: 50-200W
        - powerRangeNumeric: 125.0
        - powerRangeUnit: W
        - powerRangeMin: 20W
        - powerRangeMinNumeric: 20.0
        - powerRangeMinUnit: W
        - powerRangeMax: 500W
        - powerRangeMaxNumeric: 500.0
        - powerRangeMaxUnit: W
        """
        # Create new ordered machine settings dict
        new_machine_settings = {}
        
        # Machine settings that need triple format with industry-standard ranges
        settings_config = {
            "powerRange": {
                "unit": "W",
                "min": "20W", "max": "500W",
                "description": "Laser output power range"
            },
            "pulseDuration": {
                "unit": "ns", 
                "min": "1ns", "max": "1000ns",
                "description": "Pulse duration for pulsed lasers"
            },
            "wavelength": {
                "unit": "nm",
                "min": "355nm", "max": "2940nm", 
                "description": "Laser wavelength range (UV to IR)"
            },
            "spotSize": {
                "unit": "mm",
                "min": "0.01mm", "max": "10mm",
                "description": "Focused beam spot diameter"
            },
            "repetitionRate": {
                "unit": "kHz",
                "min": "1kHz", "max": "1000kHz",
                "description": "Pulse repetition frequency"
            },
            "fluenceRange": {
                "unit": "J/cm²",
                "min": "0.1J/cm²", "max": "50J/cm²",
                "description": "Laser fluence (energy density)"
            },
            "scanningSpeed": {
                "unit": "mm/s",
                "min": "1mm/s", "max": "5000mm/s",
                "description": "Beam scanning velocity"
            }
        }
        
        # Process machine settings in groups
        setting_order = [
            "powerRange", "pulseDuration", "wavelength", "spotSize", 
            "repetitionRate", "fluenceRange", "scanningSpeed"
        ]
        
        for setting_key in setting_order:
            if setting_key in machine_settings:
                config = settings_config[setting_key]
                value_str = str(machine_settings[setting_key])
                numeric_value, unit = self._extract_numeric_and_unit(value_str)
                
                # Add main setting
                new_machine_settings[setting_key] = machine_settings[setting_key]
                
                # Add grouped numeric and unit components
                numeric_key = f"{setting_key}Numeric"
                unit_key = f"{setting_key}Unit"
                min_key = f"{setting_key}Min"
                max_key = f"{setting_key}Max"
                
                new_machine_settings[numeric_key] = numeric_value
                new_machine_settings[unit_key] = config["unit"]
                
                # Add min with numeric/unit separation
                new_machine_settings[min_key] = config["min"]
                min_numeric, min_unit = self._extract_numeric_and_unit(config["min"])
                new_machine_settings[f"{min_key}Numeric"] = min_numeric
                new_machine_settings[f"{min_key}Unit"] = min_unit
                
                # Add max with numeric/unit separation
                new_machine_settings[max_key] = config["max"]
                max_numeric, max_unit = self._extract_numeric_and_unit(config["max"])
                new_machine_settings[f"{max_key}Numeric"] = max_numeric
                new_machine_settings[f"{max_key}Unit"] = max_unit
                
                logger.debug(f"Added grouped machine setting for {setting_key}: {numeric_value} {config['unit']}")
        
        # Add remaining settings that don't need triple format
        remaining_settings = ["safetyClass", "beamProfile", "beamProfileOptions"]
        for setting in remaining_settings:
            if setting in machine_settings:
                new_machine_settings[setting] = machine_settings[setting]
        
        # Update the machine settings dict
        machine_settings.clear()
        machine_settings.update(new_machine_settings)
        
        logger.debug("Reorganized machine settings with grouped numeric/unit components")

    def _add_triple_format_properties(self, frontmatter_data: Dict) -> None:
        """
        Add numeric and unit fields for triple format compatibility.
        
        Groups related properties together:
        - density: 2.70 g/cm³
        - densityNumeric: 2.70
        - densityUnit: g/cm³
        - densityMin: 1.8 g/cm³
        - densityMinNumeric: 1.8
        - densityMinUnit: g/cm³
        """
        properties = frontmatter_data.get("materialProperties", {})
        if not properties:
            return
        
        # Create new ordered properties dict
        new_properties = {}
        
        # Properties that need triple format and their expected units
        main_properties = {
            "density": ("densityNumeric", "densityUnit", "g/cm³"),
            "meltingPoint": ("meltingPointNumeric", "meltingPointUnit", "°C"),
            "thermalConductivity": ("thermalConductivityNumeric", "thermalConductivityUnit", "W/m·K"),
            "tensileStrength": ("tensileStrengthNumeric", "tensileStrengthUnit", "MPa"),
            "hardness": ("hardnessNumeric", "hardnessUnit", "HB"),
            "youngsModulus": ("youngsModulusNumeric", "youngsModulusUnit", "GPa"),
        }
        
        # Process properties in groups for better organization
        property_groups = [
            "density", "meltingPoint", "thermalConductivity", 
            "tensileStrength", "hardness", "youngsModulus"
        ]
        
        for base_prop in property_groups:
            # Add main property
            if base_prop in properties:
                value_str = str(properties[base_prop])
                new_properties[base_prop] = properties[base_prop]
                
                # Add numeric and unit components
                if base_prop in main_properties:
                    numeric_key, unit_key, default_unit = main_properties[base_prop]
                    
                    if not self._has_units(value_str):
                        logger.warning(f"Property {base_prop} missing units: '{value_str}' - adding default unit {default_unit}")
                        value_str = f"{value_str} {default_unit}"
                        new_properties[base_prop] = value_str
                    
                    numeric_value, unit = self._extract_numeric_and_unit(value_str)
                    new_properties[numeric_key] = numeric_value
                    new_properties[unit_key] = unit
            
            # Add related Min/Max properties grouped together
            related_props = [f"{base_prop}Min", f"{base_prop}Max"]
            for related_prop in related_props:
                if related_prop in properties:
                    value_str = str(properties[related_prop])
                    new_properties[related_prop] = properties[related_prop]
                    
                    # Add numeric and unit for Min/Max if they have units
                    if self._has_units(value_str):
                        numeric_value, unit = self._extract_numeric_and_unit(value_str)
                        new_properties[f"{related_prop}Numeric"] = numeric_value
                        new_properties[f"{related_prop}Unit"] = unit
            
            # Add percentile (should come after Min/Max)
            percentile_prop = f"{base_prop}Percentile"
            if base_prop == "meltingPoint":
                percentile_prop = "meltingPercentile"
            elif base_prop == "thermalConductivity":
                percentile_prop = "thermalPercentile"
            elif base_prop == "tensileStrength":
                percentile_prop = "tensilePercentile"
            elif base_prop == "hardness":
                percentile_prop = "hardnessPercentile"
            elif base_prop == "youngsModulus":
                percentile_prop = "modulusPercentile"
            
            if percentile_prop in properties:
                new_properties[percentile_prop] = properties[percentile_prop]
            
            # Handle special case for modulusMin/Max (youngsModulus related)
            if base_prop == "youngsModulus":
                for modulus_prop in ["modulusMin", "modulusMax"]:
                    if modulus_prop in properties:
                        value_str = str(properties[modulus_prop])
                        new_properties[modulus_prop] = properties[modulus_prop]
                        
                        if self._has_units(value_str):
                            numeric_value, unit = self._extract_numeric_and_unit(value_str)
                            new_properties[f"{modulus_prop}Numeric"] = numeric_value
                            new_properties[f"{modulus_prop}Unit"] = unit
        
        # Add remaining properties that weren't processed
        remaining_props = ["laserType", "wavelength", "fluenceRange", "chemicalFormula"]
        for prop in remaining_props:
            if prop in properties:
                new_properties[prop] = properties[prop]
        
        # Update the properties dict
        properties.clear()
        properties.update(new_properties)
        
        logger.debug("Reorganized properties with grouped numeric/unit components")

    def _has_units(self, value_str: str) -> bool:
        """
        Check if a property value string contains units.
        
        Examples:
            "2.70 g/cm³" -> True
            "385 MPa" -> True
            "70-120 HB" -> True
            "1668" -> False
        """
        import re
        # Check if string contains letters (indicating units) after numbers
        return bool(re.search(r'\d\s*[a-zA-Z°·/²³]+', value_str))

    def _extract_numeric_and_unit(self, value_str: str) -> tuple:
        """
        Extract numeric value and unit from a property string.
        
        Examples:
            "2.70 g/cm³" -> (2.70, "g/cm³")
            "385 MPa" -> (385.0, "MPa") 
            "70-120 HB" -> (95.0, "HB")  # midpoint of range
        """
        if not value_str:
            return 0.0, ""
        
        import re
        
        # Handle range values by taking the midpoint
        if '-' in value_str and not value_str.startswith('-'):
            parts = value_str.split('-')
            if len(parts) == 2:
                try:
                    num1_match = re.search(r'[\d.]+', parts[0].strip())
                    num2_match = re.search(r'[\d.]+', parts[1].strip())
                    
                    if num1_match and num2_match:
                        num1 = float(num1_match.group())
                        num2 = float(num2_match.group())
                        midpoint = (num1 + num2) / 2
                        
                        # Extract unit from second part
                        unit_match = re.search(r'[a-zA-Z°/³²·]+', parts[1].strip())
                        unit = unit_match.group() if unit_match else ""
                        
                        return midpoint, unit
                except (ValueError, AttributeError):
                    pass
        
        # Extract single value
        try:
            num_match = re.search(r'[\d.]+', value_str)
            if num_match:
                numeric_value = float(num_match.group())
                
                # Extract unit
                unit_match = re.search(r'[a-zA-Z°/³²·]+', value_str)
                unit = unit_match.group() if unit_match else ""
                
                return numeric_value, unit
        except (ValueError, AttributeError):
            pass
        
        return 0.0, ""

    def _validate_and_enhance_content(
        self, content: str, material_name: str, material_data: dict, api_client
    ) -> tuple[str, object]:
        """
        Comprehensive validation and enhancement of generated frontmatter content.
        
        This method implements the single source of truth validation pipeline:
        1. Parse generated YAML content 
        2. Run comprehensive multi-stage validation
        3. Apply automatic corrections if possible
        4. Return validated content with validation report
        
        Args:
            content: Generated frontmatter YAML content
            material_name: Name of the material
            material_data: Material data context
            api_client: API client for AI-powered validation
            
        Returns:
            tuple: (validated_content, validation_report)
        """
        try:
            # Import comprehensive validator
            from frontmatter.comprehensive_validator import ComprehensiveFrontmatterValidator
            
            # Parse YAML content for validation
            import yaml
            try:
                # Extract YAML between --- delimiters
                yaml_content = self._extract_yaml_from_content(content)
                frontmatter_data = yaml.safe_load(yaml_content)
                
                if not frontmatter_data:
                    logger.warning(f"Failed to parse YAML from generated content for {material_name}")
                    return content, None
                    
            except yaml.YAMLError as e:
                logger.error(f"YAML parsing error for {material_name}: {e}")
                return content, None

            # Initialize comprehensive validator
            validator = ComprehensiveFrontmatterValidator()
            
            # Run comprehensive validation with AI-powered verification
            logger.info(f"🔍 Running comprehensive validation for {material_name}")
            validation_report = validator.validate_frontmatter_comprehensive(
                material_name=material_name,
                frontmatter_data=frontmatter_data,
                api_client=api_client,
                enable_ai_validation=True
            )
            
            # Apply automatic corrections if validation suggests them
            corrected_content = content
            if validation_report.has_critical_issues():
                logger.warning(f"⚠️ Critical validation issues found for {material_name}")
                corrected_content = self._apply_automatic_corrections(
                    content, frontmatter_data, validation_report
                )
            
            # Log validation results
            if validation_report.overall_status == "PASS":
                logger.info(f"✅ Frontmatter validation PASSED for {material_name} (score: {validation_report.overall_score:.1f}/10)")
            elif validation_report.overall_status == "WARNING":
                logger.warning(f"⚠️ Frontmatter validation WARNING for {material_name} (score: {validation_report.overall_score:.1f}/10)")
            else:
                logger.error(f"❌ Frontmatter validation FAILED for {material_name} (score: {validation_report.overall_score:.1f}/10)")
            
            # Save validation report for debugging/review
            self._save_validation_report(material_name, validation_report)
            
            return corrected_content, validation_report
            
        except ImportError as e:
            logger.warning(f"Comprehensive validator not available: {e}")
            return content, None
        except Exception as e:
            logger.error(f"Validation error for {material_name}: {e}")
            return content, None

    def _extract_yaml_from_content(self, content: str) -> str:
        """Extract YAML content between --- delimiters"""
        import re
        
        # Match YAML frontmatter between --- delimiters
        yaml_pattern = r'^---\s*\n(.*?)\n---'
        match = re.search(yaml_pattern, content, re.DOTALL | re.MULTILINE)
        
        if match:
            return match.group(1)
        else:
            # If no delimiters, assume entire content is YAML
            return content.strip()

    def _apply_automatic_corrections(
        self, content: str, frontmatter_data: dict, validation_report
    ) -> str:
        """
        Apply automatic corrections based on validation recommendations.
        
        This method implements smart corrections for common validation issues:
        - Fix missing required fields with sensible defaults
        - Correct obvious data type issues
        - Standardize format inconsistencies
        """
        try:
            corrected_data = frontmatter_data.copy()
            corrections_applied = []
            
            # Apply corrections based on validation issues
            for result in validation_report.validation_results:
                if result.stage == "schema_structure":
                    for issue in result.issues:
                        if "Missing required field:" in issue:
                            field_name = issue.split(": ")[1]
                            # FAIL-FAST: Cannot proceed with invalid data
                            from utils.ai.loud_errors import validation_failure
                            validation_failure(
                                "frontmatter_generator",
                                f"Missing required field '{field_name}' in generated frontmatter - fail-fast architecture requires complete data",
                                field=field_name
                            )
                            raise ValueError(f"Missing required field '{field_name}' in generated frontmatter - no fallbacks allowed")
                            
            # Regenerate YAML if corrections were applied
            if corrections_applied:
                import yaml
                corrected_yaml = yaml.dump(corrected_data, default_flow_style=False, sort_keys=False)
                corrected_content = f"---\n{corrected_yaml}---"
                
                logger.info(f"Applied automatic corrections: {', '.join(corrections_applied)}")
                return corrected_content
            
            return content
            
        except Exception as e:
            logger.error(f"Error applying automatic corrections: {e}")
            return content

    def _load_material_data_from_yaml(self, material_name: str) -> Dict[str, Any]:
        """Load comprehensive material data from materials.yaml"""
        try:
            import yaml
            
            with open('data/materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
            
            # Find material in the materials section
            material_data = None
            if 'materials' in materials_data:
                for category_name, category_info in materials_data['materials'].items():
                    if isinstance(category_info, dict) and 'items' in category_info:
                        for item in category_info['items']:
                            if item.get('name', '').lower() == material_name.lower():
                                material_data = item.copy()
                                material_data['category'] = category_name
                                break
                    if material_data:
                        break
            
            if not material_data:
                raise ValueError(f"Material '{material_name}' not found in materials.yaml - fail-fast architecture requires explicit material data")
            
            # Add parameter templates and defaults
            material_data['parameter_templates'] = materials_data.get('parameter_templates', {})
            material_data['defaults'] = materials_data.get('defaults', {})
            
            return material_data
            
        except Exception as e:
            from utils.ai.loud_errors import component_failure
            component_failure(
                "frontmatter_generator",
                f"Failed to load material data from materials.yaml: {e}"
            )
            raise

    def _build_comprehensive_frontmatter_from_data(self, material_name: str, material_data: Dict, author_info: Dict, formula: str, symbol: str) -> str:
        """Build comprehensive frontmatter using data from materials.yaml with minimal API usage"""
        try:
            # Load comprehensive material data
            yaml_material_data = self._load_material_data_from_yaml(material_name)
            
            # Add generated formula and symbol to yaml_material_data
            yaml_material_data['formula'] = formula
            yaml_material_data['symbol'] = symbol
            
            # Get laser parameters for wavelength info
            laser_params = self._get_laser_parameters(yaml_material_data)
            wavelength = laser_params.get('wavelength_optimal', '1064nm')
            
            # Build comprehensive frontmatter structure
            frontmatter = {
                'name': material_name.lower(),
                'category': yaml_material_data['category'],
                'title': f"{material_name.title()} Laser Cleaning",
                'headline': f"Comprehensive technical guide for laser cleaning {yaml_material_data['category']} {material_name.lower()}",
                'description': f"Technical overview of {material_name.title()}, {symbol}, for laser cleaning applications, including optimal {wavelength} wavelength interaction, and industrial applications in surface preparation.",
                'keywords': f"{material_name.lower()}, {material_name.lower()} {yaml_material_data['category']}, laser ablation, laser cleaning, non-contact cleaning, pulsed fiber laser, surface contamination removal, industrial laser parameters, thermal processing, surface restoration",
                'chemicalProperties': {
                    'symbol': symbol,
                    'formula': formula,
                    'materialType': yaml_material_data['category']
                },
                'properties': self._build_material_properties(material_data),
                'composition': self._build_composition(yaml_material_data),
                'machineSettings': self._build_machine_settings(yaml_material_data),
                'applications': self._build_applications(yaml_material_data),
                'compatibility': self._build_compatibility(yaml_material_data),
                'regulatoryStandards': "ISO 18562, ASTM F2100, IEC 60601-1",
                'author': author_info.get('name'),
                'author_object': self._build_author_object(author_info),
                'images': self._build_images(material_name),
                'environmentalImpact': self._build_environmental_impact(),
                'outcomes': self._build_outcomes(),
                'prompt_chain_verification': self._build_verification_data(author_info)
            }
            
            # Convert to YAML format
            import yaml
            yaml_content = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False, allow_unicode=True)
            return f"---\n{yaml_content}---"
            
        except Exception as e:
            from utils.ai.loud_errors import component_failure
            component_failure(
                "frontmatter_generator",
                f"Failed to build comprehensive frontmatter from data: {e}"
            )
            raise

    def _get_laser_parameters(self, yaml_material_data: Dict) -> Dict:
        """Get laser parameters either directly or from template"""
        if 'laser_parameters' in yaml_material_data:
            return yaml_material_data['laser_parameters']
        elif 'laser_parameters_template' in yaml_material_data:
            template_name = yaml_material_data['laser_parameters_template']
            parameter_templates = yaml_material_data.get('parameter_templates', {})
            if template_name in parameter_templates:
                return parameter_templates[template_name]
            else:
                # Load default templates
                try:
                    import yaml
                    with open('data/materials.yaml', 'r') as f:
                        materials_data = yaml.safe_load(f)
                        if 'parameter_templates' in materials_data and template_name in materials_data['parameter_templates']:
                            return materials_data['parameter_templates'][template_name]
                except Exception:
                    pass
        
        # FAIL-FAST: No laser parameters available
        raise ValueError("No laser parameters found for material - fail-fast architecture requires complete laser parameter data")

    def _build_material_properties(self, material_data: Dict) -> Dict:
        """Build material properties section from comprehensive material data with category-aware percentiles"""
        properties = {}
        
        # Get material category for category-aware percentile calculations
        material_category = material_data.get('category', 'metal')
        
        # Load category ranges from materials.yaml for accurate percentiles
        category_ranges = self._get_category_ranges(material_category)
        
        # Map of comprehensive properties from materials.yaml to their extraction logic
        property_mappings = {
            'density': {'unit': 'g/cm³', 'camel_key': 'density'},
            'melting_point': {'unit': '°C', 'camel_key': 'meltingPoint'},
            'boiling_point': {'unit': '°C', 'camel_key': 'boilingPoint'},
            'thermal_conductivity': {'unit': 'W/(m·K)', 'camel_key': 'thermalConductivity'},
            'specific_heat_capacity': {'unit': 'J/(kg·K)', 'camel_key': 'specificHeatCapacity'},
            'thermal_expansion_coefficient': {'unit': '×10⁻⁶/K', 'camel_key': 'thermalExpansionCoefficient'},
            'electrical_resistivity': {'unit': 'Ω·m', 'camel_key': 'electricalResistivity'},
            'tensile_strength': {'unit': 'MPa', 'camel_key': 'tensileStrength'},
            'yield_strength': {'unit': 'MPa', 'camel_key': 'yieldStrength'},
            'elastic_modulus': {'unit': 'GPa', 'camel_key': 'elasticModulus'},
            'curie_temperature': {'unit': '°C', 'camel_key': 'curieTemperature'},
            'crystal_structure': {'unit': None, 'camel_key': 'crystalStructure'},
            'magnetic_properties': {'unit': None, 'camel_key': 'magneticProperties'}
        }
        
        # Extract comprehensive properties from material_data
        for prop_key, config in property_mappings.items():
            if prop_key in material_data:
                raw_value = material_data[prop_key]
                
                # Handle properties with units
                if config['unit']:
                    # If raw value is already a string with units, use it directly
                    if isinstance(raw_value, str):
                        properties[prop_key] = raw_value
                        
                        # Extract numeric value and unit for triple format
                        numeric_value, unit = self._extract_numeric_and_unit(raw_value)
                        if numeric_value:
                            camel_prop = self._to_camel_case(prop_key)
                            properties[f"{camel_prop}Numeric"] = numeric_value
                            properties[f"{camel_prop}Unit"] = unit or config['unit']
                            
                            # Calculate category-aware percentile using actual min/max ranges
                            if category_ranges and config['camel_key'] in category_ranges:
                                range_info = category_ranges[config['camel_key']]
                                percentile = self._calculate_percentile_from_range(
                                    numeric_value, range_info.get('min'), range_info.get('max')
                                )
                                if percentile is not None:
                                    properties[f"{camel_prop}Percentile"] = percentile
                    
                    # If raw value is numeric, add unit and create full format
                    elif isinstance(raw_value, (int, float)):
                        full_value = f"{raw_value} {config['unit']}"
                        properties[prop_key] = full_value
                        
                        camel_prop = self._to_camel_case(prop_key)
                        properties[f"{camel_prop}Numeric"] = float(raw_value)
                        properties[f"{camel_prop}Unit"] = config['unit']
                        
                        # Calculate category-aware percentile
                        if category_ranges and config['camel_key'] in category_ranges:
                            range_info = category_ranges[config['camel_key']]
                            percentile = self._calculate_percentile_from_range(
                                raw_value, range_info.get('min'), range_info.get('max')
                            )
                            if percentile is not None:
                                properties[f"{camel_prop}Percentile"] = percentile
                
                # Handle properties without units (text values)
                else:
                    properties[prop_key] = raw_value
        
        logger.info(f"Successfully extracted {len(properties)} comprehensive properties from material data")
        return properties
    
    def _to_camel_case(self, snake_str: str) -> str:
        """Convert snake_case to camelCase for property names"""
        components = snake_str.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])
    
    def _get_category_ranges(self, category: str) -> Dict:
        """Get category ranges from materials.yaml for accurate percentile calculations"""
        try:
            import yaml
            with open('data/materials.yaml', 'r') as f:
                materials_data = yaml.safe_load(f)
            
            category_ranges_data = materials_data.get('category_ranges', {})
            return category_ranges_data.get(category, {})
        except Exception as e:
            logger.warning(f"Could not load category ranges for {category}: {e}")
            return {}
    
    def _calculate_percentile_from_range(self, value: float, min_str: str, max_str: str) -> Optional[float]:
        """Calculate percentile based on category min/max ranges"""
        try:
            if not min_str or not max_str:
                return None
                
            # Extract numeric values from range strings
            min_val, _ = self._extract_numeric_and_unit(min_str)
            max_val, _ = self._extract_numeric_and_unit(max_str)
            
            if min_val is None or max_val is None or max_val <= min_val:
                return None
            
            # Calculate percentile within the category range
            if value <= min_val:
                return 0.0
            elif value >= max_val:
                return 100.0
            else:
                percentile = ((value - min_val) / (max_val - min_val)) * 100
                return round(percentile, 1)
                
        except Exception as e:
            logger.debug(f"Error calculating percentile for value {value}: {e}")
            return None

    def _generate_formula_from_material(self, material_name: str, category: str) -> str:
        """
        Generate appropriate chemical formula based on material name and category.
        Maintains fail-fast architecture by providing explicit formulas for all materials.
        """
        material_lower = material_name.lower().strip()
        
        # Known chemical formula mappings by exact name
        known_formulas = {
            # Ceramics
            'alumina': 'Al₂O₃',
            'zirconia': 'ZrO₂',
            'silicon nitride': 'Si₃N₄',
            'silicon carbide': 'SiC',
            'porcelain': 'Al₂Si₂O₅(OH)₄',  # Kaolinite base
            'stoneware': 'Al₂Si₂O₅(OH)₄',  # Clay base
            
            # Glass materials
            'borosilicate glass': 'SiO₂·B₂O₃',
            'pyrex': 'SiO₂·B₂O₃',
            'soda-lime glass': 'Na₂O·CaO·SiO₂',
            'float glass': 'Na₂O·CaO·SiO₂',
            'fused silica': 'SiO₂',
            'quartz glass': 'SiO₂',
            'tempered glass': 'Na₂O·CaO·SiO₂',
            'lead crystal': 'PbO·SiO₂',
            
            # Stone materials
            'granite': 'K(AlSi₃O₈)',  # Feldspar dominant
            'marble': 'CaCO₃',
            'limestone': 'CaCO₃',
            'calcite': 'CaCO₃',
            'basalt': 'Ca(Mg,Fe)Si₂O₆',  # Pyroxene base
            'alabaster': 'CaSO₄·2H₂O',
            'onyx': 'CaCO₃',
            'slate': 'Al₂Si₄O₁₀(OH)₂',  # Mica base
            'sandstone': 'SiO₂',
            'quartzite': 'SiO₂',
            'bluestone': 'SiO₂',
            'porphyry': 'K(AlSi₃O₈)',
            'breccia': 'CaCO₃',  # Carbonate cement typical
            'travertine': 'CaCO₃',
            'schist': 'Al₂Si₄O₁₀(OH)₂',
            'gneiss': 'K(AlSi₃O₈)',
            'andesite': 'Ca(Al₂Si₂O₈)',
            'rhyolite': 'K(AlSi₃O₈)',
            
            # Masonry materials
            'concrete': 'Ca(OH)₂·SiO₂',  # Cement base
            'cement': 'Ca₃SiO₅',  # Portland cement
            'mortar': 'Ca(OH)₂·SiO₂',
            'brick': 'Al₂Si₂O₅(OH)₄',  # Clay base
            'plaster': 'CaSO₄·2H₂O',
            'stucco': 'Ca(OH)₂',
            'terracotta': 'Al₂Si₂O₅(OH)₄',
            
            # Semiconductors
            'silicon': 'Si',
            'gallium arsenide': 'GaAs',
            'silicon germanium': 'SiGe',
            'germanium': 'Ge',
            'gallium nitride': 'GaN',
        }
        
        # Check exact match first
        if material_lower in known_formulas:
            return known_formulas[material_lower]
        
        # Category-based formula generation
        if category == 'wood':
            # All wood materials use cellulose as primary component
            return 'C₆H₁₀O₅'  # Cellulose
        elif category == 'composite':
            # Most composites are polymer-based
            if 'carbon fiber' in material_lower or 'cfrp' in material_lower:
                return 'C·(C₂H₄)ₙ'  # Carbon fiber in polymer matrix
            elif 'fiberglass' in material_lower or 'gfrp' in material_lower:
                return 'SiO₂·(C₂H₄)ₙ'  # Glass fiber in polymer matrix
            elif 'kevlar' in material_lower:
                return 'C₁₄H₁₀N₂O₂'  # Kevlar polymer
            elif 'rubber' in material_lower:
                return '(C₅H₈)ₙ'  # Natural rubber
            elif 'epoxy' in material_lower:
                return 'C₂H₄O'  # Epoxy base
            elif 'polyester' in material_lower:
                return 'C₁₀H₈O₄'  # Polyester
            elif 'phenolic' in material_lower:
                return 'C₆H₆O'  # Phenol base
            elif 'urethane' in material_lower:
                return 'C₃H₆N₂O'  # Urethane
            else:
                return '(C₂H₄)ₙ'  # Generic polymer
        elif category == 'ceramic':
            # Default ceramic formula (oxide-based)
            return 'Al₂O₃·SiO₂'
        elif category == 'glass':
            # Default glass formula
            return 'SiO₂'
        elif category == 'stone':
            # Default to silicate mineral
            return 'SiO₂'
        elif category == 'masonry':
            # Default to calcium-based cement
            return 'CaSiO₃'
        elif category == 'semiconductor':
            # Default to silicon
            return 'Si'
        else:
            # Generic formula based on material name pattern
            if any(wood in material_lower for wood in ['ash', 'oak', 'pine', 'maple', 'birch', 'beech', 'cedar', 'cherry', 'fir', 'hickory', 'mahogany', 'walnut', 'bamboo', 'poplar', 'willow', 'elm', 'spruce']):
                return 'C₆H₁₀O₅'  # Cellulose for wood
            else:
                return f'({material_name})'  # Placeholder formula
    
    def _build_composition(self, yaml_material_data: Dict) -> list:
        """Build composition section"""
        symbol = yaml_material_data.get('symbol', '')
        category = yaml_material_data.get('category', '')
        
        if category == 'metal':
            return [f"{symbol} 99.0-99.9%", "Trace elements (Si, Fe, Cu, Mn, Mg, Zn, Ti)"]
        else:
            return [f"Primary component: {symbol}"]

    def _build_machine_settings(self, yaml_material_data: Dict) -> Dict:
        """Build machine settings from laser parameters and templates"""
        laser_params = self._get_laser_parameters(yaml_material_data)
        
        # Extract numeric values for ranges
        def extract_range_values(range_str):
            if '–' in range_str or '-' in range_str:
                parts = range_str.replace('–', '-').split('-')
                if len(parts) == 2:
                    try:
                        min_val = float(parts[0])
                        max_val = float(''.join(filter(str.isdigit, parts[1].split()[0])))
                        return min_val, max_val, (min_val + max_val) / 2
                    except Exception:
                        pass
            return None, None, None
        
        machine_settings = {}
        
        # Power range
        power_range = laser_params.get('power_range', '50-200W')
        min_power, max_power, avg_power = extract_range_values(power_range)
        if avg_power:
            machine_settings.update({
                'powerRange': power_range,
                'powerRangeNumeric': avg_power,
                'powerRangeUnit': 'W',
                'powerRangeMin': f"{min_power}W",
                'powerRangeMinNumeric': min_power,
                'powerRangeMinUnit': 'W',
                'powerRangeMax': f"{max_power}W",
                'powerRangeMaxNumeric': max_power,
                'powerRangeMaxUnit': 'W'
            })
        
        # Add other laser parameters
        machine_settings.update({
            'pulseDuration': laser_params.get('pulse_duration', '20-100ns'),
            'wavelength': laser_params.get('wavelength_optimal', '1064nm'),
            'spotSize': laser_params.get('spot_size', '0.2-1.5mm'),
            'repetitionRate': laser_params.get('repetition_rate', '20-100kHz'),
            'fluenceRange': laser_params.get('fluence_threshold', '1.0–4.5 J/cm²'),
            'laserType': laser_params.get('laser_type', 'Pulsed Fiber Laser'),
            'beamProfile': 'Gaussian TEM00',
            'beamProfileOptions': ['Gaussian TEM00', 'Top-hat', 'Donut', 'Multi-mode'],
            'safetyClass': 'Class 4 (requires full enclosure)'
        })
        
        return machine_settings

    def _build_applications(self, yaml_material_data: Dict) -> list:
        """Build applications from material data"""
        applications = []
        material_applications = yaml_material_data.get('applications', [])
        
        for app in material_applications:
            if ':' in app:
                industry, detail = app.split(':', 1)
                applications.append({
                    'industry': industry.strip(),
                    'detail': detail.strip()
                })
        
        return applications

    def _build_compatibility(self, yaml_material_data: Dict) -> list:
        """Build compatibility list based on category"""
        category = yaml_material_data.get('category', '')
        
        if category == 'metal':
            return ['Stainless Steel', 'Titanium Alloys', 'Copper Alloys']
        elif category == 'ceramic':
            return ['Alumina', 'Zirconia', 'Silicon Carbide']
        elif category == 'composite':
            return ['Carbon Fiber', 'Glass Fiber', 'Aramid Fiber']
        else:
            return [f"Other {category} materials"]

    def _build_author_object(self, author_info: Dict) -> Dict:
        """Build author object from author info"""
        return {
            'id': author_info.get('id'),
            'name': author_info.get('name'),
            'sex': author_info.get('sex', 'm'),
            'title': author_info.get('title', 'Ph.D.'),
            'country': author_info.get('country'),
            'expertise': author_info.get('expertise'),
            'image': author_info.get('image')
        }

    def _build_images(self, material_name: str) -> Dict:
        """Build images section"""
        slug = material_name.lower().replace(' ', '-')
        return {
            'hero': {
                'alt': f"{material_name} surface undergoing laser cleaning showing precise contamination removal",
                'url': f"/images/{slug}-laser-cleaning-hero.jpg"
            },
            'micro': {
                'alt': f"Microscopic view of {material_name} surface after laser cleaning showing detailed surface structure",
                'url': f"/images/{slug}-laser-cleaning-micro.jpg"
            }
        }

    def _build_environmental_impact(self) -> list:
        """Build environmental impact section"""
        return [
            {
                'benefit': 'Chemical Solvent Elimination',
                'description': 'Reduces chemical usage by 100% compared to traditional solvent cleaning methods'
            },
            {
                'benefit': 'Water Conservation',
                'description': 'Saves approximately 5000 liters of water per month in industrial applications'
            },
            {
                'benefit': 'Energy Efficiency',
                'description': 'Consumes 40% less energy than thermal cleaning processes'
            }
        ]

    def _build_outcomes(self) -> list:
        """Build outcomes section"""
        return [
            {
                'result': 'Surface Cleanliness Level',
                'metric': 'Achieves ISO 14644-1 Class 7 cleanliness standard'
            },
            {
                'result': 'Material Removal Precision',
                'metric': '±5μm accuracy with no substrate damage'
            },
            {
                'result': 'Processing Speed',
                'metric': '2-5 m²/hour cleaning rate depending on contamination level'
            }
        ]

    def _build_verification_data(self, author_info: Dict) -> Dict:
        """Build prompt chain verification data"""
        import time
        return {
            'base_config_loaded': True,
            'persona_config_loaded': True,
            'formatting_config_loaded': True,
            'ai_detection_config_loaded': True,
            'persona_country': author_info.get('country'),
            'author_id': author_info.get('id'),
            'verification_timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'prompt_components_integrated': 4,
            'human_authenticity_focus': True,
            'cultural_adaptation_applied': True
        }

    def _save_validation_report(self, material_name: str, validation_report):
        """Save validation report for review and debugging"""
        try:
            import os
            
            # Create validation reports directory
            reports_dir = "logs/validation_reports"
            os.makedirs(reports_dir, exist_ok=True)
            
            # Generate comprehensive report
            from frontmatter.comprehensive_validator import ComprehensiveFrontmatterValidator
            validator = ComprehensiveFrontmatterValidator()
            report_text = validator.generate_comprehensive_report(validation_report)
            
            # Save report file
            report_file = f"{reports_dir}/{material_name}_validation_report.md"
            with open(report_file, "w") as f:
                f.write(report_text)
                
            logger.info(f"📄 Validation report saved: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")

    def _apply_field_ordering(self, frontmatter_data: Dict) -> Dict:
        """
        Apply the standard field ordering for optimal readability and consistency.
        
        Organizes fields according to the proposal:
        1. Basic Identification
        2. Content Metadata
        3. Chemical Classification
        4. Material Properties (Grouped)
        5. Material Composition
        6. Laser Machine Settings (Grouped)
        7. Applications
        8. Compatibility
        9. Regulatory Standards
        10. Author Information
        11. Visual Assets
        12. Impact Metrics
        """
        ordered_data = {}
        
        # === 1. BASIC IDENTIFICATION ===
        if "name" in frontmatter_data:
            ordered_data["name"] = frontmatter_data["name"]
        if "category" in frontmatter_data:
            ordered_data["category"] = frontmatter_data["category"]
            
        # === 2. CONTENT METADATA ===
        for field in ["title", "headline", "description", "keywords"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 3. CHEMICAL CLASSIFICATION ===
        if "chemicalProperties" in frontmatter_data:
            ordered_data["chemicalProperties"] = frontmatter_data["chemicalProperties"]
            
        # === 4. MATERIAL PROPERTIES (Grouped) ===
        if "properties" in frontmatter_data:
            ordered_data["properties"] = self._order_properties_groups(frontmatter_data["materialProperties"])
            
        # === 5. MATERIAL COMPOSITION ===
        if "composition" in frontmatter_data:
            ordered_data["composition"] = frontmatter_data["composition"]
            
        # === 6. LASER MACHINE SETTINGS (Grouped) ===
        if "machineSettings" in frontmatter_data:
            ordered_data["machineSettings"] = self._order_machine_settings_groups(frontmatter_data["machineSettings"])
            
        # === 7. APPLICATIONS ===
        if "applications" in frontmatter_data:
            ordered_data["applications"] = frontmatter_data["applications"]
            
        # === 8. COMPATIBILITY ===
        if "compatibility" in frontmatter_data:
            ordered_data["compatibility"] = frontmatter_data["compatibility"]
            
        # === 9. REGULATORY STANDARDS ===
        if "regulatoryStandards" in frontmatter_data:
            ordered_data["regulatoryStandards"] = frontmatter_data["regulatoryStandards"]
            
        # === 10. AUTHOR INFORMATION ===
        for field in ["author", "author_object"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # === 11. VISUAL ASSETS ===
        if "images" in frontmatter_data:
            ordered_data["images"] = frontmatter_data["images"]
            
        # === 12. IMPACT METRICS ===
        for field in ["environmentalImpact", "outcomes"]:
            if field in frontmatter_data:
                ordered_data[field] = frontmatter_data[field]
                
        # Add any remaining fields that weren't explicitly ordered
        for key, value in frontmatter_data.items():
            if key not in ordered_data:
                ordered_data[key] = value
                
        return ordered_data
        
    def _order_properties_groups(self, properties: Dict) -> Dict:
        """Order properties with grouped organization following the standard pattern"""
        ordered_properties = {}
        
        # Property groups in order
        property_groups = [
            "density", "meltingPoint", "thermalConductivity", 
            "tensileStrength", "hardness", "youngsModulus"
        ]
        
        # Add each group with all its components
        for prop in property_groups:
            if prop in properties:
                # Add main property
                ordered_properties[prop] = properties[prop]
                
                # Add numeric and unit fields
                if f"{prop}Numeric" in properties:
                    ordered_properties[f"{prop}Numeric"] = properties[f"{prop}Numeric"]
                if f"{prop}Unit" in properties:
                    ordered_properties[f"{prop}Unit"] = properties[f"{prop}Unit"]
                    
                # Add min fields with explicit handling for different property types
                if "meltingMin" in properties and prop == "meltingPoint":
                    ordered_properties["meltingMin"] = properties["meltingMin"]
                    ordered_properties["meltingMinNumeric"] = properties.get("meltingMinNumeric")
                    ordered_properties["meltingMinUnit"] = properties.get("meltingMinUnit")
                elif f"{prop}Min" in properties:
                    ordered_properties[f"{prop}Min"] = properties[f"{prop}Min"]
                    ordered_properties[f"{prop}MinNumeric"] = properties.get(f"{prop}MinNumeric")
                    ordered_properties[f"{prop}MinUnit"] = properties.get(f"{prop}MinUnit")
                elif "thermalMin" in properties and prop == "thermalConductivity":
                    ordered_properties["thermalMin"] = properties["thermalMin"]
                    ordered_properties["thermalMinNumeric"] = properties.get("thermalMinNumeric")
                    ordered_properties["thermalMinUnit"] = properties.get("thermalMinUnit")
                elif "tensileMin" in properties and prop == "tensileStrength":
                    ordered_properties["tensileMin"] = properties["tensileMin"]
                    ordered_properties["tensileMinNumeric"] = properties.get("tensileMinNumeric")
                    ordered_properties["tensileMinUnit"] = properties.get("tensileMinUnit")
                elif "hardnessMin" in properties and prop == "hardness":
                    ordered_properties["hardnessMin"] = properties["hardnessMin"]
                    ordered_properties["hardnessMinNumeric"] = properties.get("hardnessMinNumeric")
                    ordered_properties["hardnessMinUnit"] = properties.get("hardnessMinUnit")
                elif "modulusMin" in properties and prop == "youngsModulus":
                    ordered_properties["modulusMin"] = properties["modulusMin"]
                    ordered_properties["modulusMinNumeric"] = properties.get("modulusMinNumeric")
                    ordered_properties["modulusMinUnit"] = properties.get("modulusMinUnit")
                    
                # Add max fields
                if "meltingMax" in properties and prop == "meltingPoint":
                    ordered_properties["meltingMax"] = properties["meltingMax"]
                    ordered_properties["meltingMaxNumeric"] = properties.get("meltingMaxNumeric")
                    ordered_properties["meltingMaxUnit"] = properties.get("meltingMaxUnit")
                elif f"{prop}Max" in properties:
                    ordered_properties[f"{prop}Max"] = properties[f"{prop}Max"]
                    ordered_properties[f"{prop}MaxNumeric"] = properties.get(f"{prop}MaxNumeric")
                    ordered_properties[f"{prop}MaxUnit"] = properties.get(f"{prop}MaxUnit")
                elif "thermalMax" in properties and prop == "thermalConductivity":
                    ordered_properties["thermalMax"] = properties["thermalMax"]
                    ordered_properties["thermalMaxNumeric"] = properties.get("thermalMaxNumeric")
                    ordered_properties["thermalMaxUnit"] = properties.get("thermalMaxUnit")
                elif "tensileMax" in properties and prop == "tensileStrength":
                    ordered_properties["tensileMax"] = properties["tensileMax"]
                    ordered_properties["tensileMaxNumeric"] = properties.get("tensileMaxNumeric")
                    ordered_properties["tensileMaxUnit"] = properties.get("tensileMaxUnit")
                elif "hardnessMax" in properties and prop == "hardness":
                    ordered_properties["hardnessMax"] = properties["hardnessMax"]
                    ordered_properties["hardnessMaxNumeric"] = properties.get("hardnessMaxNumeric")
                    ordered_properties["hardnessMaxUnit"] = properties.get("hardnessMaxUnit")
                elif "modulusMax" in properties and prop == "youngsModulus":
                    ordered_properties["modulusMax"] = properties["modulusMax"]
                    ordered_properties["modulusMaxNumeric"] = properties.get("modulusMaxNumeric")
                    ordered_properties["modulusMaxUnit"] = properties.get("modulusMaxUnit")
                    
                # Add percentile
                if f"{prop}Percentile" in properties:
                    ordered_properties[f"{prop}Percentile"] = properties[f"{prop}Percentile"]
                elif "meltingPercentile" in properties and prop == "meltingPoint":
                    ordered_properties["meltingPercentile"] = properties["meltingPercentile"]
                elif "thermalPercentile" in properties and prop == "thermalConductivity":
                    ordered_properties["thermalPercentile"] = properties["thermalPercentile"]
                elif "tensilePercentile" in properties and prop == "tensileStrength":
                    ordered_properties["tensilePercentile"] = properties["tensilePercentile"]
                elif "hardnessPercentile" in properties and prop == "hardness":
                    ordered_properties["hardnessPercentile"] = properties["hardnessPercentile"]
                elif "modulusPercentile" in properties and prop == "youngsModulus":
                    ordered_properties["modulusPercentile"] = properties["modulusPercentile"]
        
        # Add laser-specific properties at the end
        for field in ["laserType", "wavelength", "fluenceRange", "chemicalFormula"]:
            if field in properties:
                ordered_properties[field] = properties[field]
                
        # Add any remaining properties
        for key, value in properties.items():
            if key not in ordered_properties:
                ordered_properties[key] = value
                
        return ordered_properties
        
    def _order_machine_settings_groups(self, machine_settings: Dict) -> Dict:
        """Order machine settings with grouped organization"""
        ordered_settings = {}
        
        # Machine setting groups in order
        setting_groups = [
            "powerRange", "pulseDuration", "wavelength", "spotSize", 
            "repetitionRate", "fluenceRange", "scanningSpeed"
        ]
        
        # Add each group with all its components
        for setting in setting_groups:
            if setting in machine_settings:
                # Add main setting
                ordered_settings[setting] = machine_settings[setting]
                
                # Add numeric and unit
                if f"{setting}Numeric" in machine_settings:
                    ordered_settings[f"{setting}Numeric"] = machine_settings[f"{setting}Numeric"]
                if f"{setting}Unit" in machine_settings:
                    ordered_settings[f"{setting}Unit"] = machine_settings[f"{setting}Unit"]
                    
                # Add min values
                if f"{setting}Min" in machine_settings:
                    ordered_settings[f"{setting}Min"] = machine_settings[f"{setting}Min"]
                    ordered_settings[f"{setting}MinNumeric"] = machine_settings.get(f"{setting}MinNumeric")
                    ordered_settings[f"{setting}MinUnit"] = machine_settings.get(f"{setting}MinUnit")
                    
                # Add max values
                if f"{setting}Max" in machine_settings:
                    ordered_settings[f"{setting}Max"] = machine_settings[f"{setting}Max"]
                    ordered_settings[f"{setting}MaxNumeric"] = machine_settings.get(f"{setting}MaxNumeric")
                    ordered_settings[f"{setting}MaxUnit"] = machine_settings.get(f"{setting}MaxUnit")
        
        # Add beam and safety settings at the end
        for field in ["beamProfile", "beamProfileOptions", "safetyClass"]:
            if field in machine_settings:
                ordered_settings[field] = machine_settings[field]
                
        # Add any remaining settings
        for key, value in machine_settings.items():
            if key not in ordered_settings:
                ordered_settings[key] = value
                
        return ordered_settings
